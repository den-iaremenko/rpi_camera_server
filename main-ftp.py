from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import uvicorn
from os import path, listdir

app = FastAPI()

UPLOAD_FOLDER = "./uploads"

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_path = path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return {"filename": file.filename}

@app.get("/files/")
async def list_files():
    files = listdir(UPLOAD_FOLDER)
    return {"files": files}

@app.get("/files/{filename}")
async def download_file(filename: str):
    file_path = path.join(UPLOAD_FOLDER, filename)
    if path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)