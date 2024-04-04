from fastapi import FastAPI, File, UploadFile, HTTPException, Response
from starlette.responses import StreamingResponse
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from os import path
import uvicorn
import cv2
import io

UPLOAD_FOLDER = "./uploads"
cap = None

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def video_generator():
    if cap != None:
        cap.release()
    cap = cv2.VideoCapture(0)  # Use 0 for the default camera
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Convert frame to JPEG
            _, buffer = cv2.imencode('.jpg', frame)

            # Yield the frame as bytes
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n'
    finally:
        cap.release()


def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/photo")
async def photo():
    camera_index = 0
    cam = cv2.VideoCapture(camera_index)
    while True:
        _, image = cam.read()
        break
    cv2.imwrite('./uploads/img.jpg', image)
    cam.release()
    if path.exists('./uploads/img.jpg'):
        return FileResponse('./uploads/img.jpg')
    else:
        raise HTTPException(status_code=404, detail="File not found")



@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
