import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Eye, Activity } from "lucide-react";

export function Demo() {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState({ x: 50, y: 50 });
  const [score, setScore] = useState(78);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const t = setTimeout(() => setLoading(false), 1800);
    return () => clearTimeout(t);
  }, []);

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      const el = wrapRef.current;
      if (!el) return;
      const r = el.getBoundingClientRect();
      const x = ((e.clientX - r.left) / r.width) * 100;
      const y = ((e.clientY - r.top) / r.height) * 100;
      if (x < 0 || y < 0 || x > 100 || y > 100) return;
      setPos({ x: Math.max(15, Math.min(85, x)), y: Math.max(20, Math.min(80, y)) });
      const dist = Math.hypot(x - 50, y - 50);
      setScore(Math.max(40, Math.min(99, Math.round(100 - dist))));
    };
    window.addEventListener("mousemove", onMove);
    return () => window.removeEventListener("mousemove", onMove);
  }, []);

  return (
    <section id="demo" className="py-24 md:py-32 bg-muted/40">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="max-w-2xl mx-auto text-center mb-12"
        >
          <div className="text-sm font-medium text-primary mb-3">Live demo</div>
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight">
            Try the <span className="text-gradient text-[#2d6902]">tracker.</span>
          </h2>
          <p className="mt-4 text-muted-foreground text-lg">
            Move your cursor — that's how our eye-tracking maps your gaze in real time.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="max-w-5xl mx-auto grid lg:grid-cols-[1.4fr,1fr] gap-5"
        >
          {/* Camera area */}
          <div
            ref={wrapRef}
            className="relative aspect-video rounded-3xl glass shadow-elegant overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-mesh opacity-60" />
            <div className="absolute top-4 left-4 flex items-center gap-2 text-xs font-medium px-3 py-1.5 rounded-full bg-background/80 backdrop-blur">
              <span className="relative flex h-2 w-2">
                <span className="absolute h-full w-full rounded-full bg-destructive opacity-75" style={{ animation: "pulse-dot 1.6s ease-in-out infinite" }} />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-destructive" />
              </span>
              REC
            </div>
            <div className="absolute top-4 right-4 px-3 py-1.5 rounded-full bg-background/80 backdrop-blur text-xs font-medium">
              Eye Contact: <span className="text-success font-bold">{score}%</span>
            </div>

            {/* Face silhouette */}
            <div className="absolute inset-0 grid place-items-center">
              <div className="relative h-56 w-44 rounded-full bg-foreground/5 border-2 border-dashed border-foreground/20" />
            </div>

            {/* Gaze dot */}
            <motion.div
              animate={{ left: `${pos.x}%`, top: `${pos.y}%` }}
              transition={{ type: "spring", stiffness: 120, damping: 18 }}
              className="absolute h-6 w-6 -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary shadow-glow"
            >
              <div className="absolute inset-0 rounded-full bg-primary" style={{ animation: "pulse-dot 1.6s ease-in-out infinite" }} />
            </motion.div>
          </div>

          {/* Feedback panel */}
          <div className="rounded-3xl glass shadow-elegant p-6 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold tracking-tight">Feedback Report</h3>
              <Activity className="lucide lucide-activity h-4 w-4 text-primary text-slate-500" />
            </div>

            {loading ? (
              <div className="space-y-3 flex-1">
                <SkeletonRow />
                <SkeletonRow />
                <SkeletonRow />
                <SkeletonRow />
              </div>
            ) : (
              <div className="space-y-4 flex-1">
                <div>
                  <div className="flex justify-between text-sm mb-1.5">
                    <span className="text-muted-foreground text-slate-500">Overall Score</span>
                    <span className="font-semibold">{score}/100</span>
                  </div>
                  <div className="h-2 rounded-full bg-muted overflow-hidden">
                    <motion.div
                      animate={{ width: `${score}%` }}
                      className="h-full bg-gradient-primary"
                    />
                  </div>
                </div>
                <Stat label="Eye Contact" value={`${score}%`} icon={Eye} />
                <Stat label="Filler Words" value="2 detected" />
                <Stat label="Confidence" value="High" tone="success" />
                <div className="pt-3 border-t text-slate-600">
                  <div className="text-xs font-medium text-muted-foreground mb-2 text-slate-500">Tips</div>
                  <ul className="text-sm space-y-1.5 text-muted-foreground text-slate-500">
                    <li className="text-slate-500">• Slow down on the second answer</li>
                    <li className="text-slate-500">• Smile during the opener</li>
                    <li className="text-slate-500">• Reduce "um" before key claims</li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function SkeletonRow() {
  return (
    <div className="space-y-2">
      <div className="h-3 w-1/3 rounded bg-muted overflow-hidden relative">
        <div className="absolute inset-0" style={{ background: "linear-gradient(90deg, transparent, oklch(1 0 0 / 0.5), transparent)", backgroundSize: "1000px 100%", animation: "shimmer 2s linear infinite" }} />
      </div>
      <div className="h-8 rounded bg-muted overflow-hidden relative">
        <div className="absolute inset-0" style={{ background: "linear-gradient(90deg, transparent, oklch(1 0 0 / 0.5), transparent)", backgroundSize: "1000px 100%", animation: "shimmer 2s linear infinite" }} />
      </div>
    </div>
  );
}

function Stat({ label, value, icon: Icon, tone }: { label: string; value: string; icon?: typeof Eye; tone?: "success" }) {
  return (
    <div className="flex items-center justify-between text-sm text-slate-500">
      <span className="text-muted-foreground flex items-center gap-2 text-slate-500">
        {Icon && <Icon className="h-3.5 w-3.5" />} {label}
      </span>
      <span className={`font-semibold ${tone === "success" ? "text-success" : ""}`}>{value}</span>
    </div>
  );
}
