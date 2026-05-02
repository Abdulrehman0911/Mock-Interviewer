# Mock Interviewer Frontend — Hybrid Build (Reuse Loveable + Build New)

**Approach:** Extract generic Loveable components + adapt patterns + build new screens
**Goal:** Token-efficient, fast build using existing code where it matches
**Tech Stack:** React 18 + TanStack Router v1 + Tailwind + shadcn/ui + Framer Motion
**Colors:** MockMate (matte green + warm beige, NOT Loveable blue)

---

## PART 1: REUSE FROM LOVEABLE

### Step 1.1: Copy These Directories Intact (No Changes)
```
src/components/ui/
├── button.tsx
├── card.tsx
├── input.tsx
├── form.tsx
├── dialog.tsx
├── tabs.tsx
├── badge.tsx
├── progress.tsx
├── label.tsx
├── select.tsx
├── [all other shadcn components]
```

All shadcn/ui components are generic and don't need modification.

### Step 1.2: Copy Configuration Files Intact
- `vite.config.ts` — No changes
- `tsconfig.json` — No changes
- `tailwind.config.ts` — Keep as is
- `src/lib/utils.ts` — No changes
- `.prettierrc` — No changes
- `eslint.config.js` — No changes
- `package.json` — Keep dependencies, just add `firebase` package

### Step 1.3: Copy Project Structure (As Reference)
- Keep `src/routes/` file-based routing (TanStack Router v1)
- Keep `src/components/` folder organization
- Keep `src/hooks/` for custom hooks
- Keep `src/lib/` for utilities

### Step 1.4: Extract Animation Patterns from Loveable
From `src/styles.css` and component files, extract:
- `@keyframes fadeIn` (opacity 0→1)
- `@keyframes slideUp` (translateY 20px→0)
- `@keyframes pulse` (opacity oscillation)
- `@keyframes gradient` (background animation)
- Hover effects: `scale-105`, `shadow-lg`
- Transition classes: `transition-all duration-200`

### Step 1.5: Adapt Navbar Structure (Keep Pattern, Modify Content)
- Use Loveable's `src/components/site/Navbar.tsx` as reference
- Keep styling approach and hover effects
- Modify content: Show logo + user profile icon (top right) only
- Remove marketing nav items

---

## PART 2: REPLACE SUPABASE WITH FIREBASE

### Step 2.1: Delete Supabase Integration
- Delete `src/integrations/supabase/` folder entirely
- Remove supabase packages from `package.json`

### Step 2.2: Create Firebase Integration
**File:** `src/integrations/firebase/client.ts`
```typescript
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
```

### Step 2.3: Create Firebase Auth Hook
**File:** `src/hooks/useAuth.ts`
```typescript
import { useState, useEffect } from 'react';
import { auth } from '@/integrations/firebase/client';
import { User, onAuthStateChanged, signOut } from 'firebase/auth';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const logout = async () => {
    await signOut(auth);
  };

  return { user, loading, logout };
}
```

---

## PART 3: MODIFY & DELETE LOVEABLE ROUTES

