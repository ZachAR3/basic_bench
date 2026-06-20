use std::collections::{HashMap, HashSet, VecDeque};
use std::fs::OpenOptions;
use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};

pub trait Clock: Send + Sync { fn now_millis(&self) -> u64; }
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Lease { pub id: String, pub payload: Vec<u8>, pub token: u64 }
struct State {
    pending: VecDeque<(String, Vec<u8>)>,
    leased: HashMap<String, (Vec<u8>, u64, u64)>,
    known: HashSet<String>,
    next_token: u64,
}
pub struct WalQueue { path: PathBuf, clock: Arc<dyn Clock>, state: Mutex<State> }
impl WalQueue {
    pub fn open(path: impl AsRef<Path>, clock: Arc<dyn Clock>) -> io::Result<Self> {
        Ok(Self { path: path.as_ref().to_path_buf(), clock, state: Mutex::new(State {
            pending: VecDeque::new(), leased: HashMap::new(), known: HashSet::new(), next_token: 1,
        })})
    }
    pub fn enqueue(&self, id: &str, payload: &[u8]) -> io::Result<bool> {
        if id.is_empty() { return Err(io::Error::new(io::ErrorKind::InvalidInput, "empty id")); }
        let mut state = self.state.lock().map_err(|_| io::Error::other("poisoned"))?;
        if !state.known.insert(id.to_string()) { return Ok(false); }
        state.pending.push_back((id.to_string(), payload.to_vec()));
        let mut file = OpenOptions::new().create(true).append(true).open(&self.path)?;
        writeln!(file, "enqueue:{id}")?;
        Ok(true)
    }
    pub fn claim(&self, _worker: &str, lease_ms: u64) -> io::Result<Option<Lease>> {
        if lease_ms == 0 { return Err(io::Error::new(io::ErrorKind::InvalidInput, "zero lease")); }
        let mut state = self.state.lock().map_err(|_| io::Error::other("poisoned"))?;
        let expired = state.leased.iter().find(|(_, value)| value.2 <= self.clock.now_millis()).map(|(id, _)| id.clone());
        let (id, payload) = if let Some(id) = expired {
            let value = state.leased.remove(&id).unwrap(); (id, value.0)
        } else if let Some(value) = state.pending.pop_front() { value } else { return Ok(None) };
        let token = state.next_token; state.next_token += 1;
        state.leased.insert(id.clone(), (payload.clone(), token, self.clock.now_millis() + lease_ms));
        Ok(Some(Lease { id, payload, token }))
    }
    pub fn ack(&self, token: u64) -> io::Result<bool> {
        let mut state = self.state.lock().map_err(|_| io::Error::other("poisoned"))?;
        let id = state.leased.iter().find(|(_, value)| value.1 == token).map(|(id, _)| id.clone());
        Ok(id.and_then(|id| state.leased.remove(&id)).is_some())
    }
    pub fn compact(&self) -> io::Result<()> { Ok(()) }
}
