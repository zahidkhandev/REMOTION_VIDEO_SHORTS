import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

export interface Scene {
  title: string;
  narration: string;
  visual: string;
  audio_path: string;
  duration_in_seconds: number;
}

export interface VideoScript {
  script_id: string;
  scenes: Scene[];
  total_duration_seconds: number;
}

export interface RenderResponse {
  video_url: string;
  script_id: string;
}

export const api = {
  async processPaper(file: File, duration: number = 60): Promise<VideoScript> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await axios.post<VideoScript>(
      `${API_BASE_URL}/paper/process?duration=${duration}`,
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
      }
    );

    return response.data;
  },

  async renderVideo(scriptId: string): Promise<RenderResponse> {
    const response = await axios.post<RenderResponse>(
      `${API_BASE_URL}/video/render`,
      { script_id: scriptId }
    );

    return response.data;
  },
};
