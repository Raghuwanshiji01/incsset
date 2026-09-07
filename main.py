import os
import re
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI(
    title="incsset Media Extractor API",
    description="High-speed non-blocking media & caption extraction API powered by yt-dlp",
    version="1.0.0"
)

# Enable CORS for all domains (Hostinger frontend support)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "service": "incsset Media Extractor API",
        "status": "online",
        "health": "/health",
        "extract_endpoint": "/api/extract?url=YOUR_URL"
    }

@app.get("/health")
def health_check():
    """Endpoint for 24/7 uptime pings via UptimeRobot"""
    return {"status": "ok", "uptime": "active"}

@app.get("/api/extract")
def extract_media(url: str = Query(..., description="The media URL to extract")):
    if not url or not url.strip():
        raise HTTPException(status_code=400, detail="Missing URL parameter")

    raw_url = url.strip()

    # yt-dlp extraction options (Fast, download=False, lightweight)
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'no_playlist': True,
        'format': 'best',
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(raw_url, download=False)
            
            if not info:
                raise HTTPException(status_code=404, detail="Could not extract media info")

            # Extract formats
            direct_video_url = info.get('url')
            title = info.get('title') or "Video"
            thumbnail = info.get('thumbnail') or ""
            duration = info.get('duration') or 0
            description = info.get('description') or info.get('caption') or ""
            uploader = info.get('uploader') or info.get('uploader_id') or ""

            # Check requested format streams
            formats_list = []
            if 'formats' in info:
                for f in info['formats']:
                    f_url = f.get('url')
                    if not f_url:
                        continue
                    ext = f.get('ext') or 'mp4'
                    vcodec = f.get('vcodec') or ''
                    acodec = f.get('acodec') or ''
                    resolution = f.get('format_note') or f.get('resolution') or f"{f.get('width', '')}x{f.get('height', '')}"
                    
                    formats_list.append({
                        "url": f_url,
                        "ext": ext,
                        "resolution": resolution,
                        "has_video": vcodec != 'none',
                        "has_audio": acodec != 'none',
                    })

            # Primary direct download link fallback
            if not direct_video_url and formats_list:
                # Pick best combined or video stream
                combined = [f for f in formats_list if f['has_video'] and f['has_audio']]
                if combined:
                    direct_video_url = combined[-1]['url']
                else:
                    direct_video_url = formats_list[-1]['url']

            return {
                "success": True,
                "title": title,
                "thumbnail": thumbnail,
                "duration": duration,
                "uploader": uploader,
                "caption": description,
                "download_url": direct_video_url,
                "formats": formats_list[:8]  # top 8 formats
            }

    except Exception as e:
        err_msg = str(e)
        if "Unsupported URL" in err_msg:
            raise HTTPException(status_code=400, detail="Unsupported platform or invalid link.")
        raise HTTPException(status_code=500, detail=f"Extraction error: {err_msg}")
