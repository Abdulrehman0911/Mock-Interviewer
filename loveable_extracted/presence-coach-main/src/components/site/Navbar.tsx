import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, Moon, Sun, Sparkles, LogOut } from "lucide-react";
import { useNavigate } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/use-auth";

export function Navbar() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate({ to: "/auth" });
  };
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  const links = [
    { href: "#features", label: "Features" },
    { href: "#practice", label: "Practice" },
    { href: "#benefits", label: "Benefits" },
    { href: "#demo", label: "Demo" },
  ];

  return (
    <header
      className={`fixed top-0 inset-x-0 z-50 transition-all duration-300 ${
        scrolled ? "py-2" : "py-4"
      }`}
    >
      <div className="container mx-auto px-4">
        <nav
          className={`mx-auto max-w-6xl flex items-center justify-between rounded-2xl px-4 sm:px-6 py-3 transition-all ${
            scrolled ? "glass shadow-soft" : "bg-transparent"
          }`}
        >
          <a href="#" className="flex items-center gap-2 font-semibold">
            <span className="grid place-items-center h-8 w-8 rounded-lg bg-primary text-primary-foreground shadow-elegant">
              <Sparkles className="h-4 w-4" />
            </span>
            <span className="tracking-tight">MockInterviewer</span>
          </a>

          <div className="hidden md:flex items-center gap-8 text-sm text-muted-foreground">
            {links.map((l) => (
              <a key={l.href} href={l.href} className="hover:text-foreground transition-colors">
                {l.label}
              </a>
            ))}
          </div>

          <div className="hidden md:flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setDark((d) => !d)}
              aria-label="Toggle theme"
            >
              {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            {user ? (
              <Button variant="ghost" size="sm" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-1.5" /> Logout
              </Button>
            ) : (
              <Button variant="ghost" size="sm" onClick={() => navigate({ to: "/auth" })}>Login</Button>
            )}
            <Button
              size="sm"
              onClick={() => navigate({ to: "/select-company" })}
              className="bg-gradient-primary text-primary-foreground hover:opacity-90 shadow-elegant"
            >
              Start Interview
            </Button>
          </div>

          <button
            className="md:hidden p-2 rounded-lg hover:bg-muted"
            onClick={() => setOpen((o) => !o)}
            aria-label="Toggle menu"
          >
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </nav>

        <AnimatePresence>
          {open && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="md:hidden mx-auto max-w-6xl mt-2 glass rounded-2xl p-4 shadow-soft"
            >
              <div className="flex flex-col gap-3">
                {links.map((l) => (
                  <a
                    key={l.href}
                    href={l.href}
                    onClick={() => setOpen(false)}
                    className="py-2 text-sm text-muted-foreground hover:text-foreground"
                  >
                    {l.label}
                  </a>
                ))}
                <div className="flex gap-2 pt-2 border-t">
                  {user ? (
                    <Button variant="outline" size="sm" className="flex-1" onClick={handleLogout}>Logout</Button>
                  ) : (
                    <Button variant="outline" size="sm" className="flex-1" onClick={() => navigate({ to: "/auth" })}>Login</Button>
                  )}
                  <Button size="sm" className="flex-1 bg-gradient-primary text-primary-foreground" onClick={() => navigate({ to: "/select-company" })}>
                    Start Interview
                  </Button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </header>
  );
}
