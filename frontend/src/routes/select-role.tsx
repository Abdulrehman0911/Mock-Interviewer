import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BriefcaseBusiness, ArrowLeft, CheckCircle2, ChevronRight, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";
import { useInterviewStore } from "@/store/interviewStore";
import { getRoles, getQuestions } from "@/lib/api";
import { ALL_ROLES } from "@/lib/companies";

export const Route = createFileRoute("/select-role")({
  component: SelectRole,
});

function SelectRole() {
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const company = useInterviewStore((s) => s.company);
  const setRole = useInterviewStore((s) => s.setRole);
  const setQuestions = useInterviewStore((s) => s.setQuestions);

  const [fetchingRoles, setFetchingRoles] = useState(true);
  const [selected, setSelected] = useState<string | null>(null);
  const [loadingRole, setLoadingRole] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && !user) navigate({ to: "/auth", replace: true });
    if (!company) navigate({ to: "/select-company", replace: true });
  }, [loading, user, company, navigate]);

  useEffect(() => {
    getRoles()
      .catch(() => {})
      .finally(() => setFetchingRoles(false));
  }, []);

  const displayRoles = fetchingRoles ? [] : ALL_ROLES;

  const handleSelect = async (role: string) => {
    setSelected(role);
    setLoadingRole(role);
    setRole(role);
    try {
      const questions = await getQuestions(role, 5);
      setQuestions(questions);
      navigate({ to: "/interview" });
    } catch (err) {
      console.debug("[MockMate] API unavailable, using offline fallback questions for", role, err);
      const fallbackQuestions: Record<string, string[]> = {
        "Software Engineer": [
          "Tell me about a challenging technical problem you solved recently.",
          "How do you approach code reviews and ensure code quality?",
          "Describe your experience with system design and architecture.",
          "How do you handle technical debt in a fast-paced environment?",
          "Walk me through your debugging process when facing a critical bug in production.",
        ],
        "Data Scientist": [
          "Describe a machine learning project you've worked on end-to-end.",
          "How do you handle missing data and outliers in a dataset?",
          "Explain the bias-variance tradeoff in your own words.",
          "How do you communicate complex analytical findings to non-technical stakeholders?",
          "What techniques do you use to prevent overfitting in ML models?",
        ],
        "Product Manager": [
          "How do you prioritize features when resources are limited?",
          "Describe a time you had to say no to a stakeholder request.",
          "How do you measure the success of a product feature?",
          "Walk me through how you would define the roadmap for a new product.",
          "How do you balance user needs with business goals?",
        ],
        "Frontend Developer": [
          "How do you optimize a React application for performance?",
          "Explain how you approach responsive and accessible UI design.",
          "Describe your experience with state management solutions.",
          "How do you handle cross-browser compatibility issues?",
          "Walk me through your approach to testing frontend components.",
        ],
        "Backend Developer": [
          "How do you design a RESTful API for scalability?",
          "Describe your experience with database optimization and indexing.",
          "How do you handle authentication and authorization in a backend system?",
          "Explain how you approach microservices vs monolithic architecture.",
          "How do you ensure your backend services are resilient to failures?",
        ],
      };
      const roleQs = fallbackQuestions[role] ?? [
        `Tell me about your background in ${role}.`,
        `What are the most important skills for a ${role}?`,
        `Describe a challenging project you worked on as a ${role}.`,
        `How do you stay up-to-date with trends in ${role}?`,
        `Where do you see yourself growing as a ${role} in the next 2 years?`,
      ];
      const fallback = roleQs.map((q, i) => ({
        question_id: i + 1,
        question: q,
        difficulty: "medium" as const,
      }));
      setQuestions(fallback);
      navigate({ to: "/interview" });
    } finally {
      setLoadingRole(null);
    }
  };

  return (
    <main className="min-h-screen bg-background text-foreground px-4 py-12">
      <div className="pointer-events-none fixed inset-0 -z-10 bg-gradient-mesh opacity-40" />
      <div className="container mx-auto max-w-2xl">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate({ to: "/select-company" })}
            className="mb-6 gap-1.5 text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" /> Back
          </Button>

          <div className="text-center">
            <div className="mx-auto mb-4 grid place-items-center h-14 w-14 rounded-2xl bg-primary/10">
              <BriefcaseBusiness className="h-6 w-6 text-primary" />
            </div>
            <h1 className="text-3xl md:text-4xl font-bold tracking-tight mb-2">
              Select a role
            </h1>
            {company && (
              <p className="text-muted-foreground">
                Preparing for{" "}
                <span className="font-medium text-foreground">{company.name}</span>
              </p>
            )}
          </div>
        </motion.div>

        {fetchingRoles ? (
          <div className="flex justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : (
          <motion.div
            initial="hidden"
            animate="show"
            variants={{ hidden: {}, show: { transition: { staggerChildren: 0.08 } } }}
            className="space-y-3"
          >
            {displayRoles.map((role) => {
              const isSelected = selected === role;
              const isLoading = loadingRole === role;

              return (
                <motion.button
                  key={role}
                  variants={{ hidden: { opacity: 0, x: -16 }, show: { opacity: 1, x: 0 } }}
                  whileHover={{ x: 4 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleSelect(role)}
                  disabled={!!loadingRole}
                  className={`w-full flex items-center justify-between rounded-xl p-5 text-left transition-all duration-200 border ${
                    isSelected
                      ? "border-primary/60 bg-primary/5 shadow-glow"
                      : "border-border/60 bg-card text-card-foreground hover:border-primary/30 hover:shadow-elegant"
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <div className="grid place-items-center h-10 w-10 rounded-lg bg-muted shrink-0">
                      <BriefcaseBusiness className="h-5 w-5 text-muted-foreground" />
                    </div>
                    <div>
                      <div className="font-medium">{role}</div>
                      <div className="text-xs text-muted-foreground mt-0.5">5 questions · 15–20 min</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {isLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin text-primary" />
                    ) : isSelected ? (
                      <CheckCircle2 className="h-5 w-5 text-success" />
                    ) : (
                      <ChevronRight className="h-4 w-4 text-muted-foreground" />
                    )}
                  </div>
                </motion.button>
              );
            })}
          </motion.div>
        )}
      </div>
    </main>
  );
}
