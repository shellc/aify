import os
import glob
import json
from typing import List, Dict
from ._env import apps_dir

def _memories_dirs():
    memories_dir = os.path.join(apps_dir(), 'memories')
    if not os.path.exists(memories_dir):
        os.mkdir(memories_dir)

    return memories_dir

def save(program_name:str, session_id: str, role: str, content: str) -> None:
    """Save memory for the specified session of the application."""

    prog_session_dir = os.path.join(_memories_dirs(), program_name)
    if not os.path.exists(prog_session_dir):
        os.mkdir(prog_session_dir)

    with open(os.path.join(prog_session_dir, session_id), 'a') as f:
        f.write(json.dumps({
            'role': role,
            'content': content
        }))
        f.write('\n')

def read(program_name: str, session_id: str, n = 10, max_len = 4096) -> List[Dict]:
    """Read memories from the specified session of the application."""
    fname = os.path.join(_memories_dirs(), program_name, session_id)
    if not os.path.exists(fname):
        return []
    
    fsize = os.path.getsize(fname)

    pos = fsize - max_len if fsize > max_len else 0
    lines = []
    with open(fname) as f:
        f.seek(pos)
        lines = f.readlines()
    lines = lines[n * -1:]

    memories = []
    for line in lines:
        try:
            m = json.loads(line.strip())
            memories.append(m)
        except Exception as e:
            pass
    return memories

def sessions(program_name: str) -> List[Dict]:
    """Get the session list of the specified application."""
    res = []
    for f in glob.glob(os.path.join(_memories_dirs(), program_name, "*")):
        mtime = os.path.getmtime(f)
        p = os.path.abspath(f).split('/')
        session_id = p[-1]

        latest = []
        memories = read(program_name=program_name, session_id=session_id, n=1)
        if memories and len(memories) > 0:
            latest = memories[-1:]

        res.append({
            'name': program_name,
            'session_id': session_id,
            'last_modified': mtime,
            'latest': latest
        })
    return res
