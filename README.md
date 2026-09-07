# incsset - Media Downloader API

A fast, lightweight Python FastAPI backend powered by `yt-dlp` for extracting Instagram Reels, TikTok (no watermark), YouTube Shorts, and Pinterest media links.

## API Endpoints
- `GET /`: Service status
- `GET /health`: Uptime monitoring endpoint
- `GET /api/extract?url=YOUR_URL`: Extracts direct media download links and captions
