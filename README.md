# up-backend

A simple FastAPI-based file storage service with SQLite backend.

## Features

- **File Upload**: Upload files with metadata (Project ID, Album name).
- **File Metadata**: Store and retrieve file information (filename, size, creation date).
- **File Download**: Download stored files.
- **CRUD Operations**: List, read, update, and delete file metadata and payloads.
- **Persistence**: Uses SQLite for both metadata and binary storage (BLOB).

## Tech Stack

- **Python**: >= 3.14
- **FastAPI**: API framework.
- **Pydantic**: Data validation and settings.
- **SQLite**: Database for storage.
- **uv**: Project management and dependency handling.

## Getting Started

### Prerequisites

- [uv](https://github.com/astral-sh/uv) installed.

### Installation

1. Clone the repository.
2. Sync dependencies:
   ```bash
   uv sync
   ```

### Running the Application

Start the server using `uv`:

```bash
uv run uvicorn up_backend.storage_api:app --host 127.0.0.1 --port 8001 --reload
```

Or run the script directly:

```bash
uv run src/up_backend/storage_api.py
```

The API will be available at `http://127.0.0.1:8001`.
You can access the interactive API documentation at `http://127.0.0.1:8001/docs`.

## Environment Variables

- `CORS_ORIGINS`: Comma-separated list of allowed origins (default: `http://localhost:4000`).
- `FILES_DB`: Path to the SQLite database file (default: `files.db`).

## API Endpoints

- `POST /files`: Upload a new file.
- `GET /files`: List all files metadata.
- `GET /files/{fid}`: Get metadata for a specific file.
- `GET /files/{fid}/download`: Download file content.
- `PATCH /files/{fid}`: Update file metadata.
- `DELETE /files/{fid}`: Delete a file and its payload.

## Development

Run tests with `pytest`:

```bash
uv run pytest
```
