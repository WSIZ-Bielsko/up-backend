import math
import os
from datetime import datetime, timezone
from urllib.parse import quote
from uuid import UUID, uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel



from file_storage import FileMeta, FileStorage


load_dotenv()

app = FastAPI(title="File Storage")
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_methods=["*"],
                   allow_headers=["*"])
store = FileStorage(os.getenv("FILES_DB", "files.db"))

logger.info(f"Using CORS:{origins}")

class MetaUpdate(BaseModel):
    pid: int | None = None
    album: str | None = None
    filename: str | None = None


def get_meta(fid: UUID) -> FileMeta:
    if not (m := store.read(fid)):
        raise HTTPException(404, "File not found")
    return m


@app.post("/files", status_code=201)
async def upload(file: UploadFile, pid: int = Form(), album: str = Form()) -> FileMeta:
    data = await file.read()
    m = FileMeta(fid=uuid4(), pid=pid, album=album, filename=file.filename or "unnamed",
                 size_mb=math.ceil(len(data) / 2**20), created_at=datetime.now(timezone.utc))
    store.create(m)
    store.create_payload(m.fid, data)
    return m


@app.get("/files")
async def list_files() -> list[FileMeta]:
    return store.all()


@app.get("/files/{fid}")
async def read_meta(fid: UUID) -> FileMeta:
    return get_meta(fid)


@app.get("/files/{fid}/download")
async def download(fid: UUID) -> Response:
    m, data = get_meta(fid), store.read_payload(fid)
    if data is None:
        raise HTTPException(404, "Payload not found")
    return Response(data, media_type="application/octet-stream",
                    headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(m.filename)}"})


@app.patch("/files/{fid}")
async def update_meta(fid: UUID, upd: MetaUpdate) -> FileMeta:
    m = get_meta(fid).model_copy(update=upd.model_dump(exclude_none=True))
    store.update(m)
    return m


@app.delete("/files/{fid}", status_code=204)
async def delete(fid: UUID) -> None:
    if not store.delete(fid):
        raise HTTPException(404, "File not found")


if __name__ == "__main__":
    import uvicorn
    port = os.getenv("PORT", 8001)
    uvicorn.run(app, host="127.0.0.1", port=int(port))