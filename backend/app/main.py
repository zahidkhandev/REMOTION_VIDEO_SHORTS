from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import get_settings
from .routers import paper, video

settings = get_settings()

app = FastAPI(
    title="Paper-to-Video Automator",
    description="Automated research paper to short-form video pipeline",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(paper.router)
app.include_router(video.router)

# Static files
app.mount("/videos", StaticFiles(directory=str(settings.storage_path / "videos")), name="videos")
app.mount("/audio", StaticFiles(directory=str(settings.storage_path / "audio")), name="audio")


@app.get("/")
async def root():
    return {
        "message": "Paper-to-Video Automator API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )
