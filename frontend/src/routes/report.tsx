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
  if (p >= 70) return "#75D28F"; // Vibrant green
  if (p >= 40) return "#F59E0B"; // Amber
  return "#E6443D"; // Vibrant red
}

function scoreLabel(score: number) {
  if (score >= 8) return "Excellent";
  if (score >= 6) return "Good";
  if (score >= 4) return "Average";
  return "Needs Work";
}

function ScoreRing({ score, outOf = 10 }: { score: number; outOf?: number }) {
  const radius = 80; // Larger
  const circ = 2 * Math.PI * radius;
  const [offset, setOffset] = useState(circ);
  const [displayScore, setDisplayScore] = useState(0);
  const color = scoreColor(score, outOf);

  useEffect(() => {
    const timer = setTimeout(() => {
      const pct = Math.min(score / outOf, 1);
      setOffset(circ - pct * circ);
      
      let start = 0;
      const duration = 1500;
      const step = (timestamp: number) => {
        if (!start) start = timestamp;
        const progress = Math.min((timestamp - start) / duration, 1);
        setDisplayScore(progress * score);
        if (progress < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    }, 300);
    return () => clearTimeout(timer);
  }, [score, outOf, circ]);

  return (
    <div className="relative flex items-center justify-center p-4">
      <svg width="220" height="220" viewBox="0 0 220 220" className="relative z-10 drop-shadow-2xl">
        <defs>
          <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={color} stopOpacity="0.8" />
            <stop offset="100%" stopColor={color} />
          </linearGradient>
        </defs>
        
        {/* Track */}
        <circle 
          cx="110" 
          cy="110" 
          r={radius} 
          fill="none" 
          stroke="white" 
          strokeOpacity="0.05"
          strokeWidth="16" 
        />
        
        {/* Ring */}
        <circle
          cx="110"
          cy="110"
          r={radius}
          fill="none"
          stroke="url(#scoreGradient)"
          strokeWidth="16"
          strokeLinecap="round"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          style={{ 
            transform: "rotate(-90deg)", 
            transformOrigin: "center", 
            transition: "stroke-dashoffset 2.5s cubic-bezier(0.2, 1, 0.3, 1)" 
          }}
        />
      </svg>
      
      {/* Center Display */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="flex flex-col items-center justify-center pt-2">
          <motion.span 
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-7xl font-black tabular-nums tracking-tighter drop-shadow-md"
            style={{ color: "var(--foreground)" }}
          >
            {displayScore.toFixed(1)}
          </motion.span>
          <span className="text-[11px] uppercase font-bold tracking-widest text-foreground/40 mt-1">
            out of {outOf}
          </span>
        </div>
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
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-12">
          <div className="mx-auto mb-6 grid place-items-center h-16 w-16 rounded-[1.25rem] bg-white/5 border border-white/10 shadow-elegant">
            <Trophy className="h-7 w-7 text-primary" />
          </div>
          <h1 className="text-4xl md:text-5xl font-black tracking-tight mb-3 text-foreground">Interview Complete!</h1>
          {(displayCompany || displayRole) && (
            <p className="text-foreground/60 text-lg font-medium">
              {displayRole}{displayCompany ? ` · ${displayCompany}` : ""}
            </p>
          )}
        </motion.div>

        {/* Overall score hero */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="relative overflow-hidden rounded-[2rem] bg-card text-card-foreground p-10 md:p-12 flex flex-col items-center text-center shadow-soft mb-12 border border-white/5 tilt-card"
        >
          {/* Subtle Ambient Glows internal to the card */}
          <div className="absolute top-0 inset-x-0 h-full bg-gradient-to-b from-transparent to-background/60 pointer-events-none" />
          <div className="absolute -top-32 -left-32 w-[30rem] h-[30rem] bg-primary/5 blur-[100px] rounded-full pointer-events-none" />

          <div className="relative z-10 flex flex-col items-center w-full">
            <div className="flex items-center gap-3 text-primary text-sm md:text-base uppercase font-extrabold tracking-[0.2em] mb-12 drop-shadow-sm">
              <span className="text-xl md:text-2xl drop-shadow-md">🏆</span> OVERALL INTERVIEW PERFORMANCE
            </div>
            
            <ScoreRing score={parseFloat(overallScore.toFixed(1))} outOf={10} />
            
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.2 }}
              className="mt-8 text-foreground/80 font-medium text-[15px] max-w-md text-center leading-relaxed"
            >
              {overallScore >= 8 ? "Outstanding performance! You demonstrated exceptional communication and technical depth." :
               overallScore >= 6 ? "Good effort! Solid responses, but there's room to refine your delivery." :
               overallScore >= 4 ? "Average performance. Focus on maintaining eye contact and reducing filler words." :
               "Needs work. Keep practicing to build confidence and articulate your points more clearly."}
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 1.4, type: "spring" }}
              className="mt-8 inline-flex items-center gap-4 px-6 py-3 rounded-full bg-background/60 border border-white/5 shadow-inner"
            >
              <div className="w-2.5 h-2.5 rounded-full animate-pulse shadow-[0_0_8px_currentColor]" style={{ color: scoreColor(overallScore), backgroundColor: "currentColor" }} />
              <span className="text-sm md:text-base font-bold text-foreground tracking-tight">
                {scoreLabel(overallScore)}
              </span>
              <div className="w-px h-4 bg-white/20" />
              <span className="text-sm md:text-base text-foreground/60 font-medium">
                {validResults.length}/{displayResults.length} scored
              </span>
            </motion.div>
          </div>
        </motion.div>

        {/* Score breakdown cards */}
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-12"
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
              className="rounded-[2rem] bg-card text-card-foreground p-8 shadow-soft border border-white/5 tilt-card"
            >
              <div className="flex items-center gap-4 mb-6">
                <div className="grid place-items-center h-12 w-12 rounded-2xl bg-white/5 border border-white/5">
                  <metric.icon className="h-5 w-5 text-primary" />
                </div>
                <div className="font-bold text-base tracking-tight">{metric.label}</div>
              </div>
              <div className="text-4xl font-black tabular-nums mb-4 text-foreground">{metric.value}</div>
              <div className="h-2 w-full bg-white/5 rounded-full mb-4 overflow-hidden">
                <motion.div
                  className="h-full rounded-full"
                  style={{ backgroundColor: scoreColor(metric.pct, 100) }}
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(metric.pct, 100)}%` }}
                  transition={{ duration: 1.5, delay: 0.6, ease: "easeOut" }}
                />
              </div>
              <p className="text-sm text-foreground/50 font-medium leading-relaxed">{metric.sub}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Feedback Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          {/* Strengths */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.4 }}
            className="rounded-[2rem] bg-card text-card-foreground p-8 shadow-soft border border-white/5"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2.5 rounded-xl bg-success/10 border border-success/10">
                <TrendingUp className="h-5 w-5 text-success" />
              </div>
              <h3 className="font-bold text-lg tracking-tight">Strengths</h3>
            </div>
            <ul className="space-y-4">
              {displayStrengths.map((s, i) => (
                <motion.li
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.5 + i * 0.1 }}
                  className="flex items-start gap-3.5 text-base"
                >
                  <div className="mt-1 p-0.5 rounded-full bg-success/20">
                    <CheckCircle2 className="h-3.5 w-3.5 text-success" />
                  </div>
                  <span className="text-foreground/80 font-medium leading-relaxed">{s}</span>
                </motion.li>
              ))}
            </ul>
          </motion.div>

          {/* Improvements */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.4 }}
            className="rounded-[2rem] bg-card text-card-foreground p-8 shadow-soft border border-white/5"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2.5 rounded-xl bg-amber-400/10 border border-amber-400/10">
                <Sparkles className="h-5 w-5 text-amber-400" />
              </div>
              <h3 className="font-bold text-lg tracking-tight">Areas to Improve</h3>
            </div>
            <ul className="space-y-4">
              {displayImprovements.map((s, i) => (
                <motion.li
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.5 + i * 0.1 }}
                  className="flex items-start gap-3.5 text-base"
                >
                  <div className="mt-1 p-0.5 rounded-full bg-amber-400/20">
                    <ChevronRight className="h-3.5 w-3.5 text-amber-400" />
                  </div>
                  <span className="text-foreground/70 font-medium leading-relaxed">{s}</span>
                </motion.li>
              ))}
            </ul>
          </motion.div>
        </div>

        {/* Per-question breakdown */}
        {displayResults.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.8 }}
            className="rounded-[2rem] bg-card text-card-foreground p-10 shadow-soft mb-12 border border-white/5"
          >
            <h3 className="font-bold text-xl mb-8 tracking-tight">Question Analysis</h3>
            <div className="space-y-6">
              {displayResults.map((r, i) => {
                const score = r.videoResult.scores?.final?.score ?? 0;
                const ok = r.videoResult.success;
                return (
                  <div key={i} className="flex items-center justify-between gap-6 py-4 border-b border-white/5 last:border-0 last:pb-0">
                    <div className="flex-1 min-w-0">
                      <p className="text-base font-bold text-foreground/90 truncate mb-1">
                        <span className="text-primary/60 font-black mr-2">Q{i + 1}</span>
                        {r.question.question}
                      </p>
                      {r.videoResult.transcript && r.videoResult.transcript !== "(skipped)" && (
                        <p className="text-sm text-foreground/50 italic truncate">
                          &ldquo;{r.videoResult.transcript.slice(0, 100)}…&rdquo;
                        </p>
                      )}
                    </div>
                    <div
                      className="text-xl font-black tabular-nums shrink-0"
                      style={{ color: ok ? scoreColor(score) : "var(--foreground-50)" }}
                    >
                      {ok ? `${score.toFixed(1)}` : "—"}
                      {ok && <span className="text-xs text-foreground/30 font-bold ml-1">/10</span>}
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}

        {/* Action buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2.0 }}
          className="flex flex-col sm:flex-row gap-4 max-w-2xl mx-auto"
        >
          <Button
            size="lg"
            onClick={handlePracticeAgain}
            className="h-14 flex-1 gap-3 rounded-2xl text-base font-bold shadow-glow hover:scale-[1.02] transition-transform"
          >
            <RotateCcw className="h-5 w-5" />
            Try Another Interview
          </Button>
          <Button
            size="lg"
            variant="outline"
            onClick={() => { reset(); navigate({ to: "/home" }); }}
            className="h-14 flex-1 gap-3 rounded-2xl text-base font-bold hover:bg-white/5"
          >
            <Home className="h-5 w-5" />
            Back to Dashboard
          </Button>
        </motion.div>
      </div>
    </main>
  );
}
