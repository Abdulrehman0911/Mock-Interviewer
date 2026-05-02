import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:5000/api",
  timeout: 60_000,
});

export interface Question {
  question_id: number;
  question: string;
  difficulty: "easy" | "medium" | "hard";
}

export interface ScoreBreakdown {
  behavioral: { score: number; out_of: number; percentage: number; subscale: Record<string, number> };
  correctness: { score: number; out_of: number; percentage: number; filler_count?: number };
  final: { score: number; out_of: number; percentage: number };
}

export interface ProcessVideoResult {
  success: boolean;
  scores: ScoreBreakdown;
  transcript: string;
  features: {
    wpm: number;
    eye_contact_pct: number;
    filler_count: number;
    pause_count: number;
  };
  feedback: {
    follow_up_question?: string;
    strengths?: string[];
    improvements?: string[];
    performance_level?: string;
  };
  error?: string;
}

export async function getRoles(): Promise<string[]> {
  const res = await api.get<{ success: boolean; roles: string[] }>("/roles");
  if (!res.data.success) throw new Error("Failed to fetch roles");
  return res.data.roles;
}

export async function getQuestions(role: string, count = 5): Promise<Question[]> {
  const res = await api.get<{ success: boolean; questions: Question[] }>(
    `/questions/${encodeURIComponent(role)}`,
    { params: { count } },
  );
  if (!res.data.success) throw new Error("Failed to fetch questions");
  return res.data.questions;
}

export async function processVideo(
  videoBlob: Blob,
  questionId: number,
  questionText: string,
  questionDifficulty: number,
  role: string,
): Promise<ProcessVideoResult> {
  console.log("[MockMate] Video upload starting", {
    questionId,
    role,
    videoSize: videoBlob.size,
    videoType: videoBlob.type,
  });

  const formData = new FormData();
  formData.append("video", videoBlob, "answer.webm");
  formData.append("question_id", String(questionId));
  formData.append("question_text", questionText);
  formData.append("question_difficulty", String(questionDifficulty));
  formData.append("role", role);

  try {
    const res = await api.post<ProcessVideoResult>("/process-video", formData, {
      // DO NOT set Content-Type — axios must auto-set multipart/form-data with boundary
      timeout: 180_000,
    });
    console.log("[MockMate] Video processing success", {
      score: res.data.scores?.final?.score,
      wpm: res.data.features?.wpm,
      eyeContact: res.data.features?.eye_contact_pct,
      success: res.data.success,
    });
    return res.data;
  } catch (error: unknown) {
    const axiosErr = error as { response?: { status?: number; data?: unknown }; message?: string };
    console.error("[MockMate] Video processing failed", {
      status: axiosErr.response?.status,
      responseData: axiosErr.response?.data,
      message: axiosErr.message,
    });
    throw error;
  }
}

export async function getSessionSummary(scores: number[], transcripts: string[], role: string) {
  const res = await api.post("/session-summary", { scores, transcripts, role });
  return res.data;
}
