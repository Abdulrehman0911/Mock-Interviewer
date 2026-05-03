import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  Play,
  Trophy,
  TrendingUp,
  BarChart3,
  ChevronRight,
  LogOut,
  Calendar,
  Star,
  User,
  Mail,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";
import { useInterviewStore, type PastInterview } from "@/store/interviewStore";
import { signOut } from "firebase/auth";
import { auth } from "@/integrations/firebase/client";
import { toast } from "sonner";

export const Route = createFileRoute("/home")({
  component: HomePage,
});

function scoreColor(score: number) {
  if (score >= 7) return "text-success";
  if (score >= 4) return "text-amber-400";
  return "text-destructive";
}

function difficultyLabel(score: number) {
  if (score >= 8) return "Excellent";
  if (score >= 6) return "Good";
  if (score >= 4) return "Average";
  return "Needs Work";
}

function HomePage() {
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const pastInterviews = useInterviewStore((s) => s.pastInterviews);
  const [showProfile, setShowProfile] = useState(false);

  useEffect(() => {
    if (!loading && !user) navigate({ to: "/auth", replace: true });
  }, [loading, user, navigate]);

  const avgScore =
    pastInterviews.length > 0
      ? pastInterviews.reduce((sum, i) => sum + i.overallScore, 0) / pastInterviews.length
      : null;
  const bestScore =
    pastInterviews.length > 0
      ? Math.max(...pastInterviews.map((i) => i.overallScore))
      : null;

  const handleLogout = async () => {
    await signOut(auth);
    toast.success("Signed out successfully.");
    navigate({ to: "/auth", replace: true });
  };

  const container = {
    hidden: {},
    show: { transition: { staggerChildren: 0.1, delayChildren: 0.2 } },
  };
  const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="pointer-events-none fixed inset-0 -z-10 bg-gradient-mesh opacity-50" />

      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur-md">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <button
            onClick={() => setShowProfile(true)}
            className="flex items-center gap-2.5 hover:opacity-80 transition-opacity"
          >
            <span className="grid place-items-center h-9 w-9 rounded-xl bg-primary text-primary-foreground shadow-elegant">
              <Sparkles className="h-4 w-4" />
            </span>
            <span className="font-bold tracking-tight text-lg">MockMate</span>
          </button>
          <div className="flex items-center gap-3">
            <span className="hidden sm:block text-sm text-muted-foreground truncate max-w-48">
              {user?.email}
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="h-9 gap-1.5 text-muted-foreground hover:text-foreground"
            >
              <LogOut className="h-4 w-4" />
              <span className="hidden sm:inline">Sign out</span>
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-12 max-w-5xl">
        {/* Hero CTA */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.1, duration: 0.5 }}
            className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-sm text-primary mb-6"
          >
            <Sparkles className="h-3.5 w-3.5" />
            AI-Powered Interview Coach
          </motion.div>
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-4">
            Ready to ace your{" "}
            <span className="text-gradient">next interview?</span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-xl mx-auto mb-10">
            Practice with real questions, get instant AI feedback on your behavior,
            correctness, eye contact, and speaking pace.
          </p>

          <motion.div
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.97 }}
            className="inline-block"
          >
            <Button
              size="lg"
              onClick={() => navigate({ to: "/select-company" })}
              className="h-14 px-10 text-lg font-semibold shadow-glow shine gap-3"
            >
              <Play className="h-5 w-5 fill-current" />
              Start Interview
            </Button>
          </motion.div>
        </motion.div>

        {/* Stats */}
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-12"
        >
          {[
            {
              icon: BarChart3,
              label: "Total Interviews",
              value: pastInterviews.length.toString(),
              sub: "sessions completed",
            },
            {
              icon: TrendingUp,
              label: "Average Score",
              value: avgScore !== null ? `${avgScore.toFixed(1)}/10` : "—",
              sub: avgScore !== null ? difficultyLabel(avgScore) : "No sessions yet",
            },
            {
              icon: Trophy,
              label: "Best Score",
              value: bestScore !== null ? `${bestScore.toFixed(1)}/10` : "—",
              sub: bestScore !== null ? difficultyLabel(bestScore) : "Keep practicing!",
            },
          ].map((stat) => (
            <motion.div
              key={stat.label}
              variants={item}
              className="rounded-2xl bg-card text-card-foreground p-6 shadow-elegant tilt-card"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="grid place-items-center h-10 w-10 rounded-xl bg-primary/10">
                  <stat.icon className="h-5 w-5 text-primary" />
                </div>
              </div>
              <div className="text-3xl font-bold tabular-nums mb-1">{stat.value}</div>
              <div className="text-sm font-medium">{stat.label}</div>
              <div className="text-xs text-muted-foreground mt-0.5">{stat.sub}</div>
            </motion.div>
          ))}
        </motion.div>

        {/* Past interviews */}
        {pastInterviews.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Star className="h-5 w-5 text-primary" />
              Recent Interviews
            </h2>
            <div className="space-y-3">
              {pastInterviews.slice(0, 5).map((interview, i) => (
                <PastInterviewCard key={interview.id} interview={interview} index={i} />
              ))}
            </div>
          </motion.div>
        )}

        {pastInterviews.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="text-center py-16 rounded-2xl border border-dashed border-border/60"
          >
            <Trophy className="h-12 w-12 text-primary/30 mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">No interviews yet</h3>
            <p className="text-sm text-muted-foreground">
              Complete your first mock interview to see results here.
            </p>
          </motion.div>
        )}
      </div>

      {/* Profile modal */}
      <AnimatePresence>
        {showProfile && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowProfile(false)}
              className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -10 }}
              transition={{ duration: 0.2 }}
              className="fixed top-20 left-1/2 -translate-x-1/2 z-50 w-full max-w-sm"
            >
              <div className="rounded-2xl bg-card border border-border/60 shadow-elegant p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="font-semibold text-lg">Profile</h2>
                  <button
                    onClick={() => setShowProfile(false)}
                    className="grid place-items-center h-8 w-8 rounded-lg hover:bg-muted transition-colors"
                  >
                    <X className="h-4 w-4 text-muted-foreground" />
                  </button>
                </div>

                {/* Avatar */}
                <div className="flex flex-col items-center mb-6">
                  <div className="grid place-items-center h-20 w-20 rounded-full bg-primary/10 mb-3">
                    <User className="h-10 w-10 text-primary" />
                  </div>
                  <p className="font-medium">{user?.displayName ?? "MockMate User"}</p>
                </div>

                {/* Info rows */}
                <div className="space-y-3 mb-6">
                  <div className="flex items-center gap-3 rounded-xl bg-muted/40 px-4 py-3">
                    <Mail className="h-4 w-4 text-muted-foreground shrink-0" />
                    <span className="text-sm truncate">{user?.email}</span>
                  </div>
                  <div className="flex items-center gap-3 rounded-xl bg-muted/40 px-4 py-3">
                    <Trophy className="h-4 w-4 text-muted-foreground shrink-0" />
                    <span className="text-sm">{pastInterviews.length} interview{pastInterviews.length !== 1 ? "s" : ""} completed</span>
                  </div>
                  {user?.metadata?.creationTime && (
                    <div className="flex items-center gap-3 rounded-xl bg-muted/40 px-4 py-3">
                      <Calendar className="h-4 w-4 text-muted-foreground shrink-0" />
                      <span className="text-sm">
                        Joined {new Date(user.metadata.creationTime).toLocaleDateString("en-US", { month: "long", year: "numeric" })}
                      </span>
                    </div>
                  )}
                </div>

                <Button
                  variant="outline"
                  className="w-full gap-2 text-destructive border-destructive/30 hover:bg-destructive/10"
                  onClick={async () => { await signOut(auth); toast.success("Signed out."); navigate({ to: "/auth", replace: true }); }}
                >
                  <LogOut className="h-4 w-4" />
                  Sign out
                </Button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </main>
  );
}