### Step 3.1: Delete These Loveable Routes
- `src/routes/index.tsx` (Loveable landing — replace with redirect)
- `src/routes/upload-cv.tsx` (you don't need CV upload)
- Delete all marketing page routes

### Step 3.2: Modify `src/routes/__root.tsx`
Keep:
- Root layout structure
- Dark theme setup
- Outlet for nested routes

Modify:
- Navbar: Use simplified version (logo + profile icon)
- Add auth redirect: if not logged in → `/auth`, if logged in → `/home`
- Remove marketing content

### Step 3.3: Modify `src/routes/auth.tsx`
Keep:
- Layout and styling from Loveable (if exists)
- Dark theme, animations, card design

Replace:
- Supabase calls → Firebase calls
- Use `signInWithEmailAndPassword()` and `createUserWithEmailAndPassword()` from firebase/auth
- Use shadcn form components (already copied)

---

## PART 4: BUILD NEW ROUTES (6 Total)

### New Route 1: `src/routes/index.tsx`
Simple redirect:
```typescript
import { useEffect } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { useAuth } from '@/hooks/useAuth';

export function IndexRoute() {
  const navigate = useNavigate();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (!loading) {
      navigate({ to: user ? '/home' : '/auth' });
    }
  }, [user, loading, navigate]);

  return null;
}
```

### New Route 2: `src/routes/home.tsx`
**Dashboard after login**

Components needed:
- Header: Logo + user profile icon
- Hero: Large "Start Interview" button (center, prominent, pulsing glow)
- Stats grid: 3 cards (Total Interviews, Average Score, Best Score)
- Previous interviews: List of past interview cards

Design:
- Full width mobile, centered container desktop
- Dark background (#172918)
- Hero button: Beige primary color (#DCCBB1), scale + glow on hover
- Stats cards: Dark card backgrounds, hover lift effect
- Use Loveable's card styling and animations

Animations:
- Page fades in on mount
- Stats cards slide up (staggered)
- Hero button has continuous pulse + shadow glow
- Cards on hover: scale + lift (translateY -4px)

### New Route 3: `src/routes/select-company.tsx`
**Company selection grid**

Components needed:
- Header: "Select Company" title + back button
- Grid of company cards (responsive: 2 cols mobile, 3 cols tablet, 4 cols desktop)
- Each card: logo/icon, company name, description, question count

Design:
- Company cards use shadcn Card component
- Logo: 48x48px circle with company color
- Hover effect: Lift + scale + glow (use Loveable patterns)
- Selected state: Checkmark + border highlight
- Click to select → navigate to `/select-role`

Animations:
- Cards fade/slide in (staggered)
- Hover: scale-105 + shadow glow
- Selection: checkmark animates in

### New Route 4: `src/routes/select-role.tsx`
**Role selection for company**

Components needed:
- Header: "Select Role for [Company]" + back button
- List of job roles
- Each role: name, difficulty badge, question count

Design:
- Vertical list (full width on mobile)
- Difficulty badges: Color-coded (Easy=green, Medium=yellow, Hard=red)
- Use shadcn Badge component
- Hover: lift + scale
- Selected: left border + background highlight

Animations:
- Items fade in (staggered)
- Hover: scale + shadow
- Selection: smooth transition to interview

### New Route 5: `src/routes/interview.tsx`
**CORE SCREEN — Interview recording**

Layout:
```
┌─────────────────────────────────────┐
│ Question 2 of 5  [Progress Bar ███]│
├─────────────────────────────────────┤
│  Question Display  │  Webcam Preview │
│  (left or top)     │  (right or btm) │
│                    │  Recording Ctrl │
├─────────────────────────────────────┤
│  [I'm Ready]  [Skip]                │
└─────────────────────────────────────┘
```

Components needed:
1. **QuestionDisplay.tsx** — Show question text + difficulty
2. **WebcamPreview.tsx** — Video element (when recording)
3. **RecordingControls.tsx** — "I'm Ready", "Stop", "Skip" buttons
4. **ProgressBar.tsx** — Interview progress (Question X of Y)
5. **Timer.tsx** — Show elapsed time (MM:SS) when recording
6. **LoadingSpinner.tsx** — Show while processing

States:
- Ready: Show "I'm Ready" button
- Recording: Show timer + red "RECORDING" indicator + "Stop" button
- Processing: Show spinner + "Processing your answer..."
- Next Question: Fade out question, fade in next

Design:
- Dark background
- Question: Large, readable text
- Webcam: 16:9 ratio, border, rounded
- Recording indicator: Red pulsing text "● RECORDING"
- Timer: Monospace font, large
- Buttons: Primary (beige), clear hierarchy

Animations:
- Question fades in on mount
- Recording indicator: Red pulse (continuous)
- Timer: Smooth number updates (no jumps)
- Transition between questions: Fade out → fade in

Critical Interactions:
1. User clicks "I'm Ready"
2. Webcam opens, preview shows
3. Recording button changes to red "Stop"
4. Timer starts counting
5. User speaks answer
6. User clicks "Stop"
7. Loading spinner appears
8. 15 seconds of processing...
9. Next question appears OR report (if last question)

API Call:
```typescript
const formData = new FormData();
formData.append('video', videoBlob);
formData.append('question_difficulty', difficulty);
formData.append('question_id', questionId);

const response = await fetch('http://localhost:5000/api/process-video', {
  method: 'POST',
  body: formData,
});

const result = await response.json();
// result contains: model_score, behavioral, correctness, breakdown
```

Responsive:
- Mobile: Stack vertically (question top, camera bottom)
- Desktop: Side-by-side (question left, camera right)

### New Route 6: `src/routes/report.tsx`
**Interview results & feedback**

Components needed:
1. **ScoreRing.tsx** — Circular progress ring (animated fill)
2. **ScoreBreakdown.tsx** — 4 cards grid (behavioral, correctness, eye contact, pace)
3. **Feedback.tsx** — Strengths + improvements bullets
4. **ActionButtons.tsx** — Practice Again, View Detailed, Home

Design:
- Header: "Interview Complete" + Company + Role
- Score Ring: Large (center), number in middle (e.g., "7.4/10")
- Ring colors: Red (<4), Orange (4-6), Green (>6)
- Score cards: 2x2 grid (mobile: stack), each with icon + metric + bar
- Feedback section: Bullets with icons (checkmark for strengths, alert for improvements)
- Buttons: Full width, primary + secondary

Data Display:
```
Overall: 7.4/10 (ring progress fills to 74%)

Behavioral:  7.5/10 → 3.0/4
Correctness: 6.0/10 → 3.6/6
Eye Contact: 72%
Speaking Pace: 145 WPM

Strengths:
✓ Good eye contact and confidence
✓ Clear, structured answer

Areas to Improve:
⚠ Reduce filler words (detected: 3)
⚠ Speak slightly slower (current: 145 WPM)

[Practice Another Interview] [View Detailed Report] [Back to Home]
```

Animations:
- Page fades in
- Score ring animates fill (0 → final %, 2 second duration)
- Score cards slide in (staggered, 0.2s delay between each)
- Feedback bullets fade in one by one
- Buttons: Hover scale + glow

Responsive:
- Score cards: Stack on mobile, 2x2 grid on desktop
- Full width buttons on mobile

---

## PART 5: CREATE CUSTOM COMPONENTS

### Interview Components
**File:** `src/components/interview/QuestionDisplay.tsx`
- Display question text
- Show difficulty badge
- Show question number / total

**File:** `src/components/interview/WebcamPreview.tsx`
- Video element (with webcam feed)
- Border + rounded corners
- 16:9 aspect ratio
- Show "RECORDING" indicator when active

**File:** `src/components/interview/RecordingControls.tsx`
- "I'm Ready" button (primary, large)
- "Stop" button (red, large, only when recording)
- "Skip" button (secondary, small)
- Button states: idle, recording, loading

**File:** `src/components/interview/ProgressBar.tsx`
- Shows "Question X of Y"
- Visual progress bar (0-100%)
- Background: muted, fill: primary color

**File:** `src/components/interview/Timer.tsx`
- Shows elapsed time MM:SS
- Only visible when recording
- Monospace font, large
- Updates every second

### Report Components
**File:** `src/components/report/ScoreRing.tsx`
- Circular SVG progress ring
- Animated fill from 0 → final percentage (2 second duration)
- Number in center (e.g., "7.4")
- Color based on score: red (<4), orange (4-6), green (>6)
- Use Framer Motion for animation

**File:** `src/components/report/ScoreCard.tsx`
- Card showing: metric name, score, percentage, visual bar
- Used for 4 cards: Behavioral, Correctness, Eye Contact, Pace
- Icon on left, metric on right
- Use shadcn Card component

**File:** `src/components/report/Feedback.tsx`
- Two sections: Strengths + Improvements
- Bullet points with icons
- Green checkmarks for strengths, orange alerts for improvements

---

## PART 6: CREATE CUSTOM HOOKS

**File:** `src/hooks/useInterview.ts`
- Manage interview state: current question, answers array, scores array
- Load questions on mount
- Track progress (question X of Y)
- Calculate final results when session ends

**File:** `src/hooks/useRecording.ts`
- Manage video recording state
- Start recording (request camera permission)
- Stop recording (get blob)
- Upload to backend
- Handle loading/error states

---

## PART 7: CREATE API CLIENT

**File:** `src/lib/api.ts`
```typescript
const API_BASE = 'http://localhost:5000/api';

export async function getCompanies() {
  const response = await fetch(`${API_BASE}/roles`);
  return response.json();
}

export async function getQuestions(role: string) {
  const response = await fetch(`${API_BASE}/questions/${role}`);
  return response.json();
}

export async function processVideo(
  videoBlob: Blob,
  questionDifficulty: number,
  questionId: string
) {
  const formData = new FormData();
  formData.append('video', videoBlob);
  formData.append('question_difficulty', questionDifficulty.toString());
  formData.append('question_id', questionId);

  const response = await fetch(`${API_BASE}/process-video`, {
    method: 'POST',
    body: formData,
  });
  return response.json();
}
```

---

## PART 8: STYLING & COLORS (MockMate)

**File:** `src/styles.css`

Update color variables:
```css
:root {
  /* MockMate Brand Colors */
  --primary: #DCCBB1;           /* Warm beige */
  --primary-glow: #EBDCC1;      /* Light beige glow */
  --background: #172918;        /* Dark matte green */
  --card-bg: #EFE7D9;          /* Light card background */
  --secondary: #376040;         /* Deep green */
  --muted: #263826;            /* Muted green */
  
  --text-primary: #F2EADD;     /* Light foreground */
  --text-secondary: #C2B6A2;   /* Muted foreground */
  --text-dark: #172918;        /* Dark foreground */
  
  --success: #55B66E;          /* Success green */
  --success-fg: #091509;       /* Success dark */
  --destructive: #E6443D;      /* Error red */
  --destructive-fg: #F8F8F8;  /* Error light */
  
  --border: rgba(242, 234, 221, 0.12);
  --input-bg: rgba(242, 234, 221, 0.16);
}
```

Add animation keyframes (from Loveable):
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes pulseGlow {
  0%, 100% { box-shadow: 0 0 20px rgba(220, 203, 177, 0.5); }
  50% { box-shadow: 0 0 30px rgba(220, 203, 177, 0.8); }
}

.animate-fade-in { animation: fadeIn 0.5s ease-in; }
.animate-slide-up { animation: slideUp 0.5s ease-out; }
.animate-pulse-glow { animation: pulseGlow 2s infinite; }
```

---

## PART 9: FINAL DIRECTORY STRUCTURE

```
src/
├── routes/
│   ├── __root.tsx (MODIFIED from Loveable)
│   ├── index.tsx (NEW - redirect)
│   ├── auth.tsx (MODIFIED - Firebase)
│   ├── home.tsx (NEW)
│   ├── select-company.tsx (NEW)
│   ├── select-role.tsx (NEW)
│   ├── interview.tsx (NEW)
│   └── report.tsx (NEW)
├── components/
│   ├── ui/ (COPIED from Loveable - no changes)
│   ├── interview/ (NEW)
│   │   ├── QuestionDisplay.tsx
│   │   ├── WebcamPreview.tsx
│   │   ├── RecordingControls.tsx
│   │   ├── ProgressBar.tsx
│   │   └── Timer.tsx
│   ├── report/ (NEW)
│   │   ├── ScoreRing.tsx
│   │   ├── ScoreCard.tsx
│   │   └── Feedback.tsx
│   ├── shared/ (NEW)
│   │   ├── Navbar.tsx (ADAPTED)
│   │   └── Loading.tsx
│   └── (DELETE site/ - Loveable marketing)
├── hooks/ (NEW/MODIFIED)
│   ├── useAuth.ts (Firebase)
│   ├── useInterview.ts (NEW)
│   └── useRecording.ts (NEW)
├── integrations/
│   ├── firebase/ (NEW)
│   │   └── client.ts
│   └── (DELETE supabase/)
├── lib/
│   ├── utils.ts (COPIED from Loveable)
│   └── api.ts (NEW)
├── types/ (NEW - optional)
│   └── index.ts
├── styles.css (MODIFIED - MockMate colors)
├── router.tsx (from Loveable)
├── main.tsx or App.tsx (from Loveable)
└── vite-env.d.ts (from Loveable)

Config (KEEP from Loveable):
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.ts
├── .prettierrc
├── eslint.config.js
├── package.json
└── package-lock.json
```

---

## IMPLEMENTATION ORDER

1. **Prep **
   - Copy all `src/components/ui/` files
   - Copy all config files (vite, ts, tailwind, prettier, eslint)
   - Keep `src/lib/utils.ts`

2. **Setup **
   - Delete `src/integrations/supabase/`
   - Create `src/integrations/firebase/client.ts`
   - Create `src/hooks/useAuth.ts`
   - Create `src/lib/api.ts`

3. **Routes **
   - Modify `src/routes/__root.tsx`
   - Modify `src/routes/auth.tsx` 
   - Create `src/routes/index.tsx`
   - Create `src/routes/home.tsx` 
   - Create `src/routes/select-company.tsx` 
   - Create `src/routes/select-role.tsx` 

4. **Interview & Report **
   - Create `src/routes/interview.tsx`
   - Create `src/routes/report.tsx` 
   - Create all interview components
   - Create all report components 

5. **Polish **
   - Update `src/styles.css` with MockMate colors
   - Create custom hooks (useInterview, useRecording)
   - Add animations using Loveable patterns
   - Test responsive design

6. **Testing **
   - Test auth flow
   - Test interview recording
   - Test report display
   - Test mobile responsiveness



---

## KEY POINTS

✅ Reuse: All shadcn/ui components, configs, Loveable patterns
✅ Replace: Supabase → Firebase
✅ Build new: 6 routes, custom components, hooks, API client
✅ Colors: MockMate (beige + green)
✅ Animations: Loveable patterns but with MockMate colors
✅ Responsive: Mobile-first, tested on all screen sizes
✅ No CV upload screen
✅ Backend integration: API calls to localhost:5000

---

## ENVIRONMENT VARIABLES

**File:** `.env`
```
VITE_FIREBASE_API_KEY=your_key
VITE_FIREBASE_AUTH_DOMAIN=your_domain
VITE_FIREBASE_PROJECT_ID=your_project
VITE_FIREBASE_STORAGE_BUCKET=your_bucket
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
VITE_API_URL=http://localhost:5000/api
```

---

## DEPENDENCIES TO ADD

```json
{
  "firebase": "^10.x.x"
}
```

Remove Supabase packages.

---

## START NOW

1. Copy Loveable components and configs
2. Set up Firebase integration
3. Build routes in order (auth → home → interview → report)
4. Create custom components
5. Apply MockMate colors
6. Test end-to-end

Go! 🚀
