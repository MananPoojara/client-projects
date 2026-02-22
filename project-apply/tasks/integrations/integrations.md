# Job Discovery System - Integrations Architecture

## Document Information
- **Version:** 1.4 (Auto-Fill Forms + Filters)
- **Last Updated:** 2026-02-21
- **Target Hardware:** 8GB RAM, Intel i5 (4 cores)
- **Budget:** $0 (Open Source Only)

---

## 0. THE REAL QUESTION: What Can Be Automated?

### Current Manual Process
```
Staff does manually (per candidate, per job):
1. Login to job portal (Indeed, LinkedIn, etc.)
2. Create candidate account on portal OR use existing
3. Upload resume (PDF/DOCX) to portal
4. Search for jobs on portal
5. Fill application form (name, experience, etc.) ← WE CAN HELP HERE!
6. Upload tailored resume
7. Submit application
8. Repeat 60 times per candidate
```

### The Hard Truth

| Step | Can Auto? | Why |
|------|-----------|-----|
| Create portal account | ❌ NO | Anti-bot, CAPTCHA, phone verification |
| Upload resume TO portal | ❌ NO | Requires browser session, CAPTCHA |
| Submit application | ❌ NO | Blocks automation, CAPTCHA |
| Upload resume to portal | ❌ NO | Requires browser session, CAPTCHA |
| Fill application form | ⚠️ HARD | Different per portal, anti-bot |
| Submit application | ❌ NO | Blocks automation, CAPTCHA |
| **Job Discovery** | ✅ YES | Search/aggregate jobs from portals |
| **Resume Parsing** | ✅ YES | Extract skills from PDF/DOCX |
| **Application Prep** | ✅ PARTIAL | Generate cover letter, tailor resume locally |

### What We Can Actually Automate

```
✅ AUTOMATE (This System):
├── 1. Job Discovery
│   ├── Scrape jobs from multiple portals
│   ├── Aggregate in one dashboard
│   └── Notify of new matching jobs
├── 2. Resume Parsing
│   ├── Extract text from PDF/DOCX
│   ├── Extract skills, experience
│   └── Store in database
├── 3. Job Matching
│   ├── Match candidate skills to job requirements
│   ├── Score matches
│   └── Present ranked list to staff
├── 4. Application Preparation (LOCAL)
│   ├── Generate cover letter (local template)
│   ├── Tailor resume (local PDF generation)
│   └── Auto-fill form answers ← NEW!
└── 5. Staff Workflow
    ├── Track applications per staff
    ├── Dashboard with filters (remote/hybrid/onsite)
    └── Head can see team progress

❌ MANUAL (Staff Must Do):
├── 1. Create candidate account on portal
├── 2. Upload resume to portal
├── 3. Click submit on portal
└── 4. Portal login verification

✅ AUTO-FILL FORMS (NEW!):
When staff clicks "Apply" on a job in our system:
- Show popup with ALL candidate answers ready
- Staff just copy-pastes to portal form
- No need to remember/lookup candidate details
```

### Auto-Fill Forms Feature

```
Staff view when applying (in our system):

┌─────────────────────────────────────────────────┐
│  APPLICATION DATA - Ready to Copy/Paste          │
├─────────────────────────────────────────────────┤
│                                                 │
│  BASIC INFO (click to copy):                    │
│  ─────────────────────────────                   │
│  Full Name: John Doe                 [📋 Copy]  │
│  Email: john@email.com               [📋 Copy]  │
│  Phone: +1 234 567 8900             [📋 Copy]  │
│  Location: New York, NY              [📋 Copy]  │
│                                                 │
│  EXPERIENCE (click to copy):                    │
│  ────────────────────────────                   │
│  Current Job: Software Engineer                 │
│  Current Company: Tech Corp                    │
│  Years Experience: 5                           │
│                                                 │
│  EDUCATION (click to copy):                    │
│  ────────────────────────                      │
│  Degree: Bachelor of Science                    │
│  Field: Computer Science                        │
│  University: NYU                               │
│                                                 │
│  SKILLS (click to copy):                       │
│  ─────────────────────                         │
│  JavaScript, React, Node.js, Python            │
│                                                 │
│  [Open Portal]  [Skip for Now]                 │
└─────────────────────────────────────────────────┘
```

