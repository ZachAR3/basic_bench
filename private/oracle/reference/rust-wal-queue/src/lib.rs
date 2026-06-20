use std::collections::{HashMap, HashSet, VecDeque};
use std::fs::{self, File, OpenOptions};
use std::io::{self, Read, Write};
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex, MutexGuard};
use std::time::{SystemTime, UNIX_EPOCH};

pub trait Clock: Send + Sync {
    fn now_millis(&self) -> u64;
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Lease {
    pub id: String,
    pub payload: Vec<u8>,
    pub token: u64,
}

#[derive(Clone)]
enum Status {
    Pending,
    Leased { token: u64, expires: u64, worker: String },
}
#[derive(Clone)]
struct Task { payload: Vec<u8>, status: Status }
struct State {
    tasks: HashMap<String, Task>,
    order: VecDeque<String>,
    done: HashSet<String>,
    next_token: u64,
}

pub struct WalQueue {
    path: PathBuf,
    clock: Arc<dyn Clock>,
    state: Mutex<State>,
}

impl WalQueue {
    pub fn open(path: impl AsRef<Path>, clock: Arc<dyn Clock>) -> io::Result<Self> {
        let path = path.as_ref().to_path_buf();
        let mut state = State {
            tasks: HashMap::new(), order: VecDeque::new(),
            done: HashSet::new(), next_token: 1,
        };
        if path.exists() {
            let mut bytes = Vec::new();
            File::open(&path)?.read_to_end(&mut bytes)?;
            replay(&bytes, &mut state)?;
        }
        Ok(Self { path, clock, state: Mutex::new(state) })
    }

    pub fn enqueue(&self, id: &str, payload: &[u8]) -> io::Result<bool> {
        if id.is_empty() { return Err(io::Error::new(io::ErrorKind::InvalidInput, "empty id")); }
        let mut state = self.lock()?;
        if state.tasks.contains_key(id) || state.done.contains(id) { return Ok(false); }
        self.append(&event_enqueue(id, payload))?;
        state.tasks.insert(id.to_string(), Task { payload: payload.to_vec(), status: Status::Pending });
        state.order.push_back(id.to_string());
        Ok(true)
    }

    pub fn claim(&self, worker: &str, lease_ms: u64) -> io::Result<Option<Lease>> {
        if worker.is_empty() || lease_ms == 0 {
            return Err(io::Error::new(io::ErrorKind::InvalidInput, "invalid lease"));
        }
        let mut state = self.lock()?;
        let now = self.clock.now_millis();
        let id = state.order.iter().find(|id| {
            match state.tasks.get(*id).map(|task| &task.status) {
                Some(Status::Pending) => true,
                Some(Status::Leased { expires, .. }) => *expires <= now,
                None => false,
            }
        }).cloned();
        let Some(id) = id else { return Ok(None) };
        let token = state.next_token;
        let expires = now.checked_add(lease_ms)
            .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, "lease overflow"))?;
        self.append(&event_claim(&id, token, expires, worker))?;
        state.next_token += 1;
        let task = state.tasks.get_mut(&id).unwrap();
        task.status = Status::Leased { token, expires, worker: worker.to_string() };
        Ok(Some(Lease { id, payload: task.payload.clone(), token }))
    }

    pub fn ack(&self, token: u64) -> io::Result<bool> {
        let mut state = self.lock()?;
        let id = state.tasks.iter().find_map(|(id, task)| match task.status {
            Status::Leased { token: current, .. } if current == token => Some(id.clone()),
            _ => None,
        });
        let Some(id) = id else { return Ok(false) };
        self.append(&event_ack(&id, token))?;
        state.tasks.remove(&id);
        state.order.retain(|candidate| candidate != &id);
        state.done.insert(id);
        Ok(true)
    }

    pub fn compact(&self) -> io::Result<()> {
        let state = self.lock()?;
        let suffix = SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default().as_nanos();
        let temporary = self.path.with_extension(format!("tmp-{}-{suffix}", std::process::id()));
        let result = (|| {
            let mut file = OpenOptions::new().create_new(true).write(true).open(&temporary)?;
            for id in &state.order {
                let task = state.tasks.get(id).unwrap();
                write_frame(&mut file, &event_enqueue(id, &task.payload))?;
                if let Status::Leased { token, expires, ref worker } = task.status {
                    write_frame(&mut file, &event_claim(id, token, expires, worker))?;
                }
            }
            for id in &state.done { write_frame(&mut file, &event_done(id))?; }
            file.sync_all()?;
            fs::rename(&temporary, &self.path)
        })();
        if result.is_err() { let _ = fs::remove_file(&temporary); }
        result
    }

    fn lock(&self) -> io::Result<MutexGuard<'_, State>> {
        self.state.lock().map_err(|_| io::Error::other("queue lock poisoned"))
    }
    fn append(&self, event: &[u8]) -> io::Result<()> {
        let mut file = OpenOptions::new().create(true).append(true).open(&self.path)?;
        write_frame(&mut file, event)?;
        file.sync_data()
    }
}

