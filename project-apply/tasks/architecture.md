# Job Discovery System - Clean Architecture

## Project Overview

**System Name:** Job Discovery & Application Preparation System  
**Purpose:** Internal tool for 200 staff to automate job discovery and application preparation for candidates  
**Automation Scope:** Job scraping, resume parsing, skill matching, application prep (NOT portal submission)

---

## Bounded Contexts (DDD)

Based on the domain, we have 4 bounded contexts:

```
┌─────────────────────────────────────────────────────────────────┐
│                     JOB DISCOVERY SYSTEM                        │
├─────────────────┬─────────────────┬─────────────────┬──────────┤
│   CANDIDATE     │      JOB        │  APPLICATION    │   STAFF   │
│    CONTEXT      │    CONTEXT      │    CONTEXT       │  CONTEXT  │
├─────────────────┼─────────────────┼─────────────────┼──────────┤
│ • Candidate     │ • Job Listing   │ • Application   │ • Staff   │
│ • Resume        │ • Job Portal    │ • Workflow      │ • Role    │
│ • Skills        │ • Job Sync      │ • Cover Letter │ • Progress│
│ • Experience    │ • Job Matching  │ • Auto-Fill    │ • Team    │
└─────────────────┴─────────────────┴─────────────────┴──────────┘
```

---

## Layer Architecture (Clean Architecture)

