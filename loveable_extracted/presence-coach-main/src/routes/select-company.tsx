import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowRight, Building2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export const Route = createFileRoute("/select-company")({
  component: SelectCompany,
  head: () => ({ meta: [{ title: "Choose company — MockInterviewer" }] }),
});

const COMPANIES = ["Google", "Meta", "Amazon", "Apple", "Microsoft", "Netflix", "Tesla", "OpenAI", "Stripe", "Airbnb"];

function SelectCompany() {
  const navigate = useNavigate();
  const [company, setCompany] = useState<string>("");

  return (
    <main className="min-h-screen grid place-items-center bg-background text-foreground px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-lg"
      >
        <div className="text-center mb-8">
          <div className="mx-auto mb-4 grid place-items-center h-12 w-12 rounded-xl bg-primary/10">
            <Building2 className="h-5 w-5 text-primary" />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Choose a company</h1>
          <p className="mt-2 text-muted-foreground">Which company are you preparing for?</p>
        </div>

        <div className="rounded-2xl bg-card text-card-foreground shadow-elegant p-8">
          <Select value={company} onValueChange={setCompany}>
            <SelectTrigger className="h-12">
              <SelectValue placeholder="Select a company" />
            </SelectTrigger>
            <SelectContent>
              {COMPANIES.map((c) => (
                <SelectItem key={c} value={c}>{c}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Button
            className="w-full h-11 mt-6"
            disabled={!company}
            onClick={() => navigate({ to: "/select-field", search: { company } })}
          >
            Continue <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </motion.div>
    </main>
  );
}