fn write_frame(file: &mut File, event: &[u8]) -> io::Result<()> {
    file.write_all(&(event.len() as u32).to_le_bytes())?;
    file.write_all(&crc32(event).to_le_bytes())?;
    file.write_all(event)
}
fn replay(bytes: &[u8], state: &mut State) -> io::Result<()> {
    let mut offset = 0;
    while offset < bytes.len() {
        if bytes.len() - offset < 8 { break; }
        let length = u32::from_le_bytes(bytes[offset..offset + 4].try_into().unwrap()) as usize;
        let checksum = u32::from_le_bytes(bytes[offset + 4..offset + 8].try_into().unwrap());
        if bytes.len() - offset - 8 < length { break; }
        let event = &bytes[offset + 8..offset + 8 + length];
        if crc32(event) != checksum {
            return Err(io::Error::new(io::ErrorKind::InvalidData, "WAL checksum mismatch"));
        }
        apply_event(event, state)?;
        offset += 8 + length;
    }
    Ok(())
}
fn apply_event(event: &[u8], state: &mut State) -> io::Result<()> {
    let mut cursor = Cursor { bytes: event, offset: 1 };
    match event.first().copied() {
        Some(1) => {
            let id = cursor.string()?;
            let payload = cursor.bytes()?;
            if !state.tasks.contains_key(&id) && !state.done.contains(&id) {
                state.order.push_back(id.clone());
                state.tasks.insert(id, Task { payload, status: Status::Pending });
            }
        }
        Some(2) => {
            let id = cursor.string()?;
            let token = cursor.u64()?;
            let expires = cursor.u64()?;
            let worker = cursor.string()?;
            if let Some(task) = state.tasks.get_mut(&id) {
                task.status = Status::Leased { token, expires, worker };
                state.next_token = state.next_token.max(token + 1);
            }
        }
        Some(3) => {
            let id = cursor.string()?;
            let token = cursor.u64()?;
            if matches!(state.tasks.get(&id).map(|task| &task.status), Some(Status::Leased { token: current, .. }) if *current == token) {
                state.tasks.remove(&id); state.order.retain(|value| value != &id); state.done.insert(id);
            }
        }
        Some(4) => { state.done.insert(cursor.string()?); }
        _ => return Err(io::Error::new(io::ErrorKind::InvalidData, "unknown WAL event")),
    }
    if cursor.offset != event.len() { return Err(io::Error::new(io::ErrorKind::InvalidData, "trailing event bytes")); }
    Ok(())
}

struct Cursor<'a> { bytes: &'a [u8], offset: usize }
impl Cursor<'_> {
    fn take(&mut self, count: usize) -> io::Result<&[u8]> {
        if self.bytes.len() - self.offset < count { return Err(io::Error::new(io::ErrorKind::InvalidData, "short event")); }
        let value = &self.bytes[self.offset..self.offset + count]; self.offset += count; Ok(value)
    }
    fn u16(&mut self) -> io::Result<u16> { Ok(u16::from_le_bytes(self.take(2)?.try_into().unwrap())) }
    fn u32(&mut self) -> io::Result<u32> { Ok(u32::from_le_bytes(self.take(4)?.try_into().unwrap())) }
    fn u64(&mut self) -> io::Result<u64> { Ok(u64::from_le_bytes(self.take(8)?.try_into().unwrap())) }
    fn string(&mut self) -> io::Result<String> {
        let length = self.u16()? as usize;
        String::from_utf8(self.take(length)?.to_vec()).map_err(|_| io::Error::new(io::ErrorKind::InvalidData, "invalid UTF-8"))
    }
    fn bytes(&mut self) -> io::Result<Vec<u8>> {
        let length = self.u32()? as usize;
        Ok(self.take(length)?.to_vec())
    }
}
fn push_string(out: &mut Vec<u8>, value: &str) { out.extend_from_slice(&(value.len() as u16).to_le_bytes()); out.extend_from_slice(value.as_bytes()); }
fn push_bytes(out: &mut Vec<u8>, value: &[u8]) { out.extend_from_slice(&(value.len() as u32).to_le_bytes()); out.extend_from_slice(value); }
fn event_enqueue(id: &str, payload: &[u8]) -> Vec<u8> { let mut out = vec![1]; push_string(&mut out, id); push_bytes(&mut out, payload); out }
fn event_claim(id: &str, token: u64, expires: u64, worker: &str) -> Vec<u8> { let mut out = vec![2]; push_string(&mut out, id); out.extend_from_slice(&token.to_le_bytes()); out.extend_from_slice(&expires.to_le_bytes()); push_string(&mut out, worker); out }
fn event_ack(id: &str, token: u64) -> Vec<u8> { let mut out = vec![3]; push_string(&mut out, id); out.extend_from_slice(&token.to_le_bytes()); out }
fn event_done(id: &str) -> Vec<u8> { let mut out = vec![4]; push_string(&mut out, id); out }
fn crc32(bytes: &[u8]) -> u32 {
    let mut crc = !0u32;
    for byte in bytes {
        crc ^= *byte as u32;
        for _ in 0..8 { crc = if crc & 1 != 0 { (crc >> 1) ^ 0xedb88320 } else { crc >> 1 }; }
    }
    !crc
}
