import { motion } from "framer-motion";
import { Eye, Radar, Brain, TrendingUp } from "lucide-react";

const features = [
  {
    icon: Eye,
    title: "Eye Contact Tracking",
    desc: "Real-time iris detection measures how often you look at the camera during answers.",
  },
  {
    icon: Radar,
    title: "Real-Time Scanning",
    desc: "Live feedback on filler words, pace, and tone with color-coded confidence alerts.",
  },
  {
    icon: Brain,
    title: "Enhanced Recognition",
    desc: "Analyzes facial micro-expressions to detect nervousness and engagement.",
  },
  {
    icon: TrendingUp,
    title: "Improvement Tips",
    desc: "Personalized, actionable advice after every session to compound your growth.",
  },
];

export function Features() {
  return (
    <section id="features" className="py-24 md:py-32 relative">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5 }}
          className="max-w-2xl mx-auto text-center mb-16"
        >
          <div className="text-sm font-medium text-primary mb-3">We've cracked the code</div>
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight">
            Everything you need to <span className="text-gradient">stand out</span>
          </h2>
          <p className="mt-4 text-muted-foreground text-lg">
            Four signals analyzed in real time, so you walk in knowing exactly how you come across.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
              className="group relative rounded-2xl glass p-6 shadow-soft hover:shadow-elegant transition-all tilt-card shine"
            >
              <div className="absolute -inset-px -z-10 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-gradient-primary blur-2xl" />
              <div className="relative h-11 w-11 mb-5 group-hover:scale-110 transition-transform">
                <div className="absolute inset-0 rounded-xl conic-ring opacity-70 animate-spin-slow" />
                <div className="absolute inset-[2px] rounded-[10px] bg-card grid place-items-center text-card-foreground">
                  <f.icon className="h-5 w-5" />
                </div>
              </div>
              <h3 className="font-semibold text-lg tracking-tight">{f.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground leading-relaxed text-slate-700">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
