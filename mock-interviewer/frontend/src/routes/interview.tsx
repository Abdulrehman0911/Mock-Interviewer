import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useRef, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Mic,
  Video,
  Square,
  SkipForward,
  Loader2,
  Sparkles,
  AlertCircle,
  CheckCircle2,
  Clock,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";
import { useInterviewStore } from "@/store/interviewStore";
import { processVideo } from "@/lib/api";
import { toast } from "sonner";
import { ProcessingOverlay } from "@/components/interview/ProcessingOverlay";

export const Route = createFileRoute("/interview")({
  component: InterviewPage,
});

type Stage = "ready" | "recording" | "processing" | "done";

function formatTime(s: number) {
  const m = Math.floor(s / 60).toString().padStart(2, "0");
  return `${m}:${(s % 60).toString().padStart(2, "0")}`;
}

function InterviewPage() {
  const navigate = useNavigate();
  const { user, loading } = useAuth();

  const company = useInterviewStore((s) => s.company);
  const role = useInterviewStore((s) => s.role);
  const questions = useInterviewStore((s) => s.questions);
  const currentQuestionIndex = useInterviewStore((s) => s.currentQuestionIndex);
  const addResult = useInterviewStore((s) => s.addResult);
  const nextQuestion = useInterviewStore((s) => s.nextQuestion);
  const setProcessing = useInterviewStore((s) => s.setProcessing);
  const results = useInterviewStore((s) => s.results);
  const savePastInterview = useInterviewStore((s) => s.savePastInterview);
  const reset = useInterviewStore((s) => s.reset);

  const [stage, setStage] = useState<Stage>("ready");
  const [elapsed, setElapsed] = useState(0);
  const [streamReady, setStreamReady] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const question = questions[currentQuestionIndex];
  const totalQuestions = questions.length;
  const progress = ((currentQuestionIndex) / totalQuestions) * 100;
  const isLast = currentQuestionIndex === totalQuestions - 1;

  useEffect(() => {
    if (!loading && !user) navigate({ to: "/auth", replace: true });
    if (!loading && (!company || !role || questions.length === 0))
      navigate({ to: "/select-company", replace: true });
  }, [loading, user, company, role, questions, navigate]);

  // Init webcam on mount
  useEffect(() => {
    let mounted = true;
    navigator.mediaDevices
      .getUserMedia({ video: { width: 1280, height: 720 }, audio: true })
      .then((stream) => {
        if (!mounted) { stream.getTracks().forEach((t) => t.stop()); return; }
        streamRef.current = stream;
        if (videoRef.current) videoRef.current.srcObject = stream;
        setStreamReady(true);
      })
      .catch(() => {
        setCameraError("Could not access camera/microphone. Check browser permissions.");
        toast.error("Camera access denied.");
      });
    return () => {
      mounted = false;
      streamRef.current?.getTracks().forEach((t) => t.stop());
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  const startRecording = useCallback(() => {
    if (!streamRef.current) return;
    chunksRef.current = [];
    const mimeType = MediaRecorder.isTypeSupported("video/webm;codecs=vp9")
      ? "video/webm;codecs=vp9"
      : "video/webm";
    const recorder = new MediaRecorder(streamRef.current, { mimeType });
    recorder.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data); };
    recorder.start(100);
    recorderRef.current = recorder;
    setElapsed(0);
    setStage("recording");
    timerRef.current = setInterval(() => setElapsed((s) => s + 1), 1000);
  }, []);

  const stopRecordingAndProcess = useCallback(async () => {
    if (!recorderRef.current || !question) return;
    if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }

    setStage("processing");
    setProcessing(true, 0);

    await new Promise<void>((resolve) => {
      recorderRef.current!.onstop = () => resolve();
      recorderRef.current!.stop();
    });

    const blob = new Blob(chunksRef.current, { type: "video/webm" });
    const difficultyNum = question.difficulty === "easy" ? 1 : question.difficulty === "medium" ? 2 : 3;

    try {
      console.log("[MockMate] Processing question", question.question_id, "for role:", role);
      const result = await processVideo(blob, question.question_id, question.question, difficultyNum, role ?? "Software Engineer");

      if (result.success) {
        console.log("[MockMate] Question scored:", result.scores?.final?.score, "/ 10");
        addResult({ question, videoResult: result });
      } else {
        console.warn("[MockMate] Backend returned success=false", result.error);
        toast.error(result.error ? `Processing error: ${result.error}` : "Processing failed. Answer recorded with zero score.");
        addResult({
          question,
          videoResult: {
            ...result,
            success: false,
            transcript: result.transcript || "(processing failed)",
          },
        });
      }
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : "Unknown error";
      console.error("[MockMate] Video processing exception:", msg);
      toast.error(`Video error: ${msg}`);
      addResult({
        question: question!,
        videoResult: {
          success: false,
          scores: { behavioral: { score: 0, out_of: 4, percentage: 0, subscale: {} }, correctness: { score: 0, out_of: 6, percentage: 0 }, final: { score: 0, out_of: 10, percentage: 0 } },
          transcript: "(exception)",
          features: { wpm: 0, eye_contact_pct: 0, filler_count: 0, pause_count: 0 },
          feedback: {},
        },
      });
    } finally {
      setProcessing(false);
    }

    goNext();
  }, [question, role, addResult, setProcessing]);

  const skipQuestion = () => {
    if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
    if (recorderRef.current?.state === "recording") recorderRef.current.stop();
    toast.info("Question skipped — not counted in score");
    addResult({
      question: question!,
      videoResult: {
        success: false,
        scores: { behavioral: { score: 0, out_of: 4, percentage: 0, subscale: {} }, correctness: { score: 0, out_of: 6, percentage: 0 }, final: { score: 0, out_of: 10, percentage: 0 } },
        transcript: "(skipped)",
        features: { wpm: 0, eye_contact_pct: 0, filler_count: 0, pause_count: 0 },
        feedback: {},
      },
    });
    goNext();
  };

  const goNext = () => {
    setStage("ready");
    setElapsed(0);
    if (isLast) {
      finishInterview();
    } else {
      nextQuestion();
    }
  };

  const finishInterview = () => {
    const allResults = [...useInterviewStore.getState().results];
    const scores = allResults.map((r) => r.videoResult.scores?.final?.score ?? 0);
    const overall = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;

    savePastInterview({
      id: Date.now().toString(),
      company: company?.name ?? "Unknown",
      role: role ?? "Unknown",
      date: new Date().toISOString(),
      overallScore: parseFloat(overall.toFixed(1)),
      results: allResults,
    });

    navigate({ to: "/report", search: { company: company?.name ?? "", role: role ?? "", pastId: "" } });
  };

  const handleCancel = () => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    if (timerRef.current) clearInterval(timerRef.current);
    reset();
    navigate({ to: "/home" });
  };

  if (!question) return null;

  return (
    <main className="min-h-screen bg-background text-foreground flex flex-col">
      {/* Top bar */}
      <div className="border-b border-border/60 bg-background/80 backdrop-blur-md sticky top-0 z-40">
        <div className="container mx-auto px-4 py-3">
          {/* Progress bar */}
          <div className="h-1 w-full bg-muted rounded-full mb-3 overflow-hidden">
            <motion.div
              className="h-full bg-primary rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>

          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="grid place-items-center h-8 w-8 rounded-lg bg-primary text-primary-foreground">
                <Sparkles className="h-4 w-4" />
              </span>
              <span className="hidden sm:block text-sm text-muted-foreground">
                {company?.name} · {role}
              </span>
            </div>

            <div className="flex items-center gap-4">
              {stage === "recording" && (
                <div className="flex items-center gap-2">
                  <span className="relative flex h-2.5 w-2.5">
                    <span className="absolute inline-flex h-full w-full rounded-full bg-destructive opacity-75 animate-ping" />
                    <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-destructive" />
                  </span>
                  <span className="text-xs font-medium text-destructive uppercase tracking-wide">REC</span>
                  <span className="font-mono tabular-nums text-sm">{formatTime(elapsed)}</span>
                </div>
              )}
              <span className="text-sm font-medium">
                {currentQuestionIndex + 1}
                <span className="text-muted-foreground">/{totalQuestions}</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Main area */}
      <div className="flex-1 container mx-auto px-4 py-8 max-w-6xl">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-full">
          {/* Question panel */}
          <AnimatePresence mode="wait">
            <motion.div
              key={question.question_id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
              className="flex flex-col justify-center"
            >
              <div className="flex items-center gap-3 mb-6">
                <span className="text-xs text-muted-foreground">Question {currentQuestionIndex + 1}</span>
              </div>

              <h2 className="text-2xl md:text-3xl font-semibold leading-relaxed mb-8">
                {question.question}
              </h2>

              {/* Controls */}
              <div className="flex flex-wrap gap-3">
                {stage === "ready" && (
                  <>
                    <Button
                      size="lg"
                      onClick={startRecording}
                      disabled={!streamReady || !!cameraError}
                      className="h-12 px-8 gap-2 shine shadow-glow"
                    >
                      <Mic className="h-5 w-5" />
                      I&apos;m Ready
                    </Button>
                    <Button variant="outline" size="lg" onClick={skipQuestion} className="h-12 gap-2">
                      <SkipForward className="h-4 w-4" />
                      Skip
                    </Button>
                  </>
                )}

                {stage === "recording" && (
                  <>
                    <Button
                      size="lg"
                      variant="destructive"
                      onClick={stopRecordingAndProcess}
                      className="h-12 px-8 gap-2 animate-pulse-red shadow-glow"
                    >
                      <Square className="h-5 w-5 fill-current" />
                      Stop Recording
                    </Button>
                    <Button variant="outline" size="lg" onClick={skipQuestion} className="h-12 gap-2">
                      <SkipForward className="h-4 w-4" />
                      Skip
                    </Button>
                  </>
                )}

                {stage === "processing" && (
                  <div className="flex items-center gap-3 py-2">
                    <Loader2 className="h-5 w-5 animate-spin text-primary" />
                    <span className="text-sm text-muted-foreground">Processing your answer…</span>
                  </div>
                )}
              </div>

              <div className="mt-6">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleCancel}
                  className="text-muted-foreground hover:text-foreground"
                >
                  Cancel Interview
                </Button>
              </div>
            </motion.div>
          </AnimatePresence>

          {/* Camera panel */}
          <div className="flex flex-col gap-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1 }}
              className="relative w-full aspect-video rounded-2xl overflow-hidden bg-foreground/5 shadow-elegant border border-border/40"
            >
              <video
                ref={videoRef}
                autoPlay
                muted
                playsInline
                className="w-full h-full object-cover"
              />

              {!streamReady && !cameraError && (
                <div className="absolute inset-0 grid place-items-center text-muted-foreground">
                  <div className="flex flex-col items-center gap-3">
                    <Loader2 className="h-8 w-8 animate-spin" />
                    <p className="text-sm">Initializing camera…</p>
                  </div>
                </div>
              )}

              {cameraError && (
                <div className="absolute inset-0 grid place-items-center text-destructive px-8">
                  <div className="flex flex-col items-center gap-3 text-center">
                    <AlertCircle className="h-10 w-10" />
                    <p className="text-sm">{cameraError}</p>
                  </div>
                </div>
              )}

              {/* Camera/mic badges */}
              {streamReady && (
                <div className="absolute top-3 left-3 flex gap-2">
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-background/80 backdrop-blur px-2.5 py-1 text-xs font-medium">
                    <Video className="h-3 w-3" /> Camera
                  </span>
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-background/80 backdrop-blur px-2.5 py-1 text-xs font-medium">
                    <Mic className="h-3 w-3" /> Mic
                  </span>
                </div>
              )}

              {/* Recording overlay */}
              {stage === "recording" && (
                <div className="absolute top-3 right-3">
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-destructive/90 backdrop-blur px-3 py-1 text-xs font-semibold text-white">
                    <span className="relative flex h-2 w-2">
                      <span className="absolute inline-flex h-full w-full rounded-full bg-white opacity-75 animate-ping" />
                      <span className="relative inline-flex h-2 w-2 rounded-full bg-white" />
                    </span>
                    RECORDING
                  </span>
                </div>
              )}

              {/* Timer overlay */}
              {(stage === "recording") && (
                <div className="absolute bottom-3 left-1/2 -translate-x-1/2">
                  <span className="font-mono tabular-nums text-2xl font-bold text-white bg-black/50 backdrop-blur rounded-lg px-4 py-2">
                    {formatTime(elapsed)}
                  </span>
                </div>
              )}

              {/* Processing overlay — in-camera spinner (full overlay is rendered outside) */}
              {stage === "processing" && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="absolute inset-0 bg-background/80 backdrop-blur-sm grid place-items-center"
                >
                  <div className="flex flex-col items-center gap-4">
                    <div className="relative">
                      <div className="h-16 w-16 rounded-full border-4 border-primary/20" />
                      <div className="absolute inset-0 h-16 w-16 rounded-full border-4 border-primary border-t-transparent animate-spin" />
                    </div>
                    <p className="text-sm font-medium">Analyzing…</p>
                  </div>
                </motion.div>
              )}
            </motion.div>

            {/* Tips */}
            {stage === "ready" && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-xl bg-card/60 border border-border/40 p-4"
              >
                <h3 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">
                  Tips for a great answer
                </h3>
                <ul className="space-y-1.5 text-xs text-muted-foreground">
                  {[
                    "Look at the camera, not the screen",
                    "Speak clearly at a moderate pace",
                    "Use the STAR method for behavioral questions",
                    "Avoid filler words (um, uh, like)",
                  ].map((tip) => (
                    <li key={tip} className="flex items-start gap-2">
                      <CheckCircle2 className="h-3.5 w-3.5 text-success shrink-0 mt-0.5" />
                      {tip}
                    </li>
                  ))}
                </ul>
              </motion.div>
            )}

            {/* Timer badge when ready */}
            {stage === "ready" && (
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Clock className="h-3.5 w-3.5" />
                Recommended: 1–3 minutes per answer
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Full-screen processing overlay with step-by-step progress */}
      <AnimatePresence>
        {stage === "processing" && <ProcessingOverlay />}
      </AnimatePresence>
    </main>
  );
}
