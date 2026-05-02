import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Upload, FileText, Loader2, ArrowRight, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/use-auth";
import { toast } from "sonner";

export const Route = createFileRoute("/upload-cv")({
  component: UploadCV,
  head: () => ({ meta: [{ title: "Upload your CV — MockInterviewer" }] }),
});

function UploadCV() {
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!loading && !user) navigate({ to: "/auth" });
  }, [loading, user, navigate]);

  const handleUpload = async () => {
    if (!file || !user) return;
    setBusy(true);
    try {
      const ext = file.name.split(".").pop() ?? "pdf";
      const path = `${user.id}/cv-${Date.now()}.${ext}`;
      const { error } = await supabase.storage.from("cvs").upload(path, file, { upsert: true });
      if (error) throw error;
      setDone(true);
      toast.success("CV uploaded successfully!");
      setTimeout(() => navigate({ to: "/home" }), 700);
    } catch (err: any) {
      toast.error(err.message ?? "Upload failed");
    } finally {
      setBusy(false);
    }
  };

  const handleSkip = () => navigate({ to: "/home" });

  return (
    <main className="min-h-screen grid place-items-center bg-background text-foreground px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-xl"
      >
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Upload your CV</h1>
          <p className="mt-2 text-muted-foreground">We'll tailor your interview practice to your experience.</p>
        </div>

        <div className="rounded-2xl bg-card text-card-foreground shadow-elegant p-8">
          <div
            onClick={() => inputRef.current?.click()}
            className="border-2 border-dashed border-foreground/15 rounded-xl p-10 text-center cursor-pointer hover:border-primary/50 hover:bg-foreground/[0.02] transition"
          >
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="hidden"
            />
            {file ? (
              <div className="flex flex-col items-center gap-2">
                <FileText className="h-10 w-10 text-primary" />
                <div className="font-medium">{file.name}</div>
                <div className="text-xs text-muted-foreground">{(file.size / 1024).toFixed(1)} KB</div>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3">
                <div className="h-12 w-12 rounded-full bg-primary/10 grid place-items-center">
                  <Upload className="h-5 w-5 text-primary" />
                </div>
                <div className="font-medium">Click to upload your CV</div>
                <div className="text-xs text-muted-foreground">PDF, DOC, or DOCX</div>
              </div>
            )}
          </div>

          <div className="mt-6 flex flex-col sm:flex-row gap-3">
            <Button
              onClick={handleUpload}
              disabled={!file || busy || done}
              className="flex-1 h-11"
            >
              {done ? (
                <><CheckCircle2 className="mr-2 h-4 w-4" /> Uploaded</>
              ) : busy ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>Upload & Continue <ArrowRight className="ml-2 h-4 w-4" /></>
              )}
            </Button>
            <Button variant="outline" onClick={handleSkip} disabled={busy} className="h-11">
              Skip for now
            </Button>
          </div>
        </div>
      </motion.div>
    </main>
  );
}
