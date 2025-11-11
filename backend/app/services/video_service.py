import asyncio  # <-- Import asyncio
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
        Render video using Remotion CLI asynchronously.
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
        
        # Get absolute paths for the command
        remotion_project_dir = str(settings.remotion_project_path.absolute())
        props_file_path = str(props_path.absolute())
        output_file_path = str(output_path.absolute())

        # Build Remotion render command
        # "PaperVideo" is your Composition ID from your frontend code
        command = (
            f"cd {remotion_project_dir} && "
            f"npx remotion render PaperVideo "
            f"{output_file_path} "
            f"--props={props_file_path} "
            f"--overwrite --log=verbose"
        )
        
        print(f"Starting async render for {script_id}...")
        print(f"Command: {command}")

        try:
            # Run Remotion asynchronously
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                print(f"Remotion rendering failed:")
                print(f"STDOUT: {stdout.decode()}")
                print(f"STDERR: {stderr.decode()}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Video rendering failed: {stderr.decode()}"
                )
            
            if not output_path.exists():
                raise Exception("Video file was not created by Remotion, despite no error.")
            
            print(f"Remotion output: {stdout.decode()}")
            
            # Return URL (works because of your app.mount in main.py)
            return f"http://localhost:{settings.backend_port}/videos/{video_filename}"
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error during rendering: {str(e)}"
            )

# Singleton instance
video_service = VideoService()