from fastapi import Depends,FastAPI, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import os
import shutil
from enum import Enum
from sqlalchemy.orm import Session
from cardamagedetection.components.database import get_db
from cardamagedetection.components.model import Content

app = FastAPI()

# Constants
MAX_FILE_SIZE = 240 * 1024 * 1024  # 240MB in bytes
UPLOAD_DIR = "uploaded_videos"

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Enum for video type
class VideoType(str, Enum):
    BEFORE = "before"
    AFTER = "after"

@app.post("/upload-video/")
async def upload_video(
    video: UploadFile,
    driver_id: str = Form(...),
    video_type: VideoType = Form(...),  # Form(...) means it's required
    db: Session = Depends(get_db)
):
    try:
        # Validate file size
        video_content = await video.read()
        file_size = len(video_content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size is too large. Maximum size allowed is 240MB"
            )
        
        # Validate file type
        if not video.content_type.startswith('video/'):
            raise HTTPException(
                status_code=400,
                detail="File must be a video"
            )
        
        # Create file path with before/after suffix
        file_extension = os.path.splitext(video.filename)[1]
        file_name = f"{video_type.value}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        
        # Remove existing file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Save the new file
        with open(file_path, "wb") as f:
            f.write(video_content)
            
        # Save to database
        new_content = Content(
            video_url=file_path,
            flag=video_type.value,
            raider_id=driver_id
        )
        
        db.add(new_content)
        db.commit()
        db.refresh(new_content)
        
        return JSONResponse(
            content={
                "message": "Video uploaded successfully",
                "driver_id": driver_id,
                "video_type": video_type,
                "file_path": file_path,
                "content_id": new_content.id
            },
            status_code=200
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()  # Rollback database changes if there's an error
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while uploading the video: {str(e)}"
        )

# # Optional: Endpoint to check if a driver's video exists
# @app.get("/check-video/{driver_id}")
# async def check_video(driver_id: str):
#     # Check common video extensions
#     video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
#     for ext in video_extensions:
#         file_path = os.path.join(UPLOAD_DIR, f"{driver_id}{ext}")
#         if os.path.exists(file_path):
#             return {"exists": True, "file_path": file_path}
    
#     return {"exists": False}