### Dashboard Filters (Remote/Hybrid/Onsite)

```
Jobs page filters:
├── All Jobs
├── Work Type:
│   ├── 🔴 Remote
│   ├── 🟡 Hybrid  
│   └── 🔵 Onsite
├── Location:
│   ├── USA
│   ├── UK
│   ├── Remote
│   └── [Search city...]
├── Source:
│   ├── Indeed
│   ├── Jobrapido
│   ├── Jooble
│   └── Manual
├── Date Posted:
│   ├── Last 24 hours
│   ├── Last 3 days
│   ├── Last 7 days
│   └── Any time
└── Match Score:
    ├── 90%+
    ├── 70%+
    └── Any
```

---

## What We AUTOMATE (Summary)
- Have pre-prepared cover letters & tailored resumes ready
- Just copy-paste to portal and submit
```

---

## 1. Real-World Constraints

### The Anti-Bot Reality

```
Indeed:     Blocks automated submissions - requires CAPTCHA
LinkedIn:  Blocks scrapers heavily - needs premium API
ZipRecruiter: Blocks automation - needs enterprise API
Glassdoor:  Heavy rate limiting

These portals make money from:
1. Employers paying to post jobs
2. Employers paying to search candidates

They DON'T want:
- Third-party systems submitting applications
- Bypassing their application tracking

SOLUTION: We only SCRAPE job listings (public data)
We DON'T submit applications (which would be blocked)
```

### Job Portals (No API Keys)
Based on your requirements - using smaller, scrapable portals:

| Portal | URL | Status | Difficulty |
|--------|-----|--------|------------|
| Jobrapido | jobrapido.com | ✅ Test first | Easy |
| Jooble | jooble.org | ✅ Good alternative | Easy |
| Indeed (limited) | indeed.com | ✅ Basic scraping | Medium |
| CVLibrary | cvlibrary.co.uk | ✅ UK focused | Medium |
| Reed | reed.co.uk | ✅ UK focused | Medium |
| Monster (limited) | monster.com | ⚠️ Heavy blocks | Hard |
| Careerjet | careerjet.com | ✅ Works | Easy |

### Workflow Reality
```
1 Staff Member = 5 Candidates
Each Candidate = 60 Applications (average)

Daily Load for 1 Staff:
- 5 candidates × 60 jobs = 300 job matches to review
- ~20-30 applications submitted per day

Team of 200 Staff:
- 200 × 30 = 6,000 applications/day
- 200 × 5 = 1,000 new candidates/week
```

### Scalability Requirements
- Code must NOT blast - use queues and rate limiting
- Process in batches, not all at once
- Stagger jobs over time
- Handle failures gracefully

---

## 2. Job Portal Integrations

### 2.1 Architecture (Rate-Limited by Design)

```javascript
// NEVER blast - always rate limit
class PortalScraper {
  constructor() {
    // Strict limits per portal
    this.limits = {
      jobrapido: { requests: 5, delay: 2000 },    // 5 req, 2s between
      jooble: { requests: 10, delay: 1000 },      // 10 req, 1s between
      indeed: { requests: 3, delay: 5000 },       // 3 req, 5s between
      cvlibrary: { requests: 5, delay: 3000 }     // 5 req, 3s between
    };
  }
  
  async searchJobs(portal, query) {
    const limit = this.limits[portal];
    
    // ALWAYS wait between requests
    await this.wait(limit.delay);
    
    // Fetch with retry logic
    return this.fetchWithRetry(portal, query, 3);
  }
}
```

### 2.2 Jobrapido Scraper
```javascript
// Jobrapido - typically easier to scrape
class JobrapidoScraper {
  constructor() {
    this.baseUrl = 'https://jobrapido.com';
    this.delay = 2000; // 2 seconds between requests
  }
  