```
┌────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                      │
│  (React Pages, Components, Hooks)                        │
├────────────────────────────────────────────────────────────┤
│                    APPLICATION LAYER                       │
│  (Use Cases, DTOs, Application Services)                  │
├────────────────────────────────────────────────────────────┤
│                      DOMAIN LAYER                          │
│  (Entities, Value Objects, Domain Services, Interfaces)    │
├────────────────────────────────────────────────────────────┤
│                  INFRASTRUCTURE LAYER                     │
│  (Database, External APIs, File Storage, Scrapers)        │
└────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

### Backend (Node.js + Express)

```
backend/
├── src/
│   ├── main.ts                      # Entry point
│   ├── app.ts                        # Express app configuration
│   │
│   ├── domain/                      # DOMAIN LAYER (innermost)
│   │   ├── entities/               # Core business entities
│   │   │   ├── Candidate.ts
│   │   │   ├── Job.ts
│   │   │   ├── Application.ts
│   │   │   └── Staff.ts
│   │   ├── value-objects/         # Immutable value objects
│   │   │   ├── Email.ts
│   │   │   ├── PhoneNumber.ts
│   │   │   ├── SkillSet.ts
│   │   │   └── MatchScore.ts
│   │   ├── domain-services/        # Business logic
│   │   │   ├── CandidateMatchingService.ts
│   │   │   ├── ApplicationWorkflowService.ts
│   │   │   └── CoverLetterGenerator.ts
│   │   └── repositories/           # Repository interfaces
│   │       ├── ICandidateRepository.ts
│   │       ├── IJobRepository.ts
│   │       ├── IApplicationRepository.ts
│   │       └── IStaffRepository.ts
│   │
│   ├── application/                # APPLICATION LAYER
│   │   ├── use-cases/            # Use case implementations
│   │   │   ├── candidates/
│   │   │   │   ├── CreateCandidateUseCase.ts
│   │   │   │   ├── UploadResumeUseCase.ts
│   │   │   │   ├── GetCandidatesUseCase.ts
│   │   │   │   └── BulkCreateCandidatesUseCase.ts
│   │   │   ├── jobs/
│   │   │   │   ├── SearchJobsUseCase.ts
│   │   │   │   ├── SyncJobsUseCase.ts
│   │   │   │   └── ImportJobsUseCase.ts
│   │   │   ├── applications/
│   │   │   │   ├── CreateApplicationUseCase.ts
│   │   │   │   ├── BulkCreateApplicationsUseCase.ts
│   │   │   │   ├── ApproveApplicationUseCase.ts
│   │   │   │   └── GetAutoFillDataUseCase.ts
│   │   │   └── staff/
│   │   │       ├── LoginUseCase.ts
│   │   │       ├── GetStaffProgressUseCase.ts
│   │   │       └── GetTeamLeaderboardUseCase.ts
│   │   ├── dto/                   # Data Transfer Objects
│   │   │   ├── CandidateDTO.ts
│   │   │   ├── JobDTO.ts
│   │   │   └── ApplicationDTO.ts
│   │   └── services/              # Application services
│   │       ├── AuthenticationService.ts
│   │       └── NotificationService.ts
│   │
│   ├── infrastructure/            # INFRASTRUCTURE LAYER (outermost)
│   │   ├── database/
│   │   │   ├── prisma/
│   │   │   │   ├── schema.prisma
│   │   │   │   └── migrations/
│   │   │   ├── repositories/     # Repository implementations
│   │   │   │   ├── PrismaCandidateRepository.ts
│   │   │   │   ├── PrismaJobRepository.ts
│   │   │   │   └── PrismaApplicationRepository.ts
│   │   │   └── DatabaseConfig.ts
│   │   ├── external/
│   │   │   ├── scrapers/         # Job portal scrapers
│   │   │   │   ├── JobrapidoScraper.ts
│   │   │   │   ├── JoobleScraper.ts
│   │   │   │   ├── IndeedScraper.ts
│   │   │   │   └── ScraperFactory.ts
│   │   │   ├── parsers/          # Resume parsers
│   │   │   │   ├── PDFResumeParser.ts
│   │   │   │   ├── DOCXResumeParser.ts
│   │   │   │   └── ResumeParserFactory.ts
│   │   │   └── rate-limiter/
│   │   │       ├── PortalRateLimiter.ts
│   │   │       └── CircuitBreaker.ts
│   │   └── queue/
│   │       ├── InMemoryQueue.ts   # For 8GB RAM constraint
│   │       └── JobProcessor.ts
│   │
│   ├── presentation/              # PRESENTATION LAYER
│   │   ├── routes/
│   │   │   ├── auth.routes.ts
│   │   │   ├── candidate.routes.ts
│   │   │   ├── job.routes.ts
│   │   │   ├── application.routes.ts
│   │   │   └── dashboard.routes.ts
│   │   ├── controllers/
│   │   │   ├── CandidateController.ts
│   │   │   ├── JobController.ts
│   │   │   ├── ApplicationController.ts
│   │   │   └── DashboardController.ts
│   │   └── middleware/
│   │       ├── auth.middleware.ts
│   │       ├── rbac.middleware.ts
│   │       └── validation.middleware.ts
│   │
│   └── shared/                   # SHARED KERNEL
│       ├── errors/
│       │   ├── NotFoundError.ts
│       │   ├── UnauthorizedError.ts
│       │   └── ValidationError.ts
│       ├── utils/
│       │   └── date.utils.ts
│       └── constants/
│           └── index.ts
│
├── tests/
│   ├── domain/
│   ├── application/
│   └── infrastructure/
│
├── docker-compose.yml
├── Dockerfile
├── package.json
└── tsconfig.json
```

### Frontend (React + Vite)

```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   │
│   ├── domain/                    # Domain interfaces (shared with backend)
│   │   └── types/
│   │       ├── Candidate.ts
│   │       ├── Job.ts
│   │       └── Application.ts
│   │
│   ├── application/               # Application layer
│   │   ├── api/                  # API client
│   │   │   ├── apiClient.ts
│   │   │   ├── candidateApi.ts
│   │   │   ├── jobApi.ts
│   │   │   └── applicationApi.ts
│   │   └── hooks/               # Custom hooks (use cases)
│   │       ├── useCandidates.ts
│   │       ├── useJobs.ts
│   │       ├── useApplications.ts
│   │       └── useAuth.ts
│   │
│   ├── presentation/              # Presentation layer
│   │   ├── components/           # Shared UI components
│   │   │   ├── common/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   ├── DataTable.tsx
│   │   │   │   └── StatusBadge.tsx
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Layout.tsx
│   │   │   └── features/         # Feature-specific components
│   │   │       ├── candidates/
│   │   │       ├── jobs/
│   │   │       └── applications/
│   │   │
│   │   ├── pages/                # Page components
│   │   │   ├── Login.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── HeadDashboard.tsx
│   │   │   ├── Candidates.tsx
│   │   │   ├── Jobs.tsx
│   │   │   ├── Applications.tsx
│   │   │   └── Reports.tsx
│   │   │
│   │   └── contexts/             # React contexts
│   │       ├── AuthContext.tsx
│   │       └── NotificationContext.tsx
│   │
│   └── assets/
│
├── public/
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

---

## Domain Entities

### Candidate Entity

