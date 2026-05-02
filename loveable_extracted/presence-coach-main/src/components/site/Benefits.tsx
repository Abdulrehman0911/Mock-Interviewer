import { motion } from "framer-motion";

const items = [
  { n: "01", t: "Build Real Confidence", d: "Stop guessing if you're ready. See measurable improvement after every session." },
  { n: "02", t: "Reduce Interview Anxiety", d: "Practice until nervous micro-expressions disappear and calm presence takes over." },
  { n: "03", t: "Stand Out to Employers", d: "Candidates with strong eye contact are 3× more likely to advance to the next round." },
  { n: "04", t: "Land Your Dream Job", d: "Walk into every interview knowing you've mastered the non-verbal skills that matter." },
];

export function Benefits() {
  return (
    <section id="benefits" className="py-24 md:py-32">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="max-w-2xl mb-16"
        >
          <div className="text-sm font-medium text-primary mb-3">The outcome</div>
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight">
            See the difference <span className="text-gradient">practice makes.</span>
          </h2>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {items.map((it, i) => (
            <motion.div
              key={it.n}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
              className="group relative rounded-2xl border bg-card p-6 hover:shadow-elegant transition-all tilt-card shine overflow-hidden"
            >
              <div className="absolute -top-12 -right-12 h-32 w-32 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500 animate-aurora"
                style={{ background: "radial-gradient(circle, oklch(0.55 0.10 150 / 0.25), transparent 70%)" }}
              />
              <div className="text-sm font-mono text-primary mb-4 transition-transform group-hover:translate-x-1">{it.n}</div>
              <h3 className="font-semibold text-lg tracking-tight mb-2 text-slate-700">{it.t}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed text-slate-700">{it.d}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