  async searchJobs(query) {
    const url = `${this.baseUrl}/jobs?q=${encodeURIComponent(query.keywords)}&l=${encodeURIComponent(query.location || '')}`;
    
    const response = await axios.get(url, {
      headers: { 
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
      },
      timeout: 15000
    });
    
    const $ = cheerio.load(response.data);
    const jobs = [];
    
    // Jobrapido typically uses structured data
    $('.job-item').each((i, el) => {
      if (i > 20) return;
      
      const job = {
        id: `jobrapido_${$(el).attr('data-id')}`,
        title: $(el).find('.job-title').text().trim(),
        company: $(el).find('.company').text().trim(),
        location: $(el).find('.location').text().trim(),
        description: $(el).find('.snippet').text().trim(),
        url: $(el).find('a.job-link').attr('href'),
        sourcePortal: 'jobrapido',
        salary: $(el).find('.salary').text().trim(),
        postedDate: this.parseDate($(el).find('.date').text())
      };
      
      if (job.title) jobs.push(job);
    });
    
    return jobs;
  }
}
```

### 2.3 Jooble Scraper
```javascript
// Jooble - often has API or easy scraping
class JoobleScraper {
  constructor() {
    this.baseUrl = 'https://jooble.org';
    this.delay = 1000;
  }
  
  async searchJobs(query) {
    // Jooble may block, try direct URL first
    const url = `${this.baseUrl}/jobs/${this.slugify(query.keywords)}`;
    
    const response = await axios.get(url, {
      headers: { 'User-Agent': 'Mozilla/5.0...' },
      timeout: 15000
    });
    
    const $ = cheerio.load(response.data);
    const jobs = [];
    
    $('.job').each((i, el) => {
      if (i > 15) return;
      
      jobs.push({
        id: `jooble_${$(el).attr('data-id')}`,
        title: $(el).find('h2').text().trim(),
        company: $(el).find('.company').text().trim(),
        location: $(el).find('.location').text().trim(),
        description: $(el).find('.description').text().trim().substring(0, 500),
        url: $(el).find('a').attr('href'),
        sourcePortal: 'jooble',
        salary: $(el).find('.salary').text().trim()
      });
    });
    
    return jobs;
  }
  
  slugify(text) {
    return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  }
}
```

### 2.4 Batch Sync (Never Blast)
```javascript
// Smart batch processing - staggered
class BatchSync {
  constructor(scrapers, db) {
    this.scrapers = scrapers;
    this.db = db;
    this.running = false;
  }
  
  // Sync jobs in small batches over time
  async syncAllPortals() {
    if (this.running) {
      console.log('Sync already running, skipping...');
      return;
    }
    
    this.running = true;
    
    try {
      // Phase 1: Jobrapido (5 jobs, wait, 5 more...)
      await this.syncPortalInBatches('jobrapido', { keywords: 'software developer' }, 5, 3000);
      
      // Phase 2: Jooble (10 jobs, wait, 10 more...)
      await this.syncPortalInBatches('jooble', { keywords: 'software developer' }, 10, 2000);
      
      // Phase 3: Indeed (3 jobs, wait, 3 more...)
      await this.syncPortalInBatches('indeed', { keywords: 'software developer' }, 3, 5000);
      
    } finally {
      this.running = false;
    }
  }
  
  async syncPortalInBatches(portal, query, batchSize, waitBetween) {
    let page = 0;
    let hasMore = true;
    
    while (hasMore) {
      // Get batch
      const jobs = await this.scrapers[portal].searchJobs({
        ...query,
        page
      });
      
      if (jobs.length === 0) {
        hasMore = false;
        break;
      }
      
      // Save batch to DB
      await this.saveBatch(jobs);
      
      console.log(`Synced ${jobs.length} jobs from ${portal} (page ${page})`);
      
      // Wait before next batch - NEVER blast
      await this.wait(waitBetween);
      
      page++;
      
      // Safety limit
      if (page > 10) break;
    }
  }
  
  async saveBatch(jobs) {
    for (const job of jobs) {
      await this.db.jobs.upsert({
        where: { id: job.id },
        update: job,
        create: job
      });
    }
  }
  