```typescript
// domain/entities/Candidate.ts
export class Candidate {
  private readonly id: string;
  private name: Name;
  private email: Email;
  private phone?: PhoneNumber;
  private location?: string;
  private skills: SkillSet;
  private experienceYears?: number;
  private resume?: Resume;
  private status: CandidateStatus;
  private createdBy: string;
  private createdAt: Date;
  private updatedAt: Date;

  constructor(props: CandidateProps) {
    this.id = props.id ?? generateUUID();
    this.name = new Name(props.firstName, props.lastName);
    this.email = new Email(props.email);
    this.phone = props.phone ? new PhoneNumber(props.phone) : undefined;
    this.skills = new SkillSet(props.skills ?? []);
    // ...
  }

  matchWithJob(job: Job): MatchScore {
    return this.skills.calculateMatchScore(job.getRequiredSkills());
  }

  addResume(resume: Resume): void {
    this.resume = resume;
    this.updatedAt = new Date();
  }

  // Value objects prevent invalid states
}
```

### Job Entity

```typescript
// domain/entities/Job.ts
export class Job {
  private readonly id: string;
  private title: string;
  private company: string;
  private location?: string;
  private description?: string;
  private requiredSkills: SkillSet;
  private workType: WorkType;  // Remote, Hybrid, Onsite
  private source: JobSource;
  private status: JobStatus;
  private postedDate?: Date;

  getRequiredSkills(): SkillSet {
    return this.requiredSkills;
  }

  matchesCandidate(candidate: Candidate): boolean {
    const score = candidate.matchWithJob(this);
    return score.isAboveThreshold(60);
  }
}
```

### Application Entity

```typescript
// domain/entities/Application.ts
export class Application {
  private readonly id: string;
  private candidateId: string;
  private jobId: string;
  private staffId: string;
  private status: ApplicationStatus;
  private coverLetter?: string;
  private tailoredResumePath?: string;
  private staffNotes?: string;
  private reviewerId?: string;
  private reviewedAt?: Date;
  private submittedAt?: Date;

  approve(reviewerId: string): void {
    this.status = ApplicationStatus.APPROVED;
    this.reviewerId = reviewerId;
    this.reviewedAt = new Date();
  }

  submit(): void {
    if (this.status !== ApplicationStatus.APPROVED) {
      throw new DomainError('Can only submit approved applications');
    }
    this.status = ApplicationStatus.SUBMITTED;
    this.submittedAt = new Date();
  }
}
```

---

## Use Cases (Application Layer)

### Example: Create Application Use Case

```typescript
// application/use-cases/applications/CreateApplicationUseCase.ts
export class CreateApplicationUseCase {
  constructor(
    private applicationRepo: IApplicationRepository,
    private candidateRepo: ICandidateRepository,
    private jobRepo: IJobRepository,
    private coverLetterGenerator: CoverLetterGenerator
  ) {}

  async execute(dto: CreateApplicationDTO): Promise<ApplicationDTO> {
    // 1. Validate candidate exists
    const candidate = await this.candidateRepo.findById(dto.candidateId);
    if (!candidate) {
      throw new NotFoundError('Candidate not found');
    }

    // 2. Validate job exists
    const job = await this.jobRepo.findById(dto.jobId);
    if (!job) {
      throw new NotFoundError('Job not found');
    }

    // 3. Check if application already exists
    const existing = await this.applicationRepo.findByCandidateAndJob(
      dto.candidateId,
      dto.jobId
    );
    if (existing) {
      throw new ValidationError('Application already exists');
    }

    // 4. Generate cover letter
    const coverLetter = await this.coverLetterGenerator.generate(
      candidate,
      job
    );

    // 5. Create application
    const application = new Application({
      candidateId: dto.candidateId,
      jobId: dto.jobId,
      staffId: dto.staffId,
      status: ApplicationStatus.DRAFT,
      coverLetter
    });

    // 6. Save
    await this.applicationRepo.save(application);

    // 7. Return DTO
    return ApplicationDTO.fromEntity(application);
  }
}
```

---

## Infrastructure Implementations

### Repository Pattern

```typescript
// infrastructure/database/repositories/PrismaCandidateRepository.ts
export class PrismaCandidateRepository implements ICandidateRepository {
  constructor(private prisma: PrismaClient) {}

  async findById(id: string): Promise<Candidate | null> {
    const data = await this.prisma.candidate.findUnique({
      where: { id }
    });
    return data ? CandidateMapper.toDomain(data) : null;
  }

  async findAll(filters: CandidateFilters): Promise<PaginatedResult<Candidate>> {
    const [items, total] = await Promise.all([
      this.prisma.candidate.findMany({
        where: filters.toPrismaWhere(),
        skip: filters.offset,
        take: filters.limit,
        orderBy: { createdAt: 'desc' }
      }),
      this.prisma.candidate.count({ where: filters.toPrismaWhere() })
    ]);

    return {
      items: items.map(CandidateMapper.toDomain),
      total,
      page: filters.page,
      limit: filters.limit
    };
  }

  async save(candidate: Candidate): Promise<void> {
    const data = CandidateMapper.toPrisma(candidate);
    await this.prisma.candidate.upsert({
      where: { id: candidate.id },
      update: data,
      create: data
    });
  }
}
```

