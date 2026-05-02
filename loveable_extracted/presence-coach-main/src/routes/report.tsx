import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { Eye, MessageSquare, Smile, Gauge, Trophy, Home } from "lucide-react";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/report")({
  component: Report,
  validateSearch: (search: Record<string, unknown>) => ({
    company: (search.company as string) ?? "",
    field: (search.field as string) ?? "",
  }),
  head: () => ({ meta: [{ title: "Your Report — MockInterviewer" }] }),
});

const METRICS = [
  { icon: Eye, label: "Eye Contact", value: 87, suffix: "%", note: "Strong — kept gaze steady most of the time." },
  { icon: MessageSquare, label: "Filler Words", value: 12, suffix: "", note: "Watch for 'um' and 'like'." },
  { icon: Smile, label: "Confidence", value: 82, suffix: "%", note: "Composed and assured tone." },
  { icon: Gauge, label: "Pace (wpm)", value: 142, suffix: "", note: "Comfortable, easy to follow." },
];

function Report() {
  const navigate = useNavigate();
  const { company, field } = Route.useSearch();
  const overall = 86;

  return (
    <main className="min-h-screen bg-background text-foreground py-12 px-4">
      <div className="container mx-auto max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-10"
        >
          <div className="mx-auto mb-4 grid place-items-center h-14 w-14 rounded-2xl bg-primary/10">
            <Trophy className="h-6 w-6 text-primary" />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Your Interview Report</h1>
          {(company || field) && (
            <p className="mt-2 text-muted-foreground">
              {field}{company ? ` · ${company}` : ""}
            </p>
          )}
        </motion.div>

        {/* Overall score card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="rounded-3xl p-10 text-center shadow-elegant mb-8"
          style={{ background: "var(--gradient-hero)" }}
        >
          <div className="text-primary-foreground/80 text-sm uppercase tracking-wider">Overall Score</div>
          <div className="text-6xl md:text-7xl font-bold text-primary-foreground tabular-nums mt-2">{overall}</div>
          <div className="text-primary-foreground/80 mt-2">Great session — keep it up.</div>
        </motion.div>

        {/* Metrics grid */}
        <div className="grid sm:grid-cols-2 gap-4 mb-10">
          {METRICS.map((m, i) => (
            <motion.div
              key={m.label}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 + i * 0.07 }}
              className="rounded-2xl bg-card text-card-foreground p-6 shadow-soft"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="grid place-items-center h-9 w-9 rounded-lg bg-primary/10">
                  <m.icon className="h-4 w-4 text-primary" />
                </div>
                <div className="font-medium">{m.label}</div>
              </div>
              <div className="text-3xl font-bold tabular-nums">
                {m.value}{m.suffix}
              </div>
              <p className="mt-2 text-sm text-muted-foreground">{m.note}</p>
            </motion.div>
          ))}
        </div>

        <div className="flex justify-center">
          <Button size="lg" onClick={() => navigate({ to: "/home" })} className="h-12 px-8">
            <Home className="mr-2 h-4 w-4" /> Go back to home page
          </Button>
        </div>
      </div>
    </main>
  );
}