function PastInterviewCard({ interview, index }: { interview: PastInterview; index: number }) {
  const navigate = useNavigate();
  return (
    <motion.div
      initial={{ opacity: 0, x: -16 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.05 * index }}
      whileHover={{ x: 4 }}
      onClick={() =>
        navigate({
          to: "/report",
          search: { company: interview.company, role: interview.role, pastId: interview.id },
        })
      }
      className="flex items-center justify-between rounded-xl bg-card text-card-foreground p-4 shadow-soft cursor-pointer hover:shadow-elegant transition-all duration-200 group"
    >
      <div className="flex items-center gap-4">
        <div className="grid place-items-center h-10 w-10 rounded-lg bg-primary/10 shrink-0">
          <Trophy className="h-5 w-5 text-primary" />
        </div>
        <div>
          <div className="font-medium text-sm">{interview.role}</div>
          <div className="text-xs text-muted-foreground flex items-center gap-1.5 mt-0.5">
            <Calendar className="h-3 w-3" />
            {interview.company} · {new Date(interview.date).toLocaleDateString()}
          </div>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <div className={`text-xl font-bold tabular-nums ${scoreColor(interview.overallScore)}`}>
          {interview.overallScore.toFixed(1)}
        </div>
        <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" />
      </div>
    </motion.div>
  );
}
