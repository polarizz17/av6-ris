import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN", "").strip()
ARCHIVE_DIR = Path(os.getenv("ARCHIVE_DIR", "./archive")).resolve()
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(1 * 1024 * 1024 * 1024)))
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="RIS Upload Server", version="1.0.0")

class UploadResult(BaseModel):
    filename: str
    stored_as: str
    size_bytes: int

def verify_auth(authorization: Optional[str] = Header(None)) -> None:
    if API_TOKEN:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Bearer token")
        token = authorization.removeprefix("Bearer ").strip()
        if token != API_TOKEN:
            raise HTTPException(status_code=403, detail="Invalid token")

@app.post("/upload", response_model=UploadResult)
async def upload_zip(file: UploadFile = File(...), _: None = Depends(verify_auth)):
    filename = file.filename or "upload.zip"
    ext = Path(filename).suffix.lower()
    if ext not in {".zip"}:
        raise HTTPException(status_code=400, detail="Only .zip files are accepted")

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    stored_name = f"{ts}__{Path(filename).name}"
    dest_path = ARCHIVE_DIR / stored_name

    size = 0
    try:
        with dest_path.open("wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    out.close()
                    dest_path.unlink(missing_ok=True)
                    raise HTTPException(status_code=413, detail="Upload too large")
                out.write(chunk)
    finally:
        await file.close()

    return UploadResult(filename=filename, stored_as=str(dest_path), size_bytes=size)

@app.get("/health")
def health():
    return {"status": "ok", "archive_dir": str(ARCHIVE_DIR)}
