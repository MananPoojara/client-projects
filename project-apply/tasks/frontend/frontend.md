# Job Discovery System - Frontend Architecture

## Document Information
- **Version:** 1.4 (Auto-Fill + Filters)
- **Last Updated:** 2026-02-21
- **Target Hardware:** 8GB RAM, Intel i5 (4 cores)
- **Budget:** $0 (Open Source Only)

---

## IMPORTANT: What This System CANNOT Do

```
❌ CANNOT create accounts on portals (Indeed, LinkedIn)
❌ CANNOT upload resumes TO portals  
❌ CANNOT submit applications on portals

✅ CAN find jobs automatically (with filters!)
✅ CAN parse resumes automatically  
✅ CAN match candidates to jobs
✅ CAN generate cover letters & tailored resumes locally
✅ CAN auto-fill form answers (copy/paste ready!) ← NEW
✅ CAN filter jobs: Remote/Hybrid/Onsite ← NEW
✅ CAN track staff progress
```

**Staff still applies manually** - but application prep is 80% faster.

---

## 0. Staff Workflow (Real-World)

### The Actual Use Case
```
1 Staff Member = 5 Candidates per session
Each Candidate = 60 Applications (average)

Daily for 1 Staff:
- Upload/manage 5 candidates (bulk CSV)
- Review 300 job matches (5 candidates × 60 jobs)
- Approve/submit 20-30 applications
- Add notes to applications

Team of 200 Staff:
- 1,000 candidates/day
- 60,000 job matches to calculate
- 6,000 applications submitted/day
```

### UI Flow for Staff
```
1. Login → Dashboard
2. Click "Add Candidates" → Upload CSV (5 at a time)
3. System auto-matches each to 60 jobs (background)
4. Dashboard shows "X matches ready for review"
5. Click to see matches → Review list
6. Select jobs → "Generate Applications"
7. Applications created as Draft
8. Review each → Approve/Reject
9. Batch Submit approved applications
10. Done for the day!
```

---

## 1. Technology Stack (Free & Lightweight)

### Core Framework
- **Framework:** React 18 with Vite (fast build, small bundles)
- **Language:** JavaScript (skip TypeScript to reduce complexity)
- **State Management:** React Context + useReducer (no Redux needed)
- **HTTP Client:** Fetch API (built-in, no axios overhead)

### UI Library
- **Primary:** Tailwind CSS (free, lightweight, no runtime)
- **Icons:** Heroicons (SVG, small bundle)
- **Charts:** Chart.js (free, ~60KB)
- **Forms:** Native HTML forms with vanilla JS validation
- **Date Handling:** Native Date API (no library needed)

### Additional (All Free)
- **PDF Viewer:** react-pdf (Mozilla PDF.js)
- **File Upload:** Native file input
- **PDF Export:** jspdf (free)
- **Animations:** CSS transitions (no library)

---

## 2. Hardware-Optimized Configuration

### Performance Targets on 8GB RAM + i5
- **Initial Load:** < 500KB JavaScript
- **First Contentful Paint:** < 1.5 seconds
- **Time to Interactive:** < 3 seconds
- **Memory Usage:** < 200MB browser tab

### Optimization Strategies
1. **Code Splitting:** Route-based lazy loading
2. **No Heavy Libraries:** Use CSS instead of styled-components
3. **Minimal Dependencies:** ~15 total npm packages (vs 100+)
4. **Efficient Rendering:** React.memo on lists
5. **Virtual Scrolling:** For 1000+ item lists

---

## 3. Module Structure (Simplified)
```
frontend/
├── index.html              # Entry point
├── package.json
├── vite.config.js
├── tailwind.config.js
├── src/
│   ├── main.jsx           # React entry
│   ├── App.jsx            # Root with routing
│   ├── components/        # Reusable UI
│   │   ├── Layout.jsx    # Header, Sidebar
│   │   ├── DataTable.jsx # Simple table
│   │   ├── Modal.jsx     # Reusable modal
│   │   └── Button.jsx   # Styled button
│   ├── pages/            # Route pages
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Candidates.jsx
│   │   ├── Jobs.jsx
│   │   ├── Applications.jsx
│   │   ├── HeadDashboard.jsx
│   │   └── Reports.jsx
│   ├── services/         # API calls
│   │   └── api.js        # Fetch wrapper
│   ├── context/          # State
│   │   └── AuthContext.jsx
│   ├── hooks/            # Custom hooks
│   │   └── useFetch.js
│   └── utils/            # Helpers
│       └── helpers.js
└── public/               # Static assets
    └── logo.svg
```

---

## 4. Page Specifications (Simplified)

### 4.1 Login Page (`/login`)
**Features:**
- Email + password fields
- "Remember me" checkbox
- Error message display
- Loading state
- JWT stored in localStorage

**Performance:** Single component, no external deps

### 4.2 Staff Dashboard (`/dashboard`)
**Components:**
- Stats cards (4 cards: today apps, pending, matched, success rate)
- Recent activity list (last 10)
- Quick actions (3 buttons)