  wait(ms) {
    return new Promise(r => setTimeout(r, ms));
  }
}
```

---

## 3. Bulk Resume Upload (Staff Workflow)

### 3.1 Bulk Upload Flow
```javascript
// Each staff handles 5 candidates → need bulk upload
class BulkResumeUploader {
  async uploadMultiple(file) {
    // Parse CSV with candidate info
    const candidates = await this.parseCSV(file);
    
    // Process in small batches (not all at once)
    const results = [];
    const batchSize = 3; // Only 3 at a time
    
    for (let i = 0; i < candidates.length; i += batchSize) {
      const batch = candidates.slice(i, i + batchSize);
      
      // Process batch
      const batchResults = await Promise.all(
        batch.map(c => this.processCandidate(c))
      );
      
      results.push(...batchResults);
      
      // Wait between batches
      if (i + batchSize < candidates.length) {
        await this.wait(2000);
      }
    }
    
    return results;
  }
  
  async processCandidate(data) {
    // 1. Parse resume if uploaded
    let parsedData = {};
    if (data.resumePath) {
      parsedData = await this.parseResume(data.resumePath);
    }
    
    // 2. Create candidate record
    const candidate = await this.db.candidates.create({
      data: {
        firstName: data.firstName,
        lastName: data.lastName,
        email: data.email,
        phone: data.phone,
        location: data.location,
        skills: parsedData.skills || data.skills || [],
        experienceYears: parsedData.experienceYears || data.experienceYears,
        resumePath: data.resumePath,
        status: 'active',
        createdBy: data.staffId
      }
    });
    
    return candidate;
  }
}
```

### 3.2 Bulk Application Generation
```javascript
// 60 applications per candidate - need smart batching
class BulkApplicationGenerator {
  async generateApplications(candidateId, jobFilters, staffId) {
    // Get matching jobs (limit to 60)
    const matchingJobs = await this.matchingService.findMatchingJobs(
      candidateId,
      { ...jobFilters, limit: 60 }
    );
    
    const applications = [];
    
    // Create applications in batches (not all 60 at once)
    const batchSize = 10;
    
    for (let i = 0; i < matchingJobs.length; i += batchSize) {
      const batch = matchingJobs.slice(i, i + batchSize);
      
      const batchApps = await Promise.all(
        batch.map(job => this.createApplication({
          candidateId,
          jobId: job.id,
          staffId,
          status: 'draft'
        }))
      );
      
      applications.push(...batchApps);
      
      // Small delay between batches
      if (i + batchSize < matchingJobs.length) {
        await this.wait(500);
      }
    }
    
    return applications;
  }
}
```

---

## 4. Queue System (Prevent Blasting)

### 4.1 In-Memory Queue (No Redis)
```javascript
// Simple queue that won't blast the system
class JobQueue {
  constructor() {
    this.queue = [];
    this.processing = false;
    this.maxConcurrent = 3; // Only 3 jobs at a time
    this.currentlyRunning = 0;
  }
  
  async add(job) {
    return new Promise((resolve, reject) => {
      this.queue.push({ job, resolve, reject });
      this.process();
    });
  }
  
  async process() {
    if (this.processing) return;
    if (this.currentlyRunning >= this.maxConcurrent) return;
    if (this.queue.length === 0) return;
    
    this.processing = true;
    
    while (this.queue.length > 0 && this.currentlyRunning < this.maxConcurrent) {
      const { job, resolve, reject } = this.queue.shift();
      this.currentlyRunning++;
      
      try {
        const result = await job.execute();
        resolve(result);
      } catch (error) {
        reject(error);
      } finally {
        this.currentlyRunning--;
      }
    }
    
    this.processing = false;
  }
}
```

### 4.2 Queue Types
```javascript
// Define job types with priorities
const QueueTypes = {
  RESUME_PARSING: { priority: 1, concurrency: 2, timeout: 30000 },
  JOB_SYNC: { priority: 2, concurrency: 1, timeout: 60000 },
  MATCHING: { priority: 3, concurrency: 2, timeout: 45000 },
  NOTIFICATION: { priority: 4, concurrency: 5, timeout: 10000 }
};

class PriorityQueue {
  constructor() {
    this.queues = {
      high: [],
      medium: [],
      low: []
    };
  }
  
  add(job, priority = 'medium') {
    // Add to appropriate queue
    this.queues[priority].push(job);
  }
  
