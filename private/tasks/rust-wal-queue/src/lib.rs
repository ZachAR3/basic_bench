use std::collections::{HashMap, VecDeque};
use std::fs::OpenOptions;
use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};

pub trait Clock: Send + Sync {
    fn now_millis(&self) -> u64;
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Lease {
    pub id: String,
    pub payload: Vec<u8>,
    pub token: u64,
}

struct State {
    pending: VecDeque<(String, Vec<u8>)>,
    leased: HashMap<String, (Vec<u8>, u64, u64)>,
    next_token: u64,
}

pub struct WalQueue {
    path: PathBuf,
    clock: Arc<dyn Clock>,
    state: Mutex<State>,
}

impl WalQueue {
    pub fn open(path: impl AsRef<Path>, clock: Arc<dyn Clock>) -> io::Result<Self> {
        Ok(Self {
            path: path.as_ref().to_path_buf(),
            clock,
            state: Mutex::new(State {
                pending: VecDeque::new(),
                leased: HashMap::new(),
                next_token: 1,
            }),
        })
    }

    pub fn enqueue(&self, id: &str, payload: &[u8]) -> io::Result<bool> {
        let mut state = self.state.lock().unwrap();
        state.pending.push_back((id.to_string(), payload.to_vec()));
        let mut file = OpenOptions::new().create(true).append(true).open(&self.path)?;
        writeln!(file, "enqueue:{id}")?;
        Ok(true)
    }

    pub fn claim(&self, worker: &str, lease_ms: u64) -> io::Result<Option<Lease>> {
        let mut state = self.state.lock().unwrap();
        let Some((id, payload)) = state.pending.pop_front() else { return Ok(None) };
        let token = state.next_token;
        state.next_token += 1;
        let expires = self.clock.now_millis() + lease_ms;
        state.leased.insert(id.clone(), (payload.clone(), token, expires));
        let _ = worker;
        Ok(Some(Lease { id, payload, token }))
    }

    pub fn ack(&self, token: u64) -> io::Result<bool> {
        let mut state = self.state.lock().unwrap();
        let id = state.leased.iter().find(|(_, value)| value.1 == token).map(|(id, _)| id.clone());
        Ok(id.and_then(|id| state.leased.remove(&id)).is_some())
    }

    pub fn compact(&self) -> io::Result<()> {
        Ok(())
    }
}
