# Job Discovery System - Backend Architecture

## Document Information
- **Version:** 1.4 (Auto-Fill + Filters)
- **Last Updated:** 2026-02-21
- **Target Hardware:** 8GB RAM, Intel i5 (4 cores)
- **Budget:** $0 (Open Source Only)

---

## 0. THE REAL WORKFLOW

### What CAN Be Automated ✅
```
1. Job Discovery - Scrape jobs from portals, show in dashboard
2. Resume Parsing - Extract skills, experience from PDF/DOCX
3. Skill Matching - Match candidates to jobs automatically
4. Application Prep:
   - Generate cover letters
   - Tailor resumes locally
   - Auto-fill form answers (copy/paste ready!) ← NEW
5. Dashboard Filters: Remote/Hybrid/Onsite ← NEW
6. Staff Tracking - Head sees everyone's progress
```

### What CANNOT Be Automated ❌
```
1. Creating candidate accounts on portals (CAPTCHA, phone verify)
2. Uploading resumes TO the portal (anti-bot blocks)
3. Submitting applications on portal (blocked by portals)
4. Portal login verification
```

### The Real Staff Workflow
```
BEFORE (Manual Only):
1. Browse Indeed/LinkedIn manually
2. Search jobs manually
3. Note down candidate skills manually
4. Fill application form manually
5. Upload resume manually
6. Submit manually
7. Repeat 60 times

WITH THIS SYSTEM:
1. System scrapes jobs automatically
2. Staff reviews matched jobs in dashboard
3. Click "Prepare Application" → System generates:
   - Cover letter (template-based)
   - Tailored resume (adds job-specific keywords)
4. Staff copies to portal, uploads resume, submits
5. Staff marks as "Submitted" in system
6. Done! (Saved ~80% time on prep work)
```

---

## 1. Staff Workflow (Real-World)

### The Actual Use Case
```
1 Staff Member = 5 Candidates per session
Each Candidate = 60 Applications (average)

Daily for 1 Staff:
- Review 300 job matches (5 candidates × 60 jobs)
- Approve/submit 20-30 applications
- Add notes to applications

Team of 200 Staff:
- 200 × 5 = 1,000 candidates/day
- 200 × 30 = 6,000 applications submitted/day
- 200 × 300 = 60,000 job matches to calculate/day
```

### API Load Calculation
- **Read operations:** High (staff browsing jobs)
- **Write operations:** Moderate (60 apps × 200 staff = 12,000/day = 8/min)
- **Matching calculations:** Background (60,000/day = 700/hour = 12/min)
- **Conclusion:** Read-heavy, need good indexing, can process matching in background

---

## 1. Technology Stack (Free & Lightweight)

### Core Backend
- **Language:** Node.js 20 LTS (free)
- **Framework:** Express.js (free, lightweight)
- **Database:** PostgreSQL 15 (free, open source)
- **ORM:** Prisma (free, lightweight)
- **Queue:** Bull (free, Redis-based) - see note below

### Security (All Free)
- **Authentication:** JWT (jsonwebtoken - free)
- **Password:** bcrypt (free)
- **Validation:** Zod (free)
- **Encryption:** Node.js crypto (built-in)

### DevOps (All Free)
- **Container:** Docker (free Community Edition)
- **Logging:** Winston (free)
- **Process Manager:** PM2 (free)

### Note on Redis
Redis is recommended but requires extra RAM. For 8GB total:
- **Option A (Recommended):** Skip Redis, use in-memory queue
- **Option B:** Run Redis in minimal mode (256MB RAM)

---

## 2. Hardware-Optimized Configuration

### Server Specs for 8GB RAM + i5
```
Total RAM: 8GB
├── PostgreSQL: 2GB (shared buffers)
├── Node.js: 1.5GB (heap)
├── OS + Other: 1GB
└── Available: 3.5GB (headroom)
```

### Performance Targets
- **API Response Time:** < 200ms (average)
- **Concurrent Users:** 50-100
- **Database Connections:** 10-20 (pooled)
- **Request Throughput:** 100 req/sec

### Optimization Strategies
1. **Connection Pooling:** pgBouncer (minimal RAM)
2. **Query Optimization:** Proper indexes, query caching
3. **No Heavy Frameworks:** Plain Express, no NestJS
4. **Synchronous Jobs:** Run in main process initially
5. **Minimal Logging:** Production level only

---

## 3. System Architecture (Simplified)

