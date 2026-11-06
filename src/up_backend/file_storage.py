import sqlite3
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FileMeta(BaseModel):
    fid: UUID
    pid: int
    album: str
    filename: str
    size_mb: int
    created_at: datetime


class FileStorage:
    COLS = list(FileMeta.model_fields)

    def __init__(self, path: str = "files.db"):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        with self.db:
            self.db.execute(f"CREATE TABLE IF NOT EXISTS files ({', '.join(self.COLS)}, PRIMARY KEY (fid))")
            self.db.execute("CREATE TABLE IF NOT EXISTS payloads (fid PRIMARY KEY, payload BLOB)")

    def _exec(self, sql: str, params) -> sqlite3.Cursor:
        with self.db:
            return self.db.execute(sql, params)

    def create(self, m: FileMeta) -> None:
        self._exec(f"INSERT INTO files VALUES ({', '.join(':' + c for c in self.COLS)})", m.model_dump(mode="json"))

    def read(self, fid: UUID) -> FileMeta | None:
        row = self._exec("SELECT * FROM files WHERE fid = ?", (str(fid),)).fetchone()
        return FileMeta(**row) if row else None

    def all(self) -> list[FileMeta]:
        return [FileMeta(**r) for r in self._exec("SELECT * FROM files", ())]

    def update(self, m: FileMeta) -> bool:
        sets = ", ".join(f"{c} = :{c}" for c in self.COLS if c != "fid")
        return self._exec(f"UPDATE files SET {sets} WHERE fid = :fid", m.model_dump(mode="json")).rowcount > 0

    def delete(self, fid: UUID) -> bool:
        self.delete_payload(fid)
        return self._exec("DELETE FROM files WHERE fid = ?", (str(fid),)).rowcount > 0

    # payloads

    def create_payload(self, fid: UUID, payload: bytes) -> None:
        self._exec("INSERT INTO payloads VALUES (?, ?)", (str(fid), payload))

    def read_payload(self, fid: UUID) -> bytes | None:
        row = self._exec("SELECT payload FROM payloads WHERE fid = ?", (str(fid),)).fetchone()
        return row[0] if row else None

    def delete_payload(self, fid: UUID) -> bool:
        return self._exec("DELETE FROM payloads WHERE fid = ?", (str(fid),)).rowcount > 0



if __name__ == '__main__':
    m1 = FileMeta(fid=UUID('00000000-0000-0000-0000-000000000000'), pid=1, album='test', filename='test.txt', size_mb=1, created_at=datetime.now())
    m2 = FileMeta(fid=UUID('00000000-0000-0000-0000-000000000001'), pid=2, album='test', filename='test2.txt', size_mb=2, created_at=datetime.now())

    fs = FileStorage()
    fs.create(m1)
    fs.create(m2)
    print(fs.all())
    print(fs.read(m1.fid))
    print(fs.read(m2.fid))
    print(fs.delete(m1.fid))
    print(fs.all())
