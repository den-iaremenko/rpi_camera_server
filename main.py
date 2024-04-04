from fastapi import FastAPI
from starlette.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import cv2
import io

app = FastAPI()

origins = [
    "*:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def video_generator():
    cap = cv2.VideoCapture(1)  # Use 0 for the default camera

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to JPEG
        _, buffer = cv2.imencode('.jpg', frame)

        # Yield the frame as bytes
        yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n'

    cap.release()

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(video_generator(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