### Scraper Strategy Pattern

```typescript
// infrastructure/external/scrapers/ScraperFactory.ts
export class ScraperFactory {
  private scrapers: Map<string, JobScraper>;

  constructor() {
    this.scrapers = new Map([
      ['jobrapido', new JobrapidoScraper()],
      ['jooble', new JoobleScraper()],
      ['indeed', new IndeedScraper()]
    ]);
  }

  getScraper(portal: string): JobScraper {
    const scraper = this.scrapers.get(portal.toLowerCase());
    if (!scraper) {
      throw new Error(`Unknown portal: ${portal}`);
    }
    return scraper;
  }

  async searchAll(query: JobSearchQuery): Promise<Job[]> {
    const results: Job[] = [];
    
    for (const [portal, scraper] of this.scrapers) {
      try {
        const jobs = await scraper.search(query);
        results.push(...jobs);
        // Rate limiting between portals
        await this.delay(2000);
      } catch (error) {
        console.error(`Failed to scrape ${portal}:`, error);
      }
    }

    return this.deduplicateJobs(results);
  }
}
```

---

## API Routes (Presentation Layer)

```typescript
// presentation/routes/application.routes.ts
const router = Router();

router.post('/',
  authenticate,
  validate(CreateApplicationSchema),
  async (req, res) => {
    const dto = req.body as CreateApplicationDTO;
    dto.staffId = req.user.id;
    
    const result = await createApplicationUseCase.execute(dto);
    res.status(201).json(result);
  }
);

router.post('/bulk',
  authenticate,
  authorize('senior_staff', 'head'),
  validate(BulkCreateApplicationSchema),
  async (req, res) => {
    const dto = req.body as BulkCreateApplicationDTO;
    const result = await bulkCreateApplicationUseCase.execute(dto);
    res.status(201).json(result);
  }
);

router.get('/autofill/:id',
  authenticate,
  async (req, res) => {
    const result = await getAutoFillDataUseCase.execute(req.params.id);
    res.json(result);
  }
);

router.put('/:id/approve',
  authenticate,
  authorize('senior_staff', 'head'),
  async (req, res) => {
    const result = await approveApplicationUseCase.execute(
      req.params.id,
      req.user.id
    );
    res.json(result);
  }
);
```

---

## Key Design Decisions

### 1. Why This Architecture?

| Principle | Implementation |
|-----------|----------------|
| **Single Responsibility** | Each use case does one thing |
| **Dependency Inversion** | Domain doesn't depend on infrastructure |
| **Ubiquitous Language** | Entities match real-world concepts |
| **Bounded Contexts** | Clear separation between Candidate, Job, Application |

### 2. Why No Redux?

For this application's complexity:
- React Context + useReducer is sufficient
- Server state can use React Query (TanStack Query)
- Simpler for 8GB RAM constraint

### 3. Why In-Memory Queue?

For 8GB RAM constraint:
- Redis requires extra RAM
- In-memory queue handles the load (12 apps/min)
- Simple and effective for this scale

### 4. Why Prisma?

- Type-safe database access
- Easy migrations
- Works well with PostgreSQL
- Good developer experience

---

## Acceptance Criteria

### Architecture
- [ ] Clear layer separation (domain/application/infrastructure)
- [ ] No circular dependencies
- [ ] Domain has no infrastructure imports
- [ ] Use cases are testable in isolation

### Bounded Contexts
- [ ] Candidate context is isolated
- [ ] Job context is isolated
- [ ] Application context is isolated
- [ ] Staff context is isolated

### Code Quality
- [ ] No generic names (utils, helpers, common)
- [ ] Domain objects use value objects
- [ ] Early returns in functions
- [ ] Max 3 nesting levels

---

## File Structure Summary

```
backend/src/
├── domain/           # Business logic (pure, testable)
├── application/      # Use cases, DTOs
├── infrastructure/  # DB, APIs, Scrapers
├── presentation/    # Routes, Controllers
└── shared/         # Errors, Utils
```

This architecture follows Clean Architecture principles with clear separation of concerns, making the codebase maintainable, testable, and scalable.
