export interface User {
  uid: string
  email: string | null
  displayName: string | null
  photoURL: string | null
}

export interface Question {
  question_id: number
  question: string
  difficulty: 'easy' | 'medium' | 'hard'
}

export interface Company {
  id: string
  name: string
  description: string
  initials: string
  color: string
  roles: string[]
}

export interface Role {
  name: string
  questionCount: number
  difficulty: 'easy' | 'medium' | 'hard'
}

export interface ScoreBreakdown {
  behavioral: {
    score: number
    out_of: number
    percentage: number
    subscale: Record<string, number>
  }
  correctness: {
    score: number
    out_of: number
    percentage: number
    subscale: Record<string, number>
    tier?: string
    match_high?: number
    match_medium?: number
    match_low?: number
    filler_count?: number
  }
  final: {
    score: number
    out_of: number
    percentage: number
  }
}

export interface QuestionResult {
  question: Question
  scores: ScoreBreakdown
  transcript: string
  features: VideoFeatures
  feedback: {
    follow_up_question?: string
    strengths?: string[]
    improvements?: string[]
    performance_level?: string
  }
}

export interface VideoFeatures {
  transcript_length: number
  wpm: number
  pause_count: number
  pause_avg_duration: number
  filler_count: number
  eye_contact_pct: number
  head_pose_score: number
  posture_score: number
  facial_stability_score: number
  question_difficulty: number
}

export interface InterviewSession {
  company: Company
  role: string
  questions: Question[]
  currentQuestionIndex: number
  results: QuestionResult[]
  startedAt: Date
  completedAt?: Date
}

export interface PastInterview {
  id: string
  company: string
  role: string
  date: string
  overallScore: number
  results?: QuestionResult[]
}

export interface ProcessVideoResponse {
  success: boolean
  scores: ScoreBreakdown
  transcript: string
  features: VideoFeatures
  feedback: {
    follow_up_question?: string
    strengths?: string[]
    improvements?: string[]
    performance_level?: string
  }
  error?: string
}

export type DifficultyLevel = 'easy' | 'medium' | 'hard'
export type PerformanceLevel = 'excellent' | 'good' | 'average' | 'poor'
