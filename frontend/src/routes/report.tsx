import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import {
  Trophy,
  Eye,
  Mic2,
  Brain,
  CheckCircle2,
  MessageSquare,
  Home,
  RotateCcw,
  TrendingUp,
  Sparkles,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useInterviewStore } from "@/store/interviewStore";
import { useAuth } from "@/hooks/use-auth";

export const Route = createFileRoute("/report")({
  component: ReportPage,
  validateSearch: (s: Record<string, unknown>) => ({
    company: (s.company as string) ?? "",
    role: (s.role as string) ?? "",
    pastId: (s.pastId as string) ?? "",
  }),
});

function scoreColor(score: number, outOf = 10) {
  const p = (score / outOf) * 100;
  if (p >= 70) return "#55B66E";
  if (p >= 40) return "#F59E0B";
  return "#E6443D";
}

function scoreLabel(score: number) {
  if (score >= 8) return "Excellent";
  if (score >= 6) return "Good";
  if (score >= 4) return "Average";
  return "Needs Work";
}

function ScoreRing({ score, outOf = 10 }: { score: number; outOf?: number }) {
  const radius = 54;
  const circ = 2 * Math.PI * radius;
  const [offset, setOffset] = useState(circ);
  const color = scoreColor(score, outOf);

  useEffect(() => {
    const timer = setTimeout(() => {
      const pct = Math.min(score / outOf, 1);
      setOffset(circ - pct * circ);
    }, 200);
    return () => clearTimeout(timer);
  }, [score, outOf, circ]);

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r={radius} fill="none" stroke="currentColor" strokeWidth="8" className="text-muted/40" />
        <circle
          cx="70"
          cy="70"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          style={{ transform: "rotate(-90deg)", transformOrigin: "center", transition: "stroke-dashoffset 1.8s cubic-bezier(0.4,0,0.2,1)" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-4xl font-bold tabular-nums" style={{ color }}>
          {score.toFixed(1)}
        </span>
        <span className="text-xs text-muted-foreground">/{outOf}</span>
      </div>
    </div>
  );
}

function ReportPage() {
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const { company: search_company, role: search_role, pastId } = Route.useSearch();

  const results = useInterviewStore((s) => s.results);
  const pastInterviews = useInterviewStore((s) => s.pastInterviews);
  const reset = useInterviewStore((s) => s.reset);
  const storeCompany = useInterviewStore((s) => s.company);
  const storeRole = useInterviewStore((s) => s.role);

  useEffect(() => {
    if (!loading && !user) navigate({ to: "/auth", replace: true });
  }, [loading, user, navigate]);

  // Resolve data source: live results or past interview
  const pastInterview = pastId ? pastInterviews.find((p) => p.id === pastId) : null;
  const displayResults = pastInterview ? pastInterview.results : results;
  const displayCompany = pastInterview?.company ?? storeCompany?.name ?? search_company;
  const displayRole = pastInterview?.role ?? storeRole ?? search_role;

  // Aggregate scores
  const validResults = displayResults.filter((r) => r.videoResult.success);
  const overallScore =
    validResults.length > 0
      ? validResults.reduce((sum, r) => sum + (r.videoResult.scores?.final?.score ?? 0), 0) / validResults.length
      : 0;
  const avgBehavioral =
    validResults.length > 0
      ? validResults.reduce((sum, r) => sum + (r.videoResult.scores?.behavioral?.score ?? 0), 0) / validResults.length
      : 0;
  const avgCorrectness =
    validResults.length > 0
      ? validResults.reduce((sum, r) => sum + (r.videoResult.scores?.correctness?.score ?? 0), 0) / validResults.length
      : 0;
  const avgEyeContact =
    validResults.length > 0
      ? validResults.reduce((sum, r) => sum + (r.videoResult.features?.eye_contact_pct ?? 0), 0) / validResults.length
      : 0;
  const avgWpm =
    validResults.length > 0
      ? validResults.reduce((sum, r) => sum + (r.videoResult.features?.wpm ?? 0), 0) / validResults.length
      : 0;
  const totalFillers = validResults.reduce((sum, r) => sum + (r.videoResult.features?.filler_count ?? 0), 0);

  // Aggregate feedback
  const allStrengths = validResults.flatMap((r) => r.videoResult.feedback?.strengths ?? []);
  const allImprovements = validResults.flatMap((r) => r.videoResult.feedback?.improvements ?? []);
  const uniqueStrengths = [...new Set(allStrengths)].slice(0, 3);
  const uniqueImprovements = [...new Set(allImprovements)].slice(0, 3);

  // Fallback feedback
  const displayStrengths = uniqueStrengths.length > 0 ? uniqueStrengths : [
    `Completed ${displayResults.length} interview question${displayResults.length !== 1 ? "s" : ""}`,
    "Showed consistency across responses",
  ];
  const displayImprovements = uniqueImprovements.length > 0 ? uniqueImprovements : [
    "Keep practicing to improve your scores",
    "Focus on reducing filler words",
    "Maintain steady eye contact with the camera",
  ];

  const handlePracticeAgain = () => {
    reset();
    navigate({ to: "/select-company" });
  };

  const container = { hidden: {}, show: { transition: { staggerChildren: 0.12, delayChildren: 0.3 } } };
  const item = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0 } };

  return (
    <main className="min-h-screen bg-background text-foreground py-12 px-4">
      <div className="pointer-events-none fixed inset-0 -z-10 bg-gradient-mesh opacity-40" />
      <div className="container mx-auto max-w-4xl">

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-10">
          <div className="mx-auto mb-4 grid place-items-center h-14 w-14 rounded-2xl bg-primary/10">
            <Trophy className="h-6 w-6 text-primary" />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight mb-2">Interview Complete!</h1>
          {(displayCompany || displayRole) && (
            <p className="text-muted-foreground">
              {displayRole}{displayCompany ? ` · ${displayCompany}` : ""}
            </p>
          )}
        </motion.div>

        {/* Overall score hero */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="rounded-3xl p-8 md:p-10 text-center shadow-elegant mb-8 border border-border/40"
          style={{ background: "var(--gradient-hero)" }}
        >
          <div className="text-primary-foreground/70 text-sm uppercase tracking-wider mb-6">Overall Score</div>
          <ScoreRing score={parseFloat(overallScore.toFixed(1))} outOf={10} />
          <div className="text-primary-foreground/80 mt-4 font-medium">
            {scoreLabel(overallScore)} · {validResults.length}/{displayResults.length} questions scored
          </div>
        </motion.div>

        {/* Score breakdown cards */}
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8"
        >
          {[
            {
              icon: Brain,
              label: "Behavioral",
              value: `${avgBehavioral.toFixed(1)}/4`,
              sub: `${Math.round((avgBehavioral / 4) * 100)}% — eye contact, posture, confidence`,
              pct: (avgBehavioral / 4) * 100,
            },
            {
              icon: MessageSquare,
              label: "Correctness",
              value: `${avgCorrectness.toFixed(1)}/6`,
              sub: `${Math.round((avgCorrectness / 6) * 100)}% — answer quality & keywords`,
              pct: (avgCorrectness / 6) * 100,
            },
            {
              icon: Eye,
              label: "Eye Contact",
              value: `${Math.round(avgEyeContact)}%`,
              sub: avgEyeContact >= 70 ? "Strong — kept gaze steady" : "Keep looking at the camera",
              pct: avgEyeContact,
            },
            {
              icon: Mic2,
              label: "Speaking Pace",
              value: `${Math.round(avgWpm)} WPM`,
              sub: `${totalFillers} filler word${totalFillers !== 1 ? "s" : ""} detected${avgWpm > 180 ? " · Try speaking slower" : avgWpm < 100 && avgWpm > 0 ? " · Try speaking a bit faster" : ""}`,
              pct: Math.min((avgWpm / 160) * 100, 100),
            },
          ].map((metric) => (
            <motion.div
              key={metric.label}
              variants={item}
              className="rounded-2xl bg-card text-card-foreground p-6 shadow-soft tilt-card"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="grid place-items-center h-9 w-9 rounded-lg bg-primary/10">
                  <metric.icon className="h-4 w-4 text-primary" />
                </div>
                <div className="font-medium text-sm">{metric.label}</div>
              </div>
              <div className="text-3xl font-bold tabular-nums mb-2">{metric.value}</div>
              <div className="h-1.5 w-full bg-muted rounded-full mb-2 overflow-hidden">
                <motion.div
                  className="h-full rounded-full"
                  style={{ backgroundColor: scoreColor(metric.pct, 100) }}
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(metric.pct, 100)}%` }}
                  transition={{ duration: 1.2, delay: 0.4 }}
                />
              </div>
              <p className="text-xs text-muted-foreground">{metric.sub}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Feedback */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
          {/* Strengths */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="rounded-2xl bg-card text-card-foreground p-6 shadow-soft"
          >
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="h-4 w-4 text-success" />
              <h3 className="font-semibold text-sm">Strengths</h3>
            </div>
            <ul className="space-y-3">
              {displayStrengths.map((s, i) => (
                <motion.li
                  key={i}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.7 + i * 0.1 }}
                  className="flex items-start gap-2.5 text-sm"
                >
                  <CheckCircle2 className="h-4 w-4 text-success shrink-0 mt-0.5" />
                  <span>{s}</span>
                </motion.li>
              ))}
            </ul>
          </motion.div>

          {/* Improvements */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="rounded-2xl bg-card text-card-foreground p-6 shadow-soft"
          >
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="h-4 w-4 text-amber-400" />
              <h3 className="font-semibold text-sm">Areas to Improve</h3>
            </div>
            <ul className="space-y-3">
              {displayImprovements.map((s, i) => (
                <motion.li
                  key={i}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.8 + i * 0.1 }}
                  className="flex items-start gap-2.5 text-sm"
                >
                  <ChevronRight className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
                  <span className="text-muted-foreground">{s}</span>
                </motion.li>
              ))}
            </ul>
          </motion.div>
        </div>

        {/* Per-question breakdown (collapsible) */}
        {displayResults.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
            className="rounded-2xl bg-card text-card-foreground p-6 shadow-soft mb-10"
          >
            <h3 className="font-semibold text-sm mb-4">Per-Question Breakdown</h3>
            <div className="space-y-3">
              {displayResults.map((r, i) => {
                const score = r.videoResult.scores?.final?.score ?? 0;
                const ok = r.videoResult.success;
                return (
                  <div key={i} className="flex items-center justify-between gap-4 py-2 border-b border-border/40 last:border-0">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">Q{i + 1}: {r.question.question}</p>
                      {r.videoResult.transcript && r.videoResult.transcript !== "(skipped)" && (
                        <p className="text-xs text-muted-foreground mt-0.5 truncate">
                          &ldquo;{r.videoResult.transcript.slice(0, 80)}…&rdquo;
                        </p>
                      )}
                    </div>
                    <div
                      className="text-lg font-bold tabular-nums shrink-0"
                      style={{ color: ok ? scoreColor(score) : undefined }}
                    >
                      {ok ? `${score.toFixed(1)}/10` : "—"}
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}

        {/* Action buttons */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.0 }}
          className="flex flex-col sm:flex-row gap-3"
        >
          <Button
            size="lg"
            onClick={handlePracticeAgain}
            className="h-12 flex-1 gap-2 shine shadow-glow"
          >
            <RotateCcw className="h-4 w-4" />
            Practice Another Interview
          </Button>
          <Button
            size="lg"
            variant="outline"
            onClick={() => { reset(); navigate({ to: "/home" }); }}
            className="h-12 flex-1 gap-2"
          >
            <Home className="h-4 w-4" />
            Back to Home
          </Button>
        </motion.div>
      </div>
    </main>
  );
}
