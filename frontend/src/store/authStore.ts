import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'
import type { PastInterview } from '@/types'

interface AuthState {
  user: User | null
  isLoading: boolean
  pastInterviews: PastInterview[]
  setUser: (user: User | null) => void
  setLoading: (loading: boolean) => void
  addPastInterview: (interview: PastInterview) => void
  clearUser: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isLoading: true,
      pastInterviews: [],
      setUser: (user) => set({ user, isLoading: false }),
      setLoading: (isLoading) => set({ isLoading }),
      addPastInterview: (interview) =>
        set((state) => ({
          pastInterviews: [interview, ...state.pastInterviews].slice(0, 20),
        })),
      clearUser: () => set({ user: null, isLoading: false }),
    }),
    {
      name: 'mockmate-auth',
      partialize: (state) => ({
        pastInterviews: state.pastInterviews,
      }),
    }
  )
)
