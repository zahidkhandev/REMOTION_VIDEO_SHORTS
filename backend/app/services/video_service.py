import asyncio
import os
from pathlib import Path
from fastapi import HTTPException
from ..config import get_settings
from asyncio.streams import StreamReader # For type hinting

settings = get_settings()

class VideoService:
    def __init__(self):
        print("Initializing VideoService...")
        self.videos_dir = settings.storage_path / "videos"
        self.props_dir = settings.storage_path / "props"
        
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        print(f"Storage 'videos' directory ensured at: {self.videos_dir.absolute()}")
        print(f"Storage 'props' directory is at: {self.props_dir.absolute()}")

    async def _log_stream(self, stream: StreamReader, log_prefix: str):
        """
        Asynchronously reads from a process stream and prints lines with a prefix.
        """
        while not stream.at_eof():
            line = await stream.readline()
            if not line:
                break
            # Decode, strip whitespace, and print the log line
            print(f"{log_prefix} {line.decode().strip()}")

    async def render_video(self, script_id: str) -> str:
        """
        Render video using Remotion CLI asynchronously.
        Returns the URL to the rendered video.
        """
        print(f"\n--- Video Render Initiated ---")
        print(f"Script ID: {script_id}")

        # 1. Check if props file exists
        print(f"1. Verifying props file...")
        props_path = self.props_dir / f"{script_id}.json"
        if not props_path.exists():
            print(f"   ERROR: Props file not found at {props_path.absolute()}")
            raise HTTPException(
                status_code=404,
                detail=f"Script props not found for '{script_id}'. Process the paper first."
            )
        print(f"   Props file found: {props_path.absolute()}")

        # 2. Define output path
        video_filename = f"{script_id}.mp4"
        output_path = self.videos_dir / video_filename
        print(f"2. Set output video path to: {output_path.absolute()}")
        
        # 3. Get absolute paths for the command
        print(f"3. Resolving absolute paths...")
        try:
            remotion_project_dir = str(settings.remotion_project_path.absolute())
            props_file_path = str(props_path.absolute())
            output_file_path = str(output_path.absolute())
            
            print(f"   Remotion Project: {remotion_project_dir}")
            print(f"   Props JSON: {props_file_path}")
            print(f"   Output MP4: {output_file_path}")

        except Exception as e:
            print(f"   ERROR: Failed to resolve absolute paths. Check config. {e}")
            raise HTTPException(status_code=500, detail=f"Path configuration error: {e}")

        # 4. Build Remotion render command
        print(f"4. Building Remotion command with proxy config...")
        proxy_url = "http://localhost:8080"
        
        # --- *** THIS IS THE NEW FIX *** ---
        # We will now explicitly tell npm/npx to use the proxy,
        # as it seems to be ignoring the environment variables.
        command = (
            f"cd {remotion_project_dir} && "
            f"npm config set proxy {proxy_url} && "
            f"npm config set https-proxy {proxy_url} && "
            f"npx remotion render PaperVideo "
            f"{output_file_path} "
            f"--props={props_file_path} "
            f"--overwrite --log=verbose"
        )
        # --- *** END OF NEW FIX *** ---
        
        print(f"   Command: {command}")

        try:
            # 5. Set up environment variables (still good to have)
            print("5. Setting up subprocess environment with proxy...")
            current_env = os.environ.copy()
            current_env["http_proxy"] = proxy_url
            current_env["https_proxy"] = proxy_url
            current_env["HTTP_PROXY"] = proxy_url
            current_env["HTTPS_PROXY"] = proxy_url
            print(f"   Subprocess will use proxy: {proxy_url}")

            # 6. Run Remotion asynchronously
            print(f"6. Launching async subprocess...")
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=current_env  # Pass the modified environment
            )
            
            # 7. Attach real-time loggers
            print(f"7. Attaching real-time log streams. (This is the long part...)")
            
            if not process.stdout:
                print("   FATAL ERROR: Subprocess stdout is None.")
                raise Exception("Subprocess failed to initialize stdout stream.")
            
            if not process.stderr:
                print("   FATAL ERROR: Subprocess stderr is None.")
                raise Exception("Subprocess failed to initialize stderr stream.")
            
            await asyncio.gather(
                self._log_stream(process.stdout, "[Remotion STDOUT]"),
                self._log_stream(process.stderr, "[Remotion STDERR]")
            )

            # 8. Wait for the process to fully terminate
            await process.wait()
            print(f"8. Subprocess finished with return code: {process.returncode}")
            
            # 9. Check for errors
            if process.returncode != 0:
                print(f"   ERROR: Remotion rendering failed with non-zero exit code.")
                raise HTTPException(
                    status_code=500,
                    detail=f"Video rendering failed. Check server logs for [Remotion STDERR] output."
                )
            
            # 10. Verify file was created
            print(f"9. Verifying output file exists...")
            if not output_path.exists():
                print(f"   ERROR: Remotion exited successfully but video file was not created at {output_path.absolute()}")
                raise Exception("Video file was not created by Remotion, despite no error.")
            print(f"   Output file successfully created.")
            
            # 11. Return URL
            video_url = f"http://localhost:{settings.backend_port}/videos/{video_filename}"
            print(f"10. Render successful. Returning URL: {video_url}")
            print(f"--- Video Render Finished ---")
            
            return video_url
            
        except Exception as e:
            print(f"FATAL ERROR during rendering: {str(e)}")
            if isinstance(e, HTTPException):
                raise e # Re-raise HTTPException
            
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error during rendering: {str(e)}"
            )

# Singleton instance
video_service = VideoService()