import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { Navbar } from "@/components/site/Navbar";
import { Hero } from "@/components/site/Hero";
import { Features } from "@/components/site/Features";
import { PracticePanel } from "@/components/site/PracticePanel";
import { Benefits } from "@/components/site/Benefits";
import { Demo } from "@/components/site/Demo";
import { CTAFooter } from "@/components/site/CTAFooter";
import { CursorGlow } from "@/components/site/CursorGlow";
import { Marquee } from "@/components/site/Marquee";
import { useAuth } from "@/hooks/use-auth";

export const Route = createFileRoute("/home")({
  component: Home,
  head: () => ({
    meta: [
      { title: "MockInterviewer — Command Confidence in Every Interview" },
      { name: "description", content: "AI mock interviews with real-time eye contact tracking, filler-word detection, and personalized feedback." },
    ],
  }),
});

function Home() {
  const navigate = useNavigate();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (!loading && !user) navigate({ to: "/auth" });
  }, [loading, user, navigate]);

  return (
    <main className="min-h-screen bg-background text-foreground">
      <CursorGlow />
      <Navbar />
      <Hero />
      <Marquee />
      <Features />
      <PracticePanel />
      <Benefits />
      <Demo />
      <CTAFooter />
    </main>
  );
}
