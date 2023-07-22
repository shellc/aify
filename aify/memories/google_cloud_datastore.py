import time
from typing import List, Dict
import uuid as _uuid
from google.cloud import datastore

namespace = _uuid.uuid1()


def uuid():
    return _uuid.uuid5(namespace, _uuid.uuid1().hex).hex


datastore_client = datastore.Client()


def save(program_name: str, session_id: str, role: str, content: str) -> None:
    """Save memory for the specified session of the application."""

    m = {
        'role': role,
        'content': content,
        'created': time.time()
    }

    entity = datastore.Entity(
        key=datastore_client.key('memories', f'{program_name}_{session_id}', 'session_memories', uuid()),
        exclude_from_indexes=("content",)
        )
    entity.update(m)
    datastore_client.put(entity)

    session_key = datastore_client.key(
        'sessions', program_name, 'session_id', session_id
        )
    session_entity = datastore.Entity(
        key=session_key,
        exclude_from_indexes=("content",)
        )
    session_entity.update(m)
    session_entity.update({
        'program_name': program_name,
        'session_id': session_id
    })

    datastore_client.put(session_entity)


def read(program_name: str, session_id: str, n=10, max_len=4096) -> List[Dict]:
    query = datastore_client.query(
        kind='session_memories', ancestor=datastore_client.key('memories', f'{program_name}_{session_id}'))
    query.order = ["created"]

    memories = [x for x in query.fetch(limit=n)]

    return memories


def sessions(program_name: str) -> List[Dict]:
    res = []

    key = datastore_client.key('sessions', program_name)
    query = datastore_client.query(kind='session_id', ancestor=key)
    # query.order = ["-created"]

    sessions = query.fetch()

    for s in sessions:
        res.append({
            'name': s['program_name'],
            'session_id': s['session_id'],
            'last_modified': s['created'],
            'latest': [dict(s)]
        })
    return res