### 4.3 Head Dashboard (`/head-dashboard`)
**Components:**
- Team stats (total staff, today apps, week apps, success rate)
- Staff leaderboard table (name, today, week, month, rank)
- Simple bar chart (apps per day - last 7 days)
- Export CSV button

### 4.4 Candidates Page (`/candidates`)
**Features:**
- Search bar
- Filter dropdown (status)
- Table with pagination
- Add single button → modal form
- **Bulk Upload button → CSV upload modal**
- Edit/Delete actions
- View matches for candidate

**Table Columns:** Name, Email, Skills (count), Status, Added Date, Actions

**Bulk Upload Modal:**
- CSV file upload (drag & drop)
- Preview first 5 rows
- Column mapping (name, email, skills, etc.)
- Upload button with progress bar
- Success/error summary after

### 4.5 Jobs Page (`/jobs`) - WITH FILTERS!
**Features:**
- Search bar
- **Work Type filter (NEW):**
  - [ ] Remote
  - [ ] Hybrid  
  - [ ] Onsite
- **Location filter:** Dropdown + search
- **Source filter:** Indeed, Jobrapido, Jooble, Manual
- **Date Posted filter:** Last 24h, 3 days, 7 days, Any
- **Match Score filter:** 90%+, 70%+, Any
- Card list view with match count badge
- Add manual job button
- Import CSV button (for manual job lists)
- View candidates for job
- **Apply button** → Opens Auto-Fill Modal!

### 4.6 Jobs Page - Auto-Fill Modal (NEW!)
**When staff clicks "Apply" on a job:**

