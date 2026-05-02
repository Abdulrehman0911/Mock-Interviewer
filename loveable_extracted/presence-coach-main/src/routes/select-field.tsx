import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowRight, Briefcase } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export const Route = createFileRoute("/select-field")({
  component: SelectField,
  validateSearch: (search: Record<string, unknown>) => ({
    company: (search.company as string) ?? "",
  }),
  head: () => ({ meta: [{ title: "Choose field — MockInterviewer" }] }),
});

const FIELDS = [
  "Software Engineering",
  "Data Science",
  "Product Management",
  "Machine Learning",
  "Frontend Development",
  "Backend Development",
  "DevOps",
  "Design (UX/UI)",
  "Marketing",
  "Finance",
];

function SelectField() {
  const navigate = useNavigate();
  const { company } = Route.useSearch();
  const [field, setField] = useState<string>("");

  return (
    <main className="min-h-screen grid place-items-center bg-background text-foreground px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-lg"
      >
        <div className="text-center mb-8">
          <div className="mx-auto mb-4 grid place-items-center h-12 w-12 rounded-xl bg-primary/10">
            <Briefcase className="h-5 w-5 text-primary" />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Choose your field</h1>
          <p className="mt-2 text-muted-foreground">
            Preparing for <span className="font-semibold text-foreground">{company || "your interview"}</span> — pick a role.
          </p>
        </div>

        <div className="rounded-2xl bg-card text-card-foreground shadow-elegant p-8">
          <Select value={field} onValueChange={setField}>
            <SelectTrigger className="h-12">
              <SelectValue placeholder="Select a field" />
            </SelectTrigger>
            <SelectContent>
              {FIELDS.map((f) => (
                <SelectItem key={f} value={f}>{f}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="mt-10 flex justify-center">
          <Button
            size="lg"
            className="h-12 px-8"
            disabled={!field}
            onClick={() => navigate({ to: "/interview", search: { company, field } })}
          >
            Start Interview <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </motion.div>
    </main>
  );
}
