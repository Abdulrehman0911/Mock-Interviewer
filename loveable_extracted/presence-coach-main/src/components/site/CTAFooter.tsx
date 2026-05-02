import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";
import { useNavigate } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";

export function CTAFooter() {
  const navigate = useNavigate();
  return (
    <>
      <section className="py-24 md:py-32">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="relative max-w-4xl mx-auto rounded-3xl overflow-hidden p-10 md:p-16 text-center"
            style={{ background: "var(--gradient-hero)" }}
          >
            <div className="absolute inset-0 opacity-30 bg-gradient-mesh text-slate-200" />
            <div className="relative">
              <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-primary-foreground">
                Ready to improve?
              </h2>
              <p className="mt-4 text-primary-foreground/80 max-w-xl mx-auto text-[#e2dada]">
                Try the demo and share your thoughts — your feedback shapes what comes next.
              </p>
              <div className="mt-8">
                <Button size="lg" onClick={() => navigate({ to: "/select-company" })} className="h-12 px-8 bg-background text-foreground hover:bg-background/90 group">
                  Start Practicing
                  <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Button>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      <footer className="border-t py-10">
        <div className="container mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <span className="grid place-items-center h-7 w-7 rounded-md bg-primary text-primary-foreground">
              <Sparkles className="h-3.5 w-3.5" />
            </span>
            <span className="font-semibold text-foreground">MockInterviewer</span>
            <span>© {new Date().getFullYear()}</span>
          </div>
          <div className="flex gap-6">
            <a href="#" className="hover:text-foreground">Privacy</a>
            <a href="#" className="hover:text-foreground">Terms</a>
            <a href="#" className="hover:text-foreground">Contact</a>
          </div>
        </div>
      </footer>
    </>
  );
}