```
┌─────────────────────────────────────────────────────────────┐
│  📋 APPLICATION DATA - John Doe                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  BASIC INFO                          [📋 Copy All]         │
│  ─────────────────                                        │
│  Full Name:    John Doe                    [📋]           │
│  Email:       john.doe@email.com           [📋]           │
│  Phone:       +1 234 567 8900             [📋]           │
│  Address:     123 Main St, New York        [📋]           │
│                                                             │
│  EXPERIENCE                                               │
│  ─────────                                               │
│  Current:     Software Engineer at Tech Corp   [📋]        │
│  Previous:    Junior Dev at Startup Inc       [📋]        │
│  Total Years: 5 years                        [📋]          │
│                                                             │
│  EDUCATION                                               │
│  ────────                                                │
│  Degree:     Bachelor of Science             [📋]        │
│  Field:      Computer Science                [📋]        │
│  University: NYU                                [📋]        │
│                                                             │
│  SKILLS (for matching):                                    │
│  ────────────────────                                      │
│  JavaScript, React, Node.js, Python, AWS     [📋]        │
│                                                             │
│  COVER LETTER (generated):                                 │
│  ─────────────────────                                     │
│  [Preview]                              [Download PDF]   │
│                                                             │
│  TAILORED RESUME:                                         │
│  ────────────────                                         │
│  [View]                                   [Download PDF]   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  [Open Indeed in New Tab]  [Copy Next Field]       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Click [📋] to copy that field to clipboard!**

### 4.7 Applications Page (`/applications`)
**Features:**
- Status filter tabs (All, Draft, Pending Review, Approved, Submitted)
- List view with status badges
- **Generate Applications button** (for selected candidate)
- Review button → opens detail modal
- Bulk approve/reject (for Senior/Head)
- Submit button for approved apps

### 4.7 Application Review Modal
- Candidate info (name, skills)
- Job info (title, company)
- Match score percentage
- Cover letter preview (auto-generated)
- Staff notes textarea
- **Approve** button (moves to Approved)
- **Reject** button with reason (moves to Rejected)
- **Submit** button (if approved - submits to portal)

### 4.8 Bulk Application Generation
**Flow:**
1. Go to candidate → Click "Generate Applications"
2. Select job filters (location, type, etc.)
3. System finds top 60 matching jobs
4. Preview 60 applications (draft status)
5. Click "Create All" → Creates 60 draft applications
6. Redirect to Applications page to review
- Notes textarea
- Approve/Reject/Submit buttons

---

## 5. Component Specifications

### 5.1 DataTable Component
```javascript
// Lightweight table with:
- Column headers (clickable sort)
- Row data display
- Pagination (prev/next)
- No external library
```

### 5.2 Modal Component
```javascript
// CSS-based modal:
- Fixed overlay
- Centered content
- Close button
- No react-portal needed
```

### 5.3 Chart Component
```javascript
// Chart.js - free and lightweight:
// Bar chart for daily apps
// Simple line for trends
// Pie for source breakdown
```

---

## 6. Security (Frontend)

### 6.1 Token Management
```javascript
// Store JWT in localStorage
// Add to all API requests
// Clear on logout
```

### 6.2 Route Protection
```javascript
// PrivateRoute component
// Check token exists
// Redirect to login if not
```

### 6.3 Role-Based UI
```javascript
// Conditional rendering based on role
// Head: sees all features
// Senior: sees candidates, jobs, apps
// Staff: sees own applications
```

---

## 7. Performance Optimizations

### 7.1 Bundle Size
- **Target:** < 300KB total JS
- **Strategy:**
  - No TypeScript (faster build, smaller output)
  - Tailwind (purges unused CSS)
  - No icon library - use inline SVGs
  - No form library - native validation

### 7.2 Runtime Performance
- **React.memo** on list items
- **Debounced** search (300ms)
- **Lazy loading** for routes
- **CSS animations** (no JS)

### 7.3 Caching
- API responses cached in memory
- LocalStorage for user preferences

---

## 8. Deployment on Low-End Hardware

### 8.1 Options (Free)
1. **Static Hosting:** Serve with nginx
2. **Node.js:** Express static files
3. **Docker:** Nginx alpine image

### 8.2 Server Requirements (for frontend only)
- **RAM:** 512MB minimum
- **CPU:** 1 core
- **Storage:** 100MB

### 8.3 Build for Production
```bash
npm run build
# Output: dist/ folder
# Serve with nginx
```

---

## 9. Work Items

### 9.1 frontend-setup
**Category:** infrastructure

Set up React frontend with Vite and Tailwind

**Steps:**
1. Initialize React project with Vite
2. Install Tailwind CSS
3. Set up folder structure
4. Create base layout components
5. Configure routing
6. Set up API service
7. Verify build works

**Verification:**
- `npm run dev` starts
- `npm run build` produces dist/

---

### 9.2 auth-ui
**Category:** feature

Build login page and auth context

**Steps:**
1. Create login form
2. Add form validation
3. Implement JWT storage
4. Create AuthContext
5. Add protected routes
6. Test login flow

**Verification:**
- Login works
- Token stored
- Protected routes work

---

### 9.3 staff-dashboard-ui
**Category:** feature

Build staff dashboard

**Steps:**
1. Create dashboard layout
2. Add stat cards
3. Add recent activity
4. Add quick actions
5. Fetch dashboard data
6. Test display

**Verification:**
- Dashboard displays
- Data loads correctly

---

### 9.4 head-dashboard
**Category:** feature

Build Head dashboard with staff progress

**Steps:**
1. Create Head dashboard layout
2. Add team stats
3. Add leaderboard table
4. Add simple chart
5. Add export button
6. Test with data

**Verification:**
- All components render
- Data displays correctly

---

### 9.5 candidates-ui
**Category:** feature

Build candidate management with bulk upload

**Steps:**
1. Create candidates list with DataTable
2. Add search/filter
3. Create add/edit modal
4. **Create bulk CSV upload modal**
5. Add delete confirmation
6. Connect API
7. Test CRUD
8. Test bulk upload

**Verification:**
- List displays
- Add/Edit works
- Delete works
- Bulk CSV upload works

---

### 9.6 jobs-ui
**Category:** feature

Build job listing

**Steps:**
1. Create jobs list
2. Add search/filter
3. Add job cards
4. Add manual job form
5. Connect API
6. Test

**Verification:**
- Jobs display
- Filters work

---

### 9.7 application-workflow-ui
**Category:** feature

Build application workflow with bulk generation

**Steps:**
1. Create applications list with status tabs
2. Create review modal with approve/reject
3. **Create bulk application generation modal**
4. Add submit functionality
5. Connect API
6. Test workflow end-to-end

**Verification:**
- Status tabs work
- Review modal works
- Bulk generation creates 60 apps
- Workflow completes

---

### 9.8 responsive-optimization
**Category:** optimization

Ensure responsive design

**Steps:**
1. Test mobile view
2. Fix layout issues
3. Test tablet view
4. Optimize for touch
5. Final testing

**Verification:**
- Works on mobile
- Works on tablet

---

## 10. Acceptance Criteria

1. ✅ Login/logout works
2. ✅ Role-based access (Head/Senior/Staff)
3. ✅ Dashboard displays stats
4. ✅ Head sees staff progress + leaderboard
5. ✅ Candidates CRUD works
6. ✅ **Bulk CSV upload works (5 candidates)**
7. ✅ Jobs listing works
8. ✅ Jobs import (CSV) works
9. ✅ Application workflow (draft→review→approve→submit)
10. ✅ **Bulk application generation (60 per candidate)**
11. ✅ Responsive on all devices
12. ✅ Bundle size < 500KB
13. ✅ Works on 8GB RAM machine

---

## 11. Realistic UI Flow (1 Staff)

```
Morning:
1. Login → Dashboard shows "5 candidates ready to upload"
2. Click "Candidates" → "Upload CSV"
3. Select CSV with 5 candidates → Upload
4. System processes in background → "5 candidates added"
5. Click "Generate Applications" for first candidate
6. Select filters → Preview 60 jobs → Create All
7. Repeat for 5 candidates = 300 draft applications

Day:
8. Click "Applications" → See 300 drafts
9. Click each → Review → Approve/Reject
10. Batch submit 20-30 approved applications
11. Done!

This is realistic and doesn't blast the system.
```

---

## 11. Dependencies List

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0",
    "jspdf": "^2.5.1"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

**Total:** ~7 dependencies (vs 100+ with Material UI)
