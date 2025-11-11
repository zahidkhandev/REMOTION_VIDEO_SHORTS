import React, { useState } from "react";
import { Upload, Play, FileText, Video } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { api, type VideoScript } from "@/lib/api";

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [script, setScript] = useState<VideoScript | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isRendering, setIsRendering] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setScript(null);
      setVideoUrl(null);
    }
  };

  const handleProcess = async () => {
    if (!file) return;

    setIsProcessing(true);
    setProgress(10);

    try {
      toast.loading("Analyzing paper and generating script...", {
        id: "processing",
      });

      setProgress(30);
      const result = await api.processPaper(file);
      setProgress(100);

      setScript(result);
      toast.success(`Generated ${result.scenes.length} scenes!`, {
        id: "processing",
      });
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to process paper", {
        id: "processing",
      });
    } finally {
      setIsProcessing(false);
      setProgress(0);
    }
  };

  const handleRender = async () => {
    if (!script) return;

    setIsRendering(true);
    setProgress(10);

    try {
      toast.loading("Rendering video... This may take 2-5 minutes", {
        id: "rendering",
      });

      // Simulate progress
      const interval = setInterval(() => {
        setProgress((prev) => Math.min(prev + 5, 90));
      }, 2000);

      const result = await api.renderVideo(script.script_id);
      clearInterval(interval);
      setProgress(100);

      setVideoUrl(result.video_url);
      toast.success("Video rendered successfully!", { id: "rendering" });
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to render video", {
        id: "rendering",
      });
    } finally {
      setIsRendering(false);
      setProgress(0);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-8">
      <div className="max-w-5xl mx-auto space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">
            Paper to Video Automator
          </h1>
          <p className="text-muted-foreground">
            Transform research papers into engaging short-form videos
          </p>
        </div>

        {/* Step 1: Upload */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="w-5 h-5" />
              Step 1: Upload Paper
            </CardTitle>
            <CardDescription>
              Upload a PDF research paper to get started
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid w-full max-w-sm items-center gap-1.5">
              <Label htmlFor="paper">PDF File</Label>
              <Input
                id="paper"
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                disabled={isProcessing || isRendering}
              />
            </div>
            {file && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <FileText className="w-4 h-4" />
                <span>{file.name}</span>
              </div>
            )}
            <Button
              onClick={handleProcess}
              disabled={!file || isProcessing || isRendering}
            >
              {isProcessing ? "Processing..." : "Generate Script"}
            </Button>
            {isProcessing && <Progress value={progress} className="w-full" />}
          </CardContent>
        </Card>

        {/* Step 2: Review Script */}
        {script && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Step 2: Review Script
              </CardTitle>
              <CardDescription>
                {script.scenes.length} scenes •{" "}
                {script.total_duration_seconds.toFixed(1)}s total
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {script.scenes.map((scene, i) => (
                  <div key={i} className="p-4 bg-muted rounded-lg space-y-2">
                    <div className="flex items-start justify-between">
                      <h4 className="font-semibold">
                        Scene {i + 1}: {scene.title}
                      </h4>
                      <span className="text-xs text-muted-foreground">
                        {scene.duration_in_seconds.toFixed(1)}s
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {scene.narration}
                    </p>
                    <div className="flex gap-2 text-xs">
                      <span className="px-2 py-1 bg-background rounded">
                        {scene.visual}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
              <Separator />
              <Button
                onClick={handleRender}
                disabled={isRendering}
                size="lg"
                className="w-full"
              >
                <Play className="w-4 h-4 mr-2" />
                {isRendering ? "Rendering Video..." : "Render Video"}
              </Button>
              {isRendering && (
                <div className="space-y-2">
                  <Progress value={progress} className="w-full" />
                  <p className="text-sm text-center text-muted-foreground">
                    Rendering in progress... This may take a few minutes
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Step 3: Watch Video */}
        {videoUrl && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Video className="w-5 h-5" />
                Step 3: Your Video
              </CardTitle>
              <CardDescription>Video rendered successfully!</CardDescription>
            </CardHeader>
            <CardContent className="flex justify-center">
              <video
                controls
                src={videoUrl}
                className="max-w-md w-full rounded-lg shadow-2xl aspect-[9/16]"
              />
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

export default App;