### Single Server Deployment
```
┌─────────────────────────────────────────┐
│              8GB RAM Server             │
├─────────────────────────────────────────┤
│                                         │
│   ┌─────────────────────────────────┐  │
│   │         Node.js App             │  │
│   │  (Express + API + Workers)      │  │
│   └─────────────────────────────────┘  │
│                   │                     │
│   ┌─────────────────────────────────┐  │
│   │         PostgreSQL              │  │
│   │    (Database + Queries)         │  │
│   └─────────────────────────────────┘  │
│                                         │
│   ┌─────────────────────────────────┐  │
│   │         File Storage            │  │
│   │     (Local Disk / S3 later)     │  │
│   └─────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

### Module Structure
```
backend/
├── package.json
├── server.js              # Entry point
├── config/
│   └── db.js            # Database config
├── routes/
│   ├── auth.js          # Login, logout
│   ├── candidates.js    # CRUD
│   ├── jobs.js         # CRUD
│   ├── applications.js # Workflow
│   ├── dashboard.js    # Stats
│   └── reports.js      # Analytics
├── middleware/
│   ├── auth.js         # JWT verify
│   ├── rbac.js         # Role check
│   └── validate.js     # Zod validation
├── services/
│   ├── parser.js       # Resume parsing
│   ├── matching.js    # Skill matching
│   └── reports.js     # Analytics
├── utils/
│   ├── crypto.js       # Encryption
│   └── helpers.js      # Helpers
└── prisma/
    ├── schema.prisma  # Database schema
    └── migrations/    # DB migrations
```

---

## 4. Database Schema (PostgreSQL)

### Core Tables (Simplified)

```sql
-- Staff table
CREATE TABLE staff (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('head', 'senior_staff', 'staff')),
    department VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Candidates table
CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    location VARCHAR(255),
    linkedin_url VARCHAR(500),
    resume_path VARCHAR(500),
    skills JSONB DEFAULT '[]',
    experience_years INTEGER,
    current_company VARCHAR(255),
    current_title VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',
    consent_gdpr BOOLEAN DEFAULT false,
    created_by UUID REFERENCES staff(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Jobs table
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    description TEXT,
    requirements JSONB,
    skills_required JSONB DEFAULT '[]',
    salary_min INTEGER,
    salary_max INTEGER,
    source_url TEXT,
    source_portal VARCHAR(50),
    job_type VARCHAR(20),
    remote_type VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    posted_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Applications table
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id),
    job_id UUID REFERENCES jobs(id),
    staff_id UUID REFERENCES staff(id),
    cover_letter TEXT,
    status VARCHAR(30) DEFAULT 'draft',
    staff_notes TEXT,
    reviewer_id UUID REFERENCES staff(id),
    reviewed_at TIMESTAMP,
    submitted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staff activities for progress tracking
