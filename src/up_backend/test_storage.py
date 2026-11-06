import sqlite3
from datetime import datetime
from uuid import uuid4

import pytest

from up_backend.file_storage import FileMeta, FileStorage


@pytest.fixture
def store():
    return FileStorage(":memory:")


@pytest.fixture
def meta():
    return FileMeta(fid=uuid4(), pid=1, album="holiday", filename="beach.jpg", size_mb=3, created_at=datetime(2026, 10, 30, 12, 0))


def test_create_and_read(store, meta):
    store.create(meta)
    assert store.read(meta.fid) == meta
    assert store.all() == [meta]


def test_update(store, meta):
    store.create(meta)
    updated = meta.model_copy(update={"album": "summer", "size_mb": 9})
    assert store.update(updated)
    assert store.read(meta.fid) == updated


def test_missing_record(store, meta):
    assert store.read(meta.fid) is None
    assert not store.update(meta)
    assert not store.delete(meta.fid)


def test_payload_roundtrip(store, meta):
    data = bytes(range(256))
    store.create(meta)
    store.create_payload(meta.fid, data)
    assert store.read_payload(meta.fid) == data
    assert store.delete_payload(meta.fid)
    assert store.read_payload(meta.fid) is None


def test_delete_removes_payload_and_rejects_duplicates(store, meta):
    store.create(meta)
    store.create_payload(meta.fid, b"abc")
    with pytest.raises(sqlite3.IntegrityError):
        store.create(meta)
    assert store.delete(meta.fid)
    assert store.read(meta.fid) is None and store.read_payload(meta.fid) is None