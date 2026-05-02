import { useEffect, useRef, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, Pause, RotateCcw, Camera, Mic, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import confetti from "canvas-confetti";

const TIMES = [1, 2, 3, 4, 5];
const FAIL_REASONS = [
  { label: "Filler Words", desc: "Um, like, you know — they leak under pressure." },
  { label: "Nervousness", desc: "Shaky voice and rushed pacing kill credibility." },
  { label: "No Eye Contact", desc: "Looking away signals doubt before you speak." },
];

export function PracticePanel() {
  const [minutes, setMinutes] = useState(2);
  const [running, setRunning] = useState(false);
  const [remaining, setRemaining] = useState(minutes * 60);
  const [completed, setCompleted] = useState(false);
  const ringRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!running) {
      setRemaining(minutes * 60);
      setCompleted(false);
    }
  }, [minutes, running]);

  useEffect(() => {
    if (!running) return;
    const id = setInterval(() => {
      setRemaining((r) => {
        if (r <= 1) {
          clearInterval(id);
          setRunning(false);
          setCompleted(true);
          burstConfetti();
          return 0;
        }
        return r - 1;
      });
    }, 1000);
    return () => clearInterval(id);
  }, [running]);

  const burstConfetti = useCallback(() => {
    const rect = ringRef.current?.getBoundingClientRect();
    const origin = rect
      ? { x: (rect.left + rect.width / 2) / window.innerWidth, y: (rect.top + rect.height / 2) / window.innerHeight }
      : { x: 0.5, y: 0.5 };
    confetti({ particleCount: 120, spread: 80, origin, colors: ["#D4C7B0", "#F0EDE6", "#3a5a3d"] });
  }, []);

  const handleStart = () => {
    if (completed) {
      setRemaining(minutes * 60);
      setCompleted(false);
    }
    setRunning((r) => !r);
  };

  const handleReset = useCallback(() => {
    setRunning(false);
    setCompleted(false);
    setRemaining(minutes * 60);
  }, [minutes]);

  // Keyboard shortcuts
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (e.code === "Space") { e.preventDefault(); handleStart(); }
      if (e.key.toLowerCase() === "r") handleReset();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  const total = minutes * 60;
  const progress = 1 - remaining / total;
  const mm = String(Math.floor(remaining / 60)).padStart(2, "0");
  const ss = String(remaining % 60).padStart(2, "0");

  return (
    <section id="practice" className="py-24 md:py-32 bg-muted/40 relative">
      <div className="container mx-auto px-4">
        <div className="grid lg:grid-cols-2 gap-12 items-center max-w-6xl mx-auto">
          {/* LEFT */}
          <motion.div
            initial={{ opacity: 0, x: -24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <div className="text-sm font-medium text-primary mb-3">The problem</div>
            <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-6">
              Why do people fail at <span className="text-gradient text-[#2f7000]">interviews?</span>
            </h2>
            <p className="text-muted-foreground text-lg mb-8">
              Most candidates know the answers. They lose the offer in the delivery.
            </p>
            <div className="space-y-3">
              {FAIL_REASONS.map((r, i) => (
                <motion.div
                  key={r.label}
                  initial={{ opacity: 0, x: -10 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  className="flex gap-3 items-start rounded-xl glass p-4"
                >
                  <div className="h-8 w-8 rounded-lg bg-destructive/10 text-destructive grid place-items-center shrink-0">
                    <AlertCircle className="h-4 w-4" />
                  </div>
                  <div>
                    <div className="font-semibold">{r.label}</div>
                    <div className="text-sm text-muted-foreground text-slate-500">{r.desc}</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* RIGHT — Timer */}
          <motion.div
            initial={{ opacity: 0, x: 24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="rounded-3xl glass shadow-elegant p-6 sm:p-8"
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold tracking-tight">What's your answer time?</h3>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full rounded-full bg-success opacity-75" style={{ animation: "pulse-dot 1.6s ease-in-out infinite" }} />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-success" />
                </span>
                Live tracking
              </div>
            </div>

            <div className="grid grid-cols-5 gap-2 mb-8">
              {TIMES.map((t) => (
                <button
                  key={t}
                  onClick={() => setMinutes(t)}
                  className={`min-h-11 rounded-xl text-sm font-medium transition-all ${
                    minutes === t
                      ? "bg-gradient-primary text-primary-foreground shadow-elegant scale-105"
                      : "bg-background/60 hover:bg-background border"
                  }`}
                >
                  {t}min
                </button>
              ))}
            </div>

            {/* Circular timer */}
            <div ref={ringRef} className="relative mx-auto h-56 w-56 sm:h-64 sm:w-64">
              <svg className="absolute inset-0 -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" stroke="var(--muted)" strokeWidth="6" fill="none" />
                <motion.circle
                  cx="50" cy="50" r="45" fill="none"
                  stroke="url(#g1)" strokeWidth="6" strokeLinecap="round"
                  strokeDasharray={2 * Math.PI * 45}
                  animate={{ strokeDashoffset: 2 * Math.PI * 45 * (1 - progress) }}
                  transition={{ duration: 0.5, ease: "linear" }}
                />
                <defs>
                  <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="oklch(0.85 0.04 80)" />
                    <stop offset="100%" stopColor="oklch(0.55 0.10 150)" />
                  </linearGradient>
                </defs>
              </svg>
              <div className="absolute inset-0 grid place-items-center">
                <div className="text-center">
                  <div className="text-5xl sm:text-6xl font-bold tracking-tight tabular-nums">
                    {mm}:{ss}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {completed ? "Session complete!" : running ? "Recording…" : "Ready"}
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-8 flex gap-2 justify-center">
              <Button
                size="lg"
                onClick={handleStart}
                className="bg-gradient-primary text-primary-foreground hover:opacity-95 shadow-elegant min-w-32"
              >
                {running ? <><Pause className="mr-2 h-4 w-4" /> Pause</> : <><Play className="mr-2 h-4 w-4" /> {completed ? "Restart" : "Start"}</>}
              </Button>
              <Button size="lg" variant="outline" onClick={handleReset}>
                <RotateCcw className="h-4 w-4" />
              </Button>
            </div>

            <div className="mt-4 flex items-center justify-center gap-4 text-xs text-muted-foreground">
              <span className="flex items-center gap-1.5"><Camera className="h-3 w-3" /> Camera ready</span>
              <span className="flex items-center gap-1.5"><Mic className="h-3 w-3" /> Mic active</span>
              <span className="hidden sm:inline">⌨ Space / R</span>
            </div>

            <AnimatePresence>
              {completed && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="mt-6 rounded-xl bg-success/10 border border-success/30 p-4 text-center text-sm"
                >
                  <span className="font-semibold text-success text-slate-500">Great work!</span>{" "}
                  <span className="text-muted-foreground text-slate-500">Generating your feedback report below…</span>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