CREATE TABLE staff_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    staff_id UUID REFERENCES staff(id),
    activity_type VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES staff(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    details JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_candidates_status ON candidates(status);
CREATE INDEX idx_candidates_skills ON candidates USING GIN(skills);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_skills ON jobs USING GIN(skills_required);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_staff ON applications(staff_id);
CREATE INDEX idx_staff_activities_date ON staff_activities(created_at);
```

---

## 5. API Endpoints

### Authentication
```
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/refresh
```

### Candidates
```
GET    /api/candidates                    # List (with search, filter, pagination)
POST   /api/candidates                    # Create single
POST   /api/candidates/bulk              # Bulk create from CSV
GET    /api/candidates/:id               # Get one
PUT    /api/candidates/:id               # Update
DELETE /api/candidates/:id               # Delete
POST   /api/candidates/:id/resume         # Upload resume
POST   /api/candidates/:id/match         # Get matching jobs for candidate
```

### Jobs
```
GET    /api/jobs                         # List (with FILTERS, pagination)
POST   /api/jobs                         # Create (manual)
POST   /api/jobs/bulk                    # Bulk create (CSV/JSON import)
GET    /api/jobs/:id                     # Get one
PUT    /api/jobs/:id                     # Update
DELETE /api/jobs/:id                     # Delete
POST   /api/jobs/sync                    # Trigger portal sync
GET    /api/jobs/:id/candidates          # Get matching candidates for job

# NEW! Filter params for GET /api/jobs:
# ?workType=remote|hybrid|onsite
# ?location=USA|UK|Remote|city name
# ?source=indeed|jobrapido|jooble|manual
# ?datePosted=1|3|7|30 (days)
# ?minMatchScore=70
```

### Applications (Staff Workflow)
```
GET    /api/applications                 # List (my apps, with filters)
GET    /api/applications/queue           # Get pending review queue (Head/Senior)
POST   /api/applications                 # Create single application
POST   /api/applications/bulk            # Generate applications for candidate (up to 60)
GET    /api/applications/:id             # Get one
PUT    /api/applications/:id              # Update (status, notes)
POST   /api/applications/:id/approve     # Approve (Senior/Head only)
POST   /api/applications/:id/reject      # Reject with reason
POST   /api/applications/:id/submit      # Submit to job portal
GET    /api/applications/stats           # Get application stats for staff

# NEW! Auto-fill endpoint
GET    /api/applications/:id/autofill   # Get all candidate data ready to copy/paste
```

### Dashboard
```
GET /api/dashboard/stats                 # Staff personal stats
GET /api/dashboard/activity             # Recent activity
GET /api/dashboard/queue                # How many pending review
```

### Reports (Head Only)
```
GET /api/reports/staff-progress         # All staff progress
GET /api/reports/staff-progress/:id    # Individual staff progress
GET /api/reports/team-stats             # Overall team stats
GET /api/reports/analytics             # Analytics
GET /api/reports/export                # Export CSV
```

---

## 6. Security Implementation

### 6.1 Authentication
- JWT tokens (access: 15min, refresh: 7 days)
- Password hashing with bcrypt (10 rounds)
- Rate limiting on login (5 attempts/15min)

### 6.2 Authorization (RBAC)
```
Head:         All access
Senior Staff: Candidates, Jobs, Applications, Own Progress
Staff:        View Candidates, Jobs, Own Applications
```

### 6.3 Data Security
- AES-256 encryption for sensitive fields
- HTTPS (using self-signed cert for now)
- SQL injection prevention (parameterized queries)
- XSS prevention (output encoding)

---

## 7. Background Jobs (Simplified)

### Option A: In-Memory Queue (No Redis)
```javascript
// Simple job queue without Redis
class JobQueue {
  constructor() {
    this.jobs = [];
    this.processing = false;
  }
  
  async add(job) {
    this.jobs.push(job);
    if (!this.processing) this.process();
  }
  
  async process() {
    this.processing = true;
    while (this.jobs.length > 0) {
      const job = this.jobs.shift();
      await job.execute();
    }
    this.processing = false;
  }
}
```

### Job Types
1. **Resume Parsing:** Process uploaded resumes
2. **Job Sync:** Fetch from portals (simplified)
3. **Matching:** Calculate match scores

---

## 8. Deployment on Low-End Hardware

### 8.1 Production Setup
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/app
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=app
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### 8.2 Server Requirements
- **RAM:** 8GB (2GB for PostgreSQL, 1.5GB for Node.js)
- **CPU:** 4 cores (i5)
- **Storage:** 20GB SSD
- **OS:** Ubuntu 22.04 LTS (free)

### 8.3 Production Commands
```bash
# Build
npm run build

# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Restart
docker-compose restart
```

---

## 9. Work Items

### 9.1 backend-setup
**Category:** infrastructure

Set up Node.js backend with Express and PostgreSQL

**Steps:**
1. Initialize Node.js project
2. Install Express and dependencies
3. Set up Prisma with PostgreSQL
4. Create database schema
5. Set up Express server
6. Add basic middleware
7. Verify server starts

**Verification:**
- Server runs on port 3000
- Database connects

---

### 9.2 database-schema
**Category:** database

Create database schema

**Steps:**
1. Create Prisma schema
2. Run migrations
3. Create seed data
4. Verify tables exist

**Verification:**
- All tables created
- Indexes exist

---

### 9.3 auth-backend
**Category:** security

Implement authentication

**Steps:**
1. Create login endpoint
2. Add JWT generation
3. Add password hashing
4. Create auth middleware
5. Add logout
6. Test auth flow

**Verification:**
- Login works
- Tokens valid
- Protected routes work

---

### 9.4 role-based-access
**Category:** security

Implement RBAC

**Steps:**
1. Define roles
2. Create middleware
3. Apply to routes
4. Test permissions

**Verification:**
- Role access works

---

### 9.5 candidates-api
**Category:** api

Implement candidate CRUD

**Steps:**
1. Create routes
2. Add CRUD handlers
3. Add validation
4. Add search/filter
5. Test endpoints

**Verification:**
- All CRUD works

---

### 9.6 jobs-api
**Category:** api

Implement job CRUD

**Steps:**
1. Create routes
2. Add CRUD handlers
3. Add filters
4. Test endpoints

**Verification:**
- All CRUD works

---

### 9.7 applications-api
**Category:** api

Implement application workflow

**Steps:**
1. Create routes
2. Add workflow handlers
3. Track staff_id
4. Add status updates
5. Test workflow

**Verification:**
- Workflow works

---

### 9.8 compliance-security
**Category:** security

Implement basic security

**Steps:**
1. Add encryption helper
2. Add GDPR fields
3. Add audit logging
4. Test security

**Verification:**
- Encryption works

---

### 9.9 resume-parser
**Category:** core-feature

Implement resume parsing

**Steps:**
1. Set up file handling
2. Add PDF parser
3. Add DOCX parser
4. Extract skills
5. Test parsing

**Verification:**
- Parsing works

---

### 9.10 bulk-candidates
**Category:** feature

Implement bulk candidate upload (CSV)

**Steps:**
1. Create CSV parser for candidates
2. Add bulk insert endpoint
3. Implement batch processing
4. Add progress tracking
5. Handle validation errors
6. Test with 5 candidate CSV

**Verification:**
- Bulk upload works
- Validation works
- Errors reported clearly

---

### 9.11 bulk-applications
**Category:** feature

Implement bulk application generation (60 per candidate)

**Steps:**
1. Create bulk application endpoint
2. Match candidate to jobs (limit 60)
3. Create applications in batches
4. Add rate limiting per staff
5. Test workflow
6. Verify no duplication

**Verification:**
- 60 applications generate
- Batches process correctly
- No duplicates

---

### 9.12 application-workflow-api
**Category:** feature

Implement application review workflow

**Steps:**
1. Create approve endpoint (Senior/Head)
2. Create reject endpoint with reason
3. Add queue endpoint for review
4. Track reviewer
5. Test workflow

**Verification:**
- Approve works
- Reject with reason works
- Queue shows pending

---

### 9.13 staff-progress-api
**Category:** feature

Implement staff progress tracking

**Steps:**
1. Track applications per staff
2. Calculate daily/weekly/monthly
3. Create progress endpoint
4. Add leaderboard logic
5. Test accuracy

**Verification:**
- Progress tracked correctly
- Leaderboard works

---

### 9.14 skill-matching
**Category:** core-feature

Implement skill matching

**Steps:**
1. Create normalizer
2. Add fuzzy matching
3. Calculate scores
4. Create API endpoint
5. Test matching

**Verification:**
- Matching works

---

### 9.15 reports-backend
**Category:** feature

Implement reports

**Steps:**
1. Create staff progress
2. Add metrics calculation
3. Create export
4. Test reports

**Verification:**
- Reports accurate

---

### 9.16 docker-deployment
**Category:** infrastructure

Deploy with Docker

**Steps:**
1. Create Dockerfile
2. Create docker-compose
3. Configure PostgreSQL
4. Test deployment
5. Verify works

**Verification:**
- All runs successfully

---

## 10. Dependencies (Minimal)

```json
{
  "dependencies": {
    "express": "^4.18.0",
    "@prisma/client": "^5.0.0",
    "jsonwebtoken": "^9.0.0",
    "bcrypt": "^5.1.0",
    "zod": "^3.22.0",
    "multer": "^1.4.0",
    "pdf-parse": "^1.1.0",
    "mammoth": "^1.6.0",
    "winston": "^3.11.0",
    "cors": "^2.8.0",
    "helmet": "^7.1.0",
    "express-rate-limit": "^7.0.0"
  },
  "devDependencies": {
    "prisma": "^5.0.0",
    "nodemon": "^3.0.0"
  }
}
```

---

## 11. Acceptance Criteria

1. ✅ API responds < 200ms
2. ✅ Handles 50+ concurrent users
3. ✅ Authentication works
4. ✅ Role-based access (Head/Senior/Staff)
5. ✅ Candidates CRUD
6. ✅ Bulk candidate upload (CSV) works
7. ✅ Jobs CRUD
8. ✅ Bulk job import works
9. ✅ Application workflow (draft → review → approve → submit)
10. ✅ Bulk application generation (60 per candidate)
11. ✅ Resume parsing
12. ✅ Skill matching
13. ✅ Staff progress tracked correctly
14. ✅ Head sees all staff progress
15. ✅ Reports generate with export
16. ✅ Rate limiting prevents blasting
17. ✅ Docker deployment works
18. ✅ Uses < 6GB RAM
19. ✅ All free tools

---

## 12. Realistic Load (200 Staff)

```
Daily:
- 1,000 new candidates (200 staff × 5)
- 60,000 job matches calculated
- 6,000 applications submitted

Per second (average):
- 12 applications/minute
- 700 matches/hour

This is manageable on 8GB RAM with:
- Batch processing
- Proper indexing
- Background matching
```

---

## 13. Skip Conditions

- Skip Redis if RAM constrained
- Skip complex caching
- Skip advanced monitoring
- Skip SSO (use local auth)
- Skip advanced OCR (basic extraction)
