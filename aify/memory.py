import os
import glob
import json
from ._env import get_apps_dir

def _memories_dirs():
    apps_dir = get_apps_dir()
    memories_dir = os.path.join(apps_dir, 'memories')
    if not os.path.exists(memories_dir):
        os.mkdir(memories_dir)

    return memories_dir

def save(program_name:str, session_id: str, role: str, content: str):

    prog_session_dir = os.path.join(_memories_dirs(), program_name)
    if not os.path.exists(prog_session_dir):
        os.mkdir(prog_session_dir)

    with open(os.path.join(prog_session_dir, session_id), 'a') as f:
        f.write(json.dumps({
            'role': role,
            'content': content
        }))
        f.write('\n')

def read(program_name: str, session_id: str, n = 10, max_len = 4096):
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

def sessions():
    res = []
    for f in sorted(glob.glob(os.path.join(_memories_dirs(), "*/*")), key=os.path.getmtime, reverse=True):
        p = os.path.abspath(f).split('/')
        program_name = p[-2]
        session_id = p[-1]

        last_message = None
        memories = read(program_name=program_name, session_id=session_id, n=1)
        if memories and len(memories) > 0:
            last_message = memories[-1]['content']

        res.append({
            'name': program_name,
            'session_id': session_id,
            'content': last_message
        })
    return res