  async process() {
    // Process high priority first
    for (const priority of ['high', 'medium', 'low']) {
      const job = this.queues[priority].shift();
      if (job) {
        await job.execute();
        await this.wait(1000); // 1s between jobs
      }
    }
  }
}
```

---

## 5. Rate Limiting (Strict)

### 5.1 Per-User Rate Limiter
```javascript
// Each staff member limited to prevent abuse
class StaffRateLimiter {
  constructor() {
    this.limits = {
      jobSearch: { count: 50, window: 60000 },     // 50 searches per minute
      applicationSubmit: { count: 10, window: 60000 }, // 10 apps per minute
      candidateCreate: { count: 20, window: 60000 } // 20 candidates per minute
    };
    
    this.requests = new Map();
  }
  
  async check(staffId, action) {
    const limit = this.limits[action];
    const key = `${staffId}_${action}`;
    
    const now = Date.now();
    const requests = this.requests.get(key) || [];
    
    // Remove old requests
    const recent = requests.filter(t => now - t < limit.window);
    
    if (recent.length >= limit.count) {
      throw new Error(`Rate limit exceeded. Try again in ${Math.ceil((recent[0] + limit.window - now)/1000)} seconds`);
    }
    
    recent.push(now);
    this.requests.set(key, recent);
  }
}
```

### 5.2 Portal Rate Limiter
```javascript
// Never blast portals
class PortalRateLimiter {
  constructor() {
    this.lastRequest = {};
    this.delays = {
      jobrapido: 2000,  // 2 seconds
      jooble: 1000,     // 1 second
      indeed: 5000,      // 5 seconds
      cvlibrary: 3000   // 3 seconds
    };
  }
  
  async waitFor(portal) {
    const delay = this.delays[portal] || 2000;
    const last = this.lastRequest[portal] || 0;
    
    const waitTime = Math.max(0, delay - (Date.now() - last));
    
    if (waitTime > 0) {
      console.log(`Waiting ${waitTime}ms for ${portal}...`);
      await new Promise(r => setTimeout(r, waitTime));
    }
    
    this.lastRequest[portal] = Date.now();
  }
}
```

---

## 6. Retry Logic (Graceful Failure)

### 6.1 Retry with Backoff
```javascript
// Don't fail immediately - retry with backoff
async function withRetry(fn, maxRetries = 3) {
  let lastError;
  
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      // Don't retry on certain errors
      if (error.statusCode === 404 || error.statusCode === 401) {
        throw error;
      }
      
      // Exponential backoff: 1s, 2s, 4s
      const waitTime = Math.pow(2, attempt) * 1000;
      console.log(`Retry ${attempt + 1} after ${waitTime}ms...`);
      await new Promise(r => setTimeout(r, waitTime));
    }
  }
  
  throw lastError;
}
```

### 6.2 Circuit Breaker
```javascript
// Stop calling a portal if it's failing
class CircuitBreaker {
  constructor() {
    this.failures = {};
    this.threshold = 3;
    this.timeout = 60000; // 1 minute
  }
  
  async call(portal, fn) {
    if (this.isOpen(portal)) {
      throw new Error(`Circuit breaker open for ${portal}`);
    }
    
    try {
      return await fn();
    } catch (error) {
      this.recordFailure(portal);
      throw error;
    }
  }
  
  isOpen(portal) {
    const failure = this.failures[portal];
    if (!failure) return false;
    
    if (failure.count >= this.threshold) {
      // Check if timeout has passed
      if (Date.now() - failure.firstFailure > this.timeout) {
        this.reset(portal);
        return false;
      }
      return true;
    }
    return false;
  }
  
  recordFailure(portal) {
    if (!this.failures[portal]) {
      this.failures[portal] = { count: 0, firstFailure: Date.now() };
    }
    this.failures[portal].count++;
  }
  
  reset(portal) {
    delete this.failures[portal];
  }
}
```

---

## 7. Scalability Considerations

### 7.1 Database Indexing (Critical)
```sql
-- Indexes for performance with large data
CREATE INDEX idx_candidates_status ON candidates(status);
CREATE INDEX idx_candidates_skills ON candidates USING GIN(skills);
CREATE INDEX idx_candidates_staff ON candidates(created_by);

CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_skills ON jobs USING GIN(skills_required);
CREATE INDEX idx_jobs_company ON jobs(company);

CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_candidate ON applications(candidate_id);
CREATE INDEX idx_applications_job ON applications(job_id);
CREATE INDEX idx_applications_staff ON applications(staff_id);

-- For matching queries
CREATE INDEX idx_applications_created ON applications(created_at DESC);
```

### 7.2 Pagination (Always)
```javascript
// Always paginate - never load all at once
async function getCandidates({ page = 1, limit = 25 }) {
  return db.candidates.findMany({
    skip: (page - 1) * limit,
    take: limit,
    orderBy: { createdAt: 'desc' }
  });
}
```

### 7.3 Caching (Reduce DB Load)
```javascript
// Simple in-memory cache
class Cache {
  constructor() {
    this.store = new Map();
    this.ttl = 60000; // 1 minute
  }
  
  get(key) {
    const item = this.store.get(key);
    if (!item) return null;
    
    if (Date.now() > item.expires) {
      this.store.delete(key);
      return null;
    }
    
    return item.value;
  }
  
  set(key, value, ttl = this.ttl) {
    this.store.set(key, {
      value,
      expires: Date.now() + ttl
    });
  }
}
```

---

## 8. Work Items

### 8.1 job-portal-scrapers
**Category:** integration

Implement scrapers for Jobrapido, Jooble, and other small portals

**Steps:**
1. Set up Cheerio-based scraper architecture
2. Create Jobrapido scraper with rate limiting
3. Create Jooble scraper
4. Add CVLibrary scraper
5. Implement circuit breaker
6. Test scraping
7. Verify data saving

**Verification:**
- All portals scrape successfully
- Rate limiting enforced
- Circuit breaker works

---

### 8.2 bulk-resume-system
**Category:** feature

Implement bulk resume upload for staff workflow

**Steps:**
1. Create bulk CSV upload
2. Implement batch processing
3. Add progress tracking
4. Handle errors gracefully
5. Test with sample data

**Verification:**
- Bulk upload works
- Batches process correctly

---

### 8.3 bulk-application-generator
**Category:** feature

Implement bulk application generation (60 per candidate)

**Steps:**
1. Create bulk application generator
2. Implement batch creation
3. Add rate limiting
4. Test workflow

**Verification:**
- 60 applications generate correctly
- Batches process without blasting

---

### 8.4 queue-system
**Category:** infrastructure

Implement queue system to prevent blasting

**Steps:**
1. Create in-memory queue
2. Add priority support
3. Implement concurrency limits
4. Add retry logic
5. Test queue processing

**Verification:**
- Jobs process in order
- No system overload

---

### 8.5 rate-limiting
**Category:** security

Implement strict rate limiting

**Steps:**
1. Add per-user rate limits
2. Add portal rate limits
3. Implement circuit breaker
4. Test limits

**Verification:**
- Rate limits enforced
- Circuit breaker works

---

### 8.6 database-optimization
**Category:** optimization

Optimize database for scale

**Steps:**
1. Add all necessary indexes
2. Verify query performance
3. Add pagination everywhere
4. Test with large data

**Verification:**
- Queries fast
- No N+1 problems

---

## 9. Acceptance Criteria

1. ✅ Jobrapido scrapes successfully
2. ✅ Jooble scrapes successfully
3. ✅ Rate limiting enforced (no blasting)
4. ✅ Bulk resume upload works
5. ✅ 60 applications generate per candidate
6. ✅ Queue processes jobs in batches
7. ✅ Circuit breaker prevents overload
8. ✅ Database queries optimized
9. ✅ Pagination everywhere
10. ✅ Works on 8GB RAM

---

## 10. Realistic Workflow

### Daily Staff Workflow
```
Morning:
1. Upload 5 candidates (bulk CSV) → 2 minutes
2. System matches each to 60 jobs → background
3. Review 300 matches → 30 minutes

Throughout day:
4. Review applications → approve/reject
5. Submit approved → 20-30 applications

Evening:
6. Check next day's queue
```

### System Load
- 200 staff × 5 candidates = 1,000 new candidates/day
- 1,000 × 60 = 60,000 applications to process
- Process in batches over 2-3 hours
- Average: 10-15 applications/second

This is manageable on 8GB RAM with proper batching.
