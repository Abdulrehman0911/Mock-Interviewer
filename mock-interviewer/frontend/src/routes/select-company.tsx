import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Building2, ArrowLeft, CheckCircle2, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/use-auth";
import { useInterviewStore } from "@/store/interviewStore";
import { COMPANIES, ALL_ROLES, type Company } from "@/lib/companies";

export const Route = createFileRoute("/select-company")({
  component: SelectCompany,
});

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06, delayChildren: 0.1 } },
};
const card = {
  hidden: { opacity: 0, y: 20, scale: 0.96 },
  show: { opacity: 1, y: 0, scale: 1 },
};

function SelectCompany() {
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const setCompany = useInterviewStore((s) => s.setCompany);
  const [selected, setSelected] = useState<Company | null>(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    if (!loading && !user) navigate({ to: "/auth", replace: true });
  }, [loading, user, navigate]);

  const filtered = COMPANIES.filter(
    (c) =>
      c.name.toLowerCase().includes(query.toLowerCase()) ||
      c.description.toLowerCase().includes(query.toLowerCase()),
  );

  const handleSelect = (company: Company) => {
    setSelected(company);
    setCompany(company);
    setTimeout(() => navigate({ to: "/select-role" }), 320);
  };

  return (
    <main className="min-h-screen bg-background text-foreground px-4 py-12">
      <div className="pointer-events-none fixed inset-0 -z-10 bg-gradient-mesh opacity-40" />
      <div className="container mx-auto max-w-5xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10"
        >
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate({ to: "/home" })}
            className="mb-6 gap-1.5 text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" /> Back
          </Button>

          <div className="text-center">
            <div className="mx-auto mb-4 grid place-items-center h-14 w-14 rounded-2xl bg-primary/10">
              <Building2 className="h-6 w-6 text-primary" />
            </div>
            <h1 className="text-3xl md:text-4xl font-bold tracking-tight mb-2">
              Choose a company
            </h1>
            <p className="text-muted-foreground">Which company are you preparing for?</p>
          </div>

          <div className="relative max-w-md mx-auto mt-8">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search companies…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </motion.div>

        {/* Company grid */}
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
        >
          {filtered.map((company) => {
            const isSelected = selected?.id === company.id;
            return (
              <motion.button
                key={company.id}
                variants={card}
                whileHover={{ y: -4, scale: 1.02 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => handleSelect(company)}
                className={`relative rounded-2xl p-6 text-left shadow-soft transition-all duration-200 border ${
                  isSelected
                    ? "border-primary/60 shadow-glow bg-primary/5"
                    : "border-transparent bg-card text-card-foreground hover:shadow-elegant hover:border-primary/20"
                }`}
              >
                {isSelected && (
                  <motion.div
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="absolute top-3 right-3"
                  >
                    <CheckCircle2 className="h-5 w-5 text-success" />
                  </motion.div>
                )}

                {/* Logo */}
                <div
                  className="h-12 w-12 rounded-xl flex items-center justify-center text-sm font-bold mb-4 text-white"
                  style={{ backgroundColor: company.color }}
                >
                  {company.initials}
                </div>

                <h3 className="font-semibold mb-1">{company.name}</h3>
                <p className="text-xs text-muted-foreground line-clamp-2 mb-3">
                  {company.description}
                </p>
                <div className="text-xs text-primary/80 font-medium">
                  {ALL_ROLES.length} roles available
                </div>
              </motion.button>
            );
          })}
        </motion.div>

        {filtered.length === 0 && (
          <div className="text-center py-16 text-muted-foreground">
            No companies match &ldquo;{query}&rdquo;
          </div>
        )}
      </div>
    </main>
  );
}
