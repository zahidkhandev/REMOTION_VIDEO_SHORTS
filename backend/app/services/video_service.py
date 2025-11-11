import subprocess
import os
from pathlib import Path
from fastapi import HTTPException
from ..config import get_settings

settings = get_settings()


class VideoService:
    def __init__(self):
        self.videos_dir = settings.storage_path / "videos"
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        self.props_dir = settings.storage_path / "props"
    
    async def render_video(self, script_id: str) -> str:
        """
        Render video using Remotion CLI.
        Returns the URL to the rendered video.
        """
        # Check if props file exists
        props_path = self.props_dir / f"{script_id}.json"
        if not props_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Script props not found for '{script_id}'. Process the paper first."
            )
        
        # Define output path
        video_filename = f"{script_id}.mp4"
        output_path = self.videos_dir / video_filename
        
        # Build Remotion render command
        command = [
            "npx",
            "remotion",
            "render",
            "src/Root.tsx",
            "PaperVideo",
            str(output_path.absolute()),
            f"--props={str(props_path.absolute())}",
            "--overwrite"
        ]
        
        try:
            # Run Remotion from its project directory
            result = subprocess.run(
                command,
                cwd=str(settings.remotion_project_path.absolute()),
                capture_output=True,
                text=True,
                check=True
            )
            
            print(f"Remotion output: {result.stdout}")
            
            if not output_path.exists():
                raise Exception("Video file was not created")
            
            # Return URL
            return f"http://localhost:{settings.backend_port}/videos/{video_filename}"
            
        except subprocess.CalledProcessError as e:
            print(f"Remotion rendering failed:")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            raise HTTPException(
                status_code=500,
                detail=f"Video rendering failed: {e.stderr}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error during rendering: {str(e)}"
            )


# Singleton instance
video_service = VideoService()
