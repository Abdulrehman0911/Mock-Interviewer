import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, Loader2 } from "lucide-react";

interface ProcessingStep {
  id: number;
  name: string;
  duration: number;
  started: boolean;
  completed: boolean;
}

const INITIAL_STEPS: ProcessingStep[] = [
  { id: 1, name: "Converting video format", duration: 15, started: false, completed: false },
  { id: 2, name: "Extracting audio", duration: 3, started: false, completed: false },
  { id: 3, name: "Transcribing speech", duration: 8, started: false, completed: false },
  { id: 4, name: "Analyzing behavior", duration: 5, started: false, completed: false },
  { id: 5, name: "Calculating scores", duration: 2, started: false, completed: false },
];

export function ProcessingOverlay() {
  const [steps, setSteps] = useState<ProcessingStep[]>(
    INITIAL_STEPS.map((s) => ({ ...s }))
  );
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  // Pre-compute cumulative durations
  const cumulativeDurations = steps.reduce<number[]>((acc, step, idx) => {
    const prev = idx > 0 ? acc[idx - 1] : 0;
    acc.push(prev + step.duration);
    return acc;
  }, []);

  const totalEstimatedTime = cumulativeDurations[cumulativeDurations.length - 1] || 33;

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Update steps based on elapsed time
  useEffect(() => {
    setSteps((prev) =>
      prev.map((step, idx) => {
        const startTime = idx === 0 ? 0 : cumulativeDurations[idx - 1];
        const endTime = cumulativeDurations[idx];
        return {
          ...step,
          started: elapsedSeconds >= startTime,
          completed: elapsedSeconds >= endTime,
        };
      })
    );
  }, [elapsedSeconds]);

  const remainingSeconds = Math.max(0, totalEstimatedTime - elapsedSeconds);
  const progressPct = Math.min((elapsedSeconds / totalEstimatedTime) * 100, 100);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: "rgba(0,0,0,0.6)", backdropFilter: "blur(8px)" }}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.92, y: 24 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ type: "spring", damping: 26, stiffness: 260 }}
        className="mx-4 w-full max-w-md overflow-hidden rounded-2xl border shadow-2xl"
        style={{
          background: "var(--card, hsl(220 20% 10%))",
          borderColor: "var(--border, hsl(220 15% 20%))",
        }}
      >
        {/* Header */}
        <div className="px-8 pt-8 pb-2">
          <h2
            className="text-2xl font-bold"
            style={{ color: "var(--foreground, #fff)" }}
          >
            Processing Your Answer
          </h2>
          <p
            className="mt-1 text-sm"
            style={{ color: "var(--muted-foreground, hsl(220 10% 55%))" }}
          >
            This typically takes 30–40 seconds
          </p>
        </div>

        {/* Progress Steps */}
        <div className="space-y-1 px-8 py-4">
          {steps.map((step, index) => (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.07 }}
              className="flex items-center gap-3 rounded-lg px-3 py-2.5"
              style={{
                backgroundColor: step.started
                  ? "var(--accent, hsl(220 15% 14%))"
                  : "transparent",
              }}
            >
              {/* Step Indicator */}
              <div
                className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-sm font-bold transition-all"
                style={{
                  backgroundColor: step.completed
                    ? "hsl(142 71% 45%)"
                    : step.started
                      ? "var(--primary, hsl(217 91% 60%))"
                      : "var(--muted, hsl(220 15% 20%))",
                  color: step.completed || step.started ? "#fff" : "var(--muted-foreground, hsl(220 10% 55%))",
                  animation: step.started && !step.completed ? "pulse 2s infinite" : "none",
                }}
              >
                {step.completed ? (
                  <CheckCircle2 className="h-4 w-4" />
                ) : (
                  index + 1
                )}
              </div>

              {/* Step Name */}
              <div className="flex-1">
                <p
                  className="text-sm font-medium transition-colors"
                  style={{
                    color: step.started
                      ? "var(--foreground, #fff)"
                      : "var(--muted-foreground, hsl(220 10% 55%))",
                  }}
                >
                  {step.name}
                </p>
                <p
                  className="text-xs"
                  style={{ color: "var(--muted-foreground, hsl(220 10% 45%))" }}
                >
                  ~{step.duration}s
                </p>
              </div>

              {/* Step Status */}
              <AnimatePresence>
                {step.completed && (
                  <motion.span
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="text-xs font-semibold"
                    style={{ color: "hsl(142 71% 45%)" }}
                  >
                    Done
                  </motion.span>
                )}
                {step.started && !step.completed && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                  >
                    <Loader2
                      className="h-4 w-4 animate-spin"
                      style={{ color: "var(--primary, hsl(217 91% 60%))" }}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>

        {/* Overall Progress Bar */}
        <div className="px-8 pb-2">
          <div className="mb-2 flex items-center justify-between">
            <p
              className="text-xs font-medium"
              style={{ color: "var(--muted-foreground, hsl(220 10% 55%))" }}
            >
              Overall Progress
            </p>
            <p
              className="text-xs tabular-nums"
              style={{ color: "var(--muted-foreground, hsl(220 10% 55%))" }}
            >
              {elapsedSeconds}s / {totalEstimatedTime}s
            </p>
          </div>
          <div
            className="h-2 w-full overflow-hidden rounded-full"
            style={{ backgroundColor: "var(--muted, hsl(220 15% 15%))" }}
          >
            <motion.div
              className="h-full rounded-full"
              style={{
                background: "linear-gradient(90deg, hsl(217 91% 60%), hsl(199 89% 48%))",
              }}
              initial={{ width: "0%" }}
              animate={{ width: `${progressPct}%` }}
              transition={{ duration: 0.6, ease: "easeOut" }}
            />
          </div>
        </div>

        {/* Estimated Time Remaining */}
        <div className="px-8 pb-6 pt-3 text-center">
          <p
            className="text-sm"
            style={{ color: "var(--muted-foreground, hsl(220 10% 55%))" }}
          >
            Estimated time remaining:{" "}
            <span
              className="font-semibold tabular-nums"
              style={{ color: "var(--foreground, #fff)" }}
            >
              {remainingSeconds}s
            </span>
          </p>
        </div>

        {/* Bottom animated bar */}
        <div
          className="h-1 w-full overflow-hidden"
          style={{ backgroundColor: "var(--muted, hsl(220 15% 15%))" }}
        >
          <motion.div
            className="h-full"
            style={{
              background:
                "linear-gradient(90deg, transparent, hsl(217 91% 60%), transparent)",
              width: "40%",
            }}
            animate={{ x: ["0%", "250%"] }}
            transition={{
              repeat: Infinity,
              duration: 1.8,
              ease: "easeInOut",
            }}
          />
        </div>
      </motion.div>
    </motion.div>
  );
}
