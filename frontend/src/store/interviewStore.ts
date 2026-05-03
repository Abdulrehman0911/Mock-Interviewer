import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Company } from "@/lib/companies";
import type { Question, ProcessVideoResult } from "@/lib/api";

export interface QuestionResult {
  question: Question;
  videoResult: ProcessVideoResult;
}

export interface PastInterview {
  id: string;
  company: string;
  role: string;
  date: string;
  overallScore: number;
  results: QuestionResult[];
}

interface InterviewState {
  company: Company | null;
  role: string | null;
  questions: Question[];
  currentQuestionIndex: number;
  results: QuestionResult[];
  isProcessing: boolean;
  processingProgress: number;
  pastInterviews: PastInterview[];

  setCompany: (company: Company) => void;
  setRole: (role: string) => void;
  setQuestions: (questions: Question[]) => void;
  nextQuestion: () => void;
  addResult: (result: QuestionResult) => void;
  setProcessing: (processing: boolean, progress?: number) => void;
  savePastInterview: (interview: PastInterview) => void;
  reset: () => void;
}

export const useInterviewStore = create<InterviewState>()(
  persist(
    (set) => ({
      company: null,
      role: null,
      questions: [],
      currentQuestionIndex: 0,
      results: [],
      isProcessing: false,
      processingProgress: 0,
      pastInterviews: [],

      setCompany: (company) => set({ company }),
      setRole: (role) => set({ role }),
      setQuestions: (questions) => set({ questions, currentQuestionIndex: 0, results: [] }),
      nextQuestion: () => set((s) => ({ currentQuestionIndex: s.currentQuestionIndex + 1 })),
      addResult: (result) => set((s) => ({ results: [...s.results, result] })),
      setProcessing: (isProcessing, processingProgress = 0) => set({ isProcessing, processingProgress }),
      savePastInterview: (interview) =>
        set((s) => ({ pastInterviews: [interview, ...s.pastInterviews].slice(0, 20) })),
      reset: () =>
        set({ company: null, role: null, questions: [], currentQuestionIndex: 0, results: [], isProcessing: false, processingProgress: 0 }),
    }),
    {
      name: "mockmate-interview",
      partialize: (s) => ({ pastInterviews: s.pastInterviews }),
    },
  ),
);
