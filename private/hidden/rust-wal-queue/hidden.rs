use std::fs::{self, OpenOptions};
use std::io::Write;
use std::path::PathBuf;
use std::sync::{Arc, atomic::{AtomicU64, Ordering}};
use wal_queue::{Clock, WalQueue};

struct ManualClock(AtomicU64);
impl ManualClock {
    fn new(value: u64) -> Self { Self(AtomicU64::new(value)) }
    fn set(&self, value: u64) { self.0.store(value, Ordering::SeqCst); }
}
impl Clock for ManualClock { fn now_millis(&self) -> u64 { self.0.load(Ordering::SeqCst) } }

fn path(name: &str) -> PathBuf {
    let root = std::env::temp_dir().join(format!(
        "basic-bench-wal-{}-{}-{}", std::process::id(), name,
        std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos()
    ));
    fs::create_dir_all(&root).unwrap();
    root.join("queue.wal")
}

#[test]
fn replay() {
    let path = path("replay");
    let clock = Arc::new(ManualClock::new(10));
    {
        let queue = WalQueue::open(&path, clock.clone()).unwrap();
        assert!(queue.enqueue("a", b"payload").unwrap());
    }
    let queue = WalQueue::open(&path, clock).unwrap();
    let lease = queue.claim("worker", 100).unwrap().unwrap();
    assert_eq!(lease.id, "a");
    assert_eq!(lease.payload, b"payload");
}

#[test]
fn truncated_and_corrupt() {
    let path = path("corrupt");
    let clock = Arc::new(ManualClock::new(0));
    let queue = WalQueue::open(&path, clock.clone()).unwrap();
    queue.enqueue("a", b"payload").unwrap();
    let clean = fs::read(&path).unwrap();
    OpenOptions::new().append(true).open(&path).unwrap().write_all(&[9, 8, 7]).unwrap();
    assert!(WalQueue::open(&path, clock.clone()).is_ok());
    let mut corrupt = clean;
    let last = corrupt.len() - 1;
    corrupt[last] ^= 0xff;
    fs::write(&path, corrupt).unwrap();
    let error = match WalQueue::open(&path, clock) {
        Ok(_) => panic!("corrupt WAL was accepted"),
        Err(error) => error,
    };
    assert_eq!(error.kind(), std::io::ErrorKind::InvalidData);
}

#[test]
fn idempotent_across_ack() {
    let path = path("idempotent");
    let clock = Arc::new(ManualClock::new(0));
    {
        let queue = WalQueue::open(&path, clock.clone()).unwrap();
        assert!(queue.enqueue("a", b"one").unwrap());
        assert!(!queue.enqueue("a", b"two").unwrap());
        let lease = queue.claim("w", 10).unwrap().unwrap();
        assert!(queue.ack(lease.token).unwrap());
    }
    let queue = WalQueue::open(&path, clock).unwrap();
    assert!(!queue.enqueue("a", b"again").unwrap());
}

#[test]
fn lease_tokens_and_concurrency() {
    let path = path("lease");
    let clock = Arc::new(ManualClock::new(0));
    let queue = Arc::new(WalQueue::open(&path, clock.clone()).unwrap());
    queue.enqueue("a", b"x").unwrap();
    let first = queue.claim("one", 10).unwrap().unwrap();
    let mut threads = vec![];
    for _ in 0..8 {
        let queue = queue.clone();
        threads.push(std::thread::spawn(move || queue.claim("other", 10).unwrap()));
    }
    assert_eq!(
        threads.into_iter()
            .map(|thread| thread.join().unwrap())
            .filter(Option::is_some)
            .count(),
        0
    );
    clock.set(10);
    let second = queue.claim("two", 10).unwrap().unwrap();
    assert_ne!(first.token, second.token);
    assert!(!queue.ack(first.token).unwrap());
    assert!(queue.ack(second.token).unwrap());
}

#[test]
fn compaction_preserves_all_states() {
    let path = path("compact");
    let clock = Arc::new(ManualClock::new(0));
    {
        let queue = WalQueue::open(&path, clock.clone()).unwrap();
        queue.enqueue("done", b"d").unwrap();
        let done = queue.claim("w", 10).unwrap().unwrap();
        queue.ack(done.token).unwrap();
        queue.enqueue("leased", b"l").unwrap();
        queue.claim("w", 100).unwrap();
        queue.enqueue("pending", b"p").unwrap();
        queue.compact().unwrap();
    }
    assert_eq!(fs::read_dir(path.parent().unwrap()).unwrap().count(), 1);
    let queue = WalQueue::open(&path, clock.clone()).unwrap();
    assert!(!queue.enqueue("done", b"x").unwrap());
    let pending = queue.claim("w2", 10).unwrap().unwrap();
    assert_eq!(pending.id, "pending");
    clock.set(100);
    let leased = queue.claim("w3", 10).unwrap().unwrap();
    assert_eq!(leased.id, "leased");
}
