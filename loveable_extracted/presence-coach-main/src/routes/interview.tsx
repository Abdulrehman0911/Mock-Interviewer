import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Mic, Video, X, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export const Route = createFileRoute("/interview")({
  component: Interview,
  validateSearch: (search: Record<string, unknown>) => ({
    company: (search.company as string) ?? "",
    field: (search.field as string) ?? "",
  }),
  head: () => ({ meta: [{ title: "Interview — MockInterviewer" }] }),
});

function formatTime(s: number) {
  const m = Math.floor(s / 60).toString().padStart(2, "0");
  const sec = (s % 60).toString().padStart(2, "0");
  return `${m}:${sec}`;
}

function Interview() {
  const navigate = useNavigate();
  const { company, field } = Route.useSearch();
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [streamReady, setStreamReady] = useState(false);

  useEffect(() => {
    let mounted = true;
    navigator.mediaDevices
      .getUserMedia({ video: true, audio: true })
      .then((stream) => {
        if (!mounted) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        streamRef.current = stream;
        if (videoRef.current) videoRef.current.srcObject = stream;
        setStreamReady(true);
      })
      .catch(() => {
        toast.error("Could not access camera/microphone. Check browser permissions.");
      });

    return () => {
      mounted = false;
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  useEffect(() => {
    const id = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(id);
  }, []);

  const stopStream = () => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
  };

  const handleCancel = () => {
    stopStream();
    navigate({ to: "/home" });
  };

  const handleFinish = () => {
    stopStream();
    navigate({ to: "/report", search: { company, field } });
  };

  return (
    <main className="min-h-screen bg-background text-foreground flex flex-col">
      {/* Top bar */}
      <div className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full rounded-full bg-destructive opacity-75 animate-ping" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-destructive" />
            </span>
            <span className="text-sm font-medium">REC</span>
            <span className="text-sm text-muted-foreground hidden sm:inline">
              {company} · {field}
            </span>
          </div>
          <div className="font-mono tabular-nums text-lg">{formatTime(elapsed)}</div>
        </div>
      </div>

      {/* Video area */}
      <div className="flex-1 grid place-items-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-4xl aspect-video rounded-2xl overflow-hidden bg-foreground/5 shadow-elegant relative"
        >
          <video
            ref={videoRef}
            autoPlay
            muted
            playsInline
            className="w-full h-full object-cover bg-black"
          />
          {!streamReady && (
            <div className="absolute inset-0 grid place-items-center text-muted-foreground">
              <div className="flex flex-col items-center gap-3">
                <Video className="h-10 w-10" />
                <p className="text-sm">Waiting for camera…</p>
              </div>
            </div>
          )}

          {/* Indicator badges */}
          <div className="absolute top-4 left-4 flex gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-background/80 backdrop-blur px-3 py-1 text-xs font-medium">
              <Video className="h-3 w-3" /> Camera
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-full bg-background/80 backdrop-blur px-3 py-1 text-xs font-medium">
              <Mic className="h-3 w-3" /> Mic
            </span>
          </div>
        </motion.div>
      </div>

      {/* Bottom controls */}
      <div className="border-t">
        <div className="container mx-auto px-4 py-5 flex items-center justify-center gap-3">
          <Button variant="outline" size="lg" onClick={handleCancel} className="h-12 px-6">
            <X className="mr-2 h-4 w-4" /> Cancel Interview
          </Button>
          <Button size="lg" onClick={handleFinish} className="h-12 px-6">
            <CheckCircle2 className="mr-2 h-4 w-4" /> Finish & See Report
          </Button>
        </div>
      </div>
    </main>
  );
}
