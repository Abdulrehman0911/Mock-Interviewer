import { motion } from "framer-motion";
import { ArrowRight, Play, Sparkles, Eye } from "lucide-react";
import { useNavigate } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { useReveal } from "@/hooks/use-reveal";
import { useCountUp } from "@/hooks/use-count-up";

function Stat({ value, suffix, label, decimals = 0 }: { value: number; suffix?: string; label: string; decimals?: number }) {
  const { ref, visible } = useReveal<HTMLDivElement>(0.4);
  const v = useCountUp(value, 1600, visible);
  return (
    <div ref={ref} className="text-center">
      <div className="text-2xl md:text-3xl font-bold tracking-tight tabular-nums">
        {decimals ? v.toFixed(decimals) : Math.round(v).toLocaleString()}
        {suffix}
      </div>
      <div className="text-xs md:text-sm text-muted-foreground mt-1 text-slate-600">{label}</div>
    </div>
  );
}

export function Hero() {
  const navigate = useNavigate();
  return (
    <section className="relative pt-32 pb-24 md:pt-40 md:pb-32 overflow-hidden">
      {/* Soft beige glow behind headline */}
      <div
        className="pointer-events-none absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 -z-10 h-[40rem] w-[40rem] rounded-full"
        style={{
          background: "radial-gradient(circle, oklch(0.88 0.04 80 / 0.08), transparent 70%)",
        }}
      />

      {/* Animated grid pattern */}
      <div
        className="pointer-events-none absolute inset-0 -z-10 opacity-[0.05]"
        style={{
          backgroundImage:
            "linear-gradient(oklch(0.88 0.04 80) 1px, transparent 1px), linear-gradient(90deg, oklch(0.88 0.04 80) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
          animation: "grid-pan 30s linear infinite",
          maskImage: "radial-gradient(ellipse at center, black 40%, transparent 80%)",
          WebkitMaskImage: "radial-gradient(ellipse at center, black 40%, transparent 80%)",
        }}
      />

      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 rounded-full border bg-background/40 backdrop-blur px-4 py-1.5 text-xs font-medium text-muted-foreground mb-6"
          >
            <Sparkles className="h-3.5 w-3.5 text-primary" />
            AI-powered mock interviews
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.1, ease: "easeOut" }}
            className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight leading-[1.08]"
          >
            Master Presence. <span className="text-gradient text-[#ccc7c7]">Command Confidence.</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.25 }}
            className="mt-6 text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto text-slate-600"
          >
            Practice interviews with real-time eye-contact tracking, filler-word detection,
            and AI feedback engineered to make you unforgettable.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.35 }}
            className="mt-10 flex flex-col sm:flex-row gap-3 justify-center"
          >
            <Button
              size="lg"
              onClick={() => navigate({ to: "/select-company" })}
              className="bg-primary text-primary-foreground hover:bg-primary-glow shadow-elegant h-12 px-7 text-base group transition-all duration-300 hover:scale-105 hover:shadow-glow"
            >
              Start Interview
              <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="h-12 px-7 text-base backdrop-blur bg-background/40 border-foreground/20 hover:bg-background/60 transition-all duration-300 hover:scale-105"
            >
              <Play className="mr-2 h-4 w-4" /> Watch Demo
            </Button>
          </motion.div>

          {/* Eye Contact card */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.55 }}
            whileHover={{ y: -4, scale: 1.03 }}
            className="mt-12 mx-auto inline-flex items-center gap-4 rounded-2xl bg-card text-card-foreground shadow-elegant px-5 py-3 shine"
          >
            <div className="relative h-14 w-14">
              {/* Rotating conic ring */}
              <div className="absolute inset-0 rounded-full conic-ring animate-spin-slow opacity-80" />
              <div className="absolute inset-[3px] rounded-full bg-card" />
              <svg viewBox="0 0 36 36" className="absolute inset-[3px] -rotate-90">
                <circle cx="18" cy="18" r="15" fill="none" stroke="currentColor" strokeOpacity="0.12" strokeWidth="3" />
                <motion.circle
                  cx="18" cy="18" r="15" fill="none"
                  stroke="oklch(0.45 0.10 150)" strokeWidth="3" strokeLinecap="round"
                  strokeDasharray={2 * Math.PI * 15}
                  initial={{ strokeDashoffset: 2 * Math.PI * 15 }}
                  animate={{ strokeDashoffset: 2 * Math.PI * 15 * 0.13 }}
                  transition={{ duration: 1.4, delay: 0.8, ease: "easeOut" }}
                />
              </svg>
              <div className="absolute inset-0 grid place-items-center">
                <Eye className="h-4 w-4" style={{ color: "oklch(0.30 0.06 145)" }} />
              </div>
            </div>
            <div className="text-left">
              <div className="text-xs uppercase tracking-wider opacity-60">Eye Contact</div>
              <div className="text-2xl font-bold tabular-nums" style={{ color: "oklch(0.30 0.08 150)" }}>87%</div>
            </div>
          </motion.div>

          {/* Stats strip */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.7 }}
            className="mt-14 grid grid-cols-2 md:grid-cols-4 gap-6 max-w-3xl mx-auto"
          >
            <Stat value={50} suffix="k+" label="Sessions" />
            <Stat value={92} suffix="%" label="Confidence boost" />
            <Stat value={3.4} suffix="x" label="More callbacks" decimals={1} />
            <Stat value={4.9} suffix="★" label="User rating" decimals={1} />
          </motion.div>
        </div>
      </div>
    </section>
  );
}
