# Job Discovery System - Backend

A full-stack job discovery and application management system with web scraping capabilities.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Job Discovery System                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────────────────┐ │
│   │   Frontend  │     │   Backend   │     │       Scraper          │ │
│   │  (React)    │◄───►│  (Node.js)  │     │      (Python)          │ │
│   └─────────────┘     └──────┬──────┘     └───────────┬─────────────┘ │
│                              │                         │               │
│                              ▼                         ▼               │
│                       ┌─────────────┐          ┌─────────────┐          │
│                       │  PostgreSQL │◄────────►│    Redis   │          │
│                       │  Database   │          │   Queue    │          │
│                       └─────────────┘          └─────────────┘          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
backend/
├── src/
│   ├── main.ts                      # Application entry point
│   ├── app.ts                       # Express app configuration
│   │
│   ├── domain/                      # DOMAIN LAYER (innermost)
│   │   │                            # Core business entities & rules
│   │   ├── entities/
│   │   │   ├── Staff.ts            # Staff user entity
│   │   │   ├── Candidate.ts        # Job candidate entity
│   │   │   ├── Job.ts              # Job listing entity
│   │   │   └── Application.ts      # Job application entity
│   │   │
│   │   ├── value-objects/           # Immutable value objects
│   │   │   ├── Email.ts            # Email value object
│   │   │   ├── PhoneNumber.ts      # Phone number value object
│   │   │   ├── SkillSet.ts        # Skills collection
│   │   │   └── MatchScore.ts      # Matching score value object
│   │   │
│   │   └── repositories/           # Repository interfaces (contracts)
│   │       ├── IStaffRepository.ts
│   │       ├── ICandidateRepository.ts
│   │       ├── IJobRepository.ts
│   │       └── IApplicationRepository.ts
│   │
│   ├── infrastructure/             # INFRASTRUCTURE LAYER (outermost)
│   │   │                          # External integrations
│   │   ├── database/
│   │   │   ├── DatabaseConfig.ts  # Prisma database connection
│   │   │   └── repositories/     # Repository implementations
│   │   │       ├── PrismaStaffRepository.ts
│   │   │       ├── PrismaCandidateRepository.ts
│   │   │       ├── PrismaJobRepository.ts
│   │   │       └── PrismaApplicationRepository.ts
│   │   │
│   │   ├── queue/
│   │   │   └── RedisQueue.ts     # Redis queue for async jobs
│   │   │
│   │   └── external/
│   │       └── scraper/           # Python scraper service
│   │           ├── src/
│   │           │   ├── worker.py            # Scraper worker
│   │           │   └── infrastructure/
│   │           │       └── scrapers/       # Individual scrapers
│   │           │           ├── base_scraper.py
│   │           │           ├── jooble_scraper.py
│   │           │           ├── remotive_scraper.py
│   │           │           └── indeed_selenium_scraper.py
│   │           ├── requirements.txt
│   │           └── Dockerfile
│   │
│   ├── presentation/              # PRESENTATION LAYER
│   │   │                          # HTTP handlers & routes
│   │   ├── routes/               # API endpoints
│   │   │   ├── auth.routes.ts    # /api/auth/*
│   │   │   ├── candidate.routes.ts # /api/candidates/*
│   │   │   ├── job.routes.ts     # /api/jobs/*
│   │   │   ├── application.routes.ts # /api/applications/*
│   │   │   ├── dashboard.routes.ts # /api/dashboard/*
│   │   │   └── report.routes.ts  # /api/reports/*
│   │   │
│   │   └── middleware/            # Express middleware
│   │       ├── auth.middleware.ts    # JWT authentication
│   │       ├── rbac.middleware.ts    # Role-based access control
│   │       ├── validation.middleware.ts # Request validation
│   │       ├── errorHandler.middleware.ts # Error handling
│   │       └── rateLimiter.middleware.ts # Rate limiting
│   │
│   └── shared/                   # SHARED KERNEL
│       ├── errors/               # Custom error classes
│       │   └── index.ts
│       ├── utils/
│       │   ├── logger.ts        # Winston logger
│       │   └── date.utils.ts    # Date utilities
│       └── constants/
│           └── index.ts          # App constants
│
├── prisma/
│   └── schema.prisma            # Database schema
│
├── docker-compose.yml            # Docker orchestration
├── Dockerfile                    # Backend Docker image
├── tsconfig.json                 # TypeScript config
├── package.json                  # Node.js dependencies
└── README.md                     # This file
```

## Technology Stack

### Backend (Node.js)
| Technology | Purpose |
|------------|---------|
| Node.js 20 LTS | Runtime |
| Express.js | Web framework |
| PostgreSQL 15 | Database |
| Prisma | ORM |
| Redis + ioredis | Message queue |
| JWT + bcrypt | Authentication |
| Zod | Request validation |
| Winston | Logging |

### Scraper (Python)
| Technology | Purpose |
|------------|---------|
| Python 3.11+ | Runtime |
| requests | HTTP client |
| aiohttp | Async HTTP |
| Selenium | Browser automation |
| asyncpg | PostgreSQL async driver |
| redis-py | Redis client |

## Prerequisites

1. **Node.js** 20+ installed
2. **Python** 3.11+ installed (for scraper)
3. **Docker & Docker Compose** (recommended)
4. **PostgreSQL** 15+ (if not using Docker)
5. **Redis** 7+ (if not using Docker)

## Quick Start

### Option 1: Using Docker (Recommended)

```bash
# Navigate to backend
cd backend

# Start all services (app, db, redis, scraper)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app
docker-compose logs -f scraper
```

### Option 2: Local Development

```bash
# 1. Install Node.js dependencies
npm install

# 2. Install Python dependencies (for scraper)
cd src/infrastructure/external/scraper
pip install -r requirements.txt
cd ../../../../..

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your settings

# 4. Set up database
npx prisma migrate dev

# 5. Start the server
npm run dev

# 6. Start scraper worker (separate terminal)
cd src/infrastructure/external/scraper
python -m src.worker
```

## Environment Variables

Create a `.env` file in the backend root:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/job_discovery

# Redis
REDIS_URL=redis://localhost:6379

# JWT (generate secure secrets - minimum 32 characters!)
JWT_SECRET=your-super-secret-jwt-key-min-32-chars
JWT_REFRESH_SECRET=your-super-secret-refresh-key-min-32

# Server
PORT=3000
NODE_ENV=development

# Upload
MAX_FILE_SIZE=5242880
UPLOAD_DIR=uploads/resumes

# Logging
LOG_LEVEL=info
LOG_FORMAT=json
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login with email/password |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Get current user |

### Jobs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/jobs` | List jobs (with filters) |
| POST | `/api/jobs` | Create job manually |
| POST | `/api/jobs/sync` | Trigger scraper |
| GET | `/api/jobs/sync/status/:id` | Check scrape status |
| GET | `/api/jobs/:id` | Get job details |
| PUT | `/api/jobs/:id` | Update job |
| DELETE | `/api/jobs/:id` | Delete job |

### Candidates
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/candidates` | List candidates |
| POST | `/api/candidates` | Create candidate |
| GET | `/api/candidates/:id` | Get candidate |
| PUT | `/api/candidates/:id` | Update candidate |
| DELETE | `/api/candidates/:id` | Delete candidate |

### Applications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/applications` | List applications |
| POST | `/api/applications` | Create application |
| POST | `/api/applications/:id/approve` | Approve (senior+) |
| POST | `/api/applications/:id/reject` | Reject with reason |
| DELETE | `/api/applications/:id` | Delete application |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats` | Staff statistics |
| GET | `/api/dashboard/activity` | Recent activity |

### Reports (Head only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reports/staff-progress` | All staff progress |
| GET | `/api/reports/team-stats` | Team statistics |

## Using the Scraper

### Trigger a Scrape Job

```bash
curl -X POST http://localhost:3000/api/jobs/sync \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  -d '{
    "board": "jooble",
    "keywords": ["python", "javascript", "react"],
    "location": "remote"
  }'
```

### Check Scrape Status

```bash
curl http://localhost:3000/api/jobs/sync/status/<JOB_ID> \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```

### Response Example

```json
{
  "success": true,
  "data": {
    "jobId": "abc-123",
    "status": "completed",
    "result": {
      "jobsFound": 45,
      "jobsSaved": 42,
      "completedAt": "2024-01-15T10:30:00Z"
    }
  }
}
```

### Available Boards
| Board | Type | Description |
|-------|------|-------------|
| `jooble` | API | Jooble job board (free) |
| `remotive` | API | Remotive remote jobs (free) |
| `indeed` | Selenium | Indeed jobs (requires browser) |
| `linkedin` | Selenium | LinkedIn jobs (requires browser) |
| `all` | Mixed | All available boards |

### Request Options
```json
{
  "board": "jooble",
  "keywords": ["python", "javascript"],
  "location": "remote",
  "options": {
    "country": "us",
    "datePosted": 7
  }
}
```

### Job Filter Query Parameters
```
GET /api/jobs?workType=remote&location=USA&source=jooble&datePosted=7&skills=python,javascript&search=developer
```

| Parameter | Description |
|-----------|-------------|
| `workType` | remote, hybrid, onsite |
| `location` | Location name |
| `source` | jooble, remotive, indeed, linkedin, manual |
| `datePosted` | Jobs from last N days (1, 3, 7, 30) |
| `minMatchScore` | Minimum match percentage |
| `search` | Search in title, company, description |
| `skills` | Comma-separated skills |
| `page` | Page number (default: 1) |
| `limit` | Items per page (default: 20, max: 100) |

## Database Schema

### Staff
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| email | String | Unique email |
| passwordHash | String | Bcrypt hashed password |
| firstName | String | First name |
| lastName | String | Last name |
| role | Enum | head, senior_staff, staff |
| department | String? | Optional department |
| isActive | Boolean | Account status |
| lastLogin | DateTime? | Last login timestamp |

### Candidate
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| firstName | String | First name |
| lastName | String | Last name |
| email | String | Unique email |
| phone | String? | Phone number |
| location | String? | Location |
| linkedinUrl | String? | LinkedIn profile |
| resumePath | String? | Path to resume file |
| skills | String[] | Array of skills |
| experienceYears | Int? | Years of experience |
| currentCompany | String? | Current employer |
| currentTitle | String? | Current job title |
| status | Enum | active, inactive, hired, withdrawn |
| consentGdpr | Boolean | GDPR consent |

### Job
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| title | String | Job title |
| company | String | Company name |
| location | String? | Job location |
| description | String? | Full description |
| requirements | String[] | Job requirements |
| skillsRequired | String[] | Required skills |
| salaryMin | Int? | Minimum salary |
| salaryMax | Int? | Maximum salary |
| sourceUrl | String? | Original job URL |
| sourcePortal | String | jooble, remotive, indeed, linkedin, manual |
| jobType | Enum | full_time, part_time, contract, internship, temporary |
| remoteType | Enum | remote, hybrid, onsite |
| status | String | active, inactive, closed |

### Application
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| candidateId | UUID | FK to Candidate |
| jobId | UUID | FK to Job |
| staffId | UUID | FK to Staff (creator) |
| coverLetter | String? | Cover letter text |
| status | Enum | draft, pending_review, approved, rejected, submitted |
| staffNotes | String? | Staff notes |
| reviewerId | UUID? | FK to Staff (reviewer) |
| reviewedAt | DateTime? | Review timestamp |
| submittedAt | DateTime? | Submission timestamp |

## Role-Based Access Control

| Feature | Head | Senior Staff | Staff |
|---------|------|---------------|-------|
| View Candidates | ✓ | ✓ | ✓ |
| Create Candidates | ✓ | ✓ | ✓ |
| Delete Candidates | ✓ | ✗ | ✗ |
| View Jobs | ✓ | ✓ | ✓ |
| Create Jobs | ✓ | ✓ | ✗ |
| Delete Jobs | ✓ | ✗ | ✗ |
| Create Applications | ✓ | ✓ | ✓ |
| Approve Applications | ✓ | ✓ | ✗ |
| Reject Applications | ✓ | ✓ | ✗ |
| View Reports | ✓ | ✓ | ✗ |
| Manage Staff | ✓ | ✗ | ✗ |

## Making Changes

### Adding a New API Endpoint

1. **Create the route file** in `src/presentation/routes/`
   ```typescript
   // src/presentation/routes/custom.routes.ts
   import { Router } from 'express';
   
   const router = Router();
   
   router.get('/', (req, res) => {
     res.json({ message: 'Hello World' });
   });
   
   export default router;
   ```

2. **Register the route** in `src/app.ts`
   ```typescript
   import customRoutes from './presentation/routes/custom.routes';
   
   app.use('/api/custom', customRoutes);
   ```

3. **Add validation** using Zod (recommended)
   ```typescript
   import { z } from 'zod';
   
   const customSchema = z.object({
     param1: z.string(),
     param2: z.number().optional()
   });
   
   // Use in route
   router.post('/', validateBody(customSchema), handler);
   ```

### Adding a New Scraper

1. **Create scraper class** in `src/infrastructure/external/scraper/src/infrastructure/scrapers/`
   ```python
   from src.infrastructure.scrapers.base_scraper import BaseScraper
   
   class MyPortalScraper(BaseScraper):
       name = "myportal"
       board_id = "myportal"
       
       def __init__(self):
           super().__init__(None)
       
       def scrape(self, keywords, location="", **kwargs):
           results = []
           # Implement scraping logic
           # Use self._create_job_record() to standardize output
           return results
   ```

2. **Register in worker** (`src/worker.py`)
   ```python
   async def scrape_board(self, board, keywords, location):
       if board == 'myportal':
           return await self.scrape_myportal(keywords, location)
   ```

3. **Add to API options** in `src/presentation/routes/job.routes.ts`
   ```typescript
   const syncJobSchema = z.object({
     board: z.enum(['jooble', 'remotive', 'indeed', 'myportal', 'all']),
     // ...
   });
   ```

### Adding a New Entity

1. **Define entity** in `src/domain/entities/`
2. **Create repository interface** in `src/domain/repositories/`
3. **Implement repository** in `src/infrastructure/database/repositories/`
4. **Add to Prisma schema** in `prisma/schema.prisma`
5. **Run migration**: `npx prisma migrate dev`

### Adding Middleware

1. **Create middleware** in `src/presentation/middleware/`
   ```typescript
   export const myMiddleware = (req, res, next) => {
     // Do something (logging, auth check, etc.)
     next();
   };
   ```

2. **Apply to routes**
   ```typescript
   // Global (in app.ts)
   app.use(myMiddleware);
   
   // Specific route
   router.use('/path', myMiddleware);
   ```

### Customizing Validation

Validation schemas are in `src/presentation/middleware/validation.middleware.ts`:

```typescript
const newSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  age: z.number().int().min(18).max(100),
  tags: z.array(z.string()).optional(),
  metadata: z.record(z.string(), z.any()).optional()
});

// Use in route
router.post('/', validateBody(newSchema), handler);
```

## Running Tests

```bash
# TypeScript type checking
npm run typecheck

# Prisma Studio (database GUI)
npm run db:studio

# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f app
docker-compose logs -f scraper
docker-compose logs -f db
```

## Common Issues

### "Redis not connected"
- Ensure Redis is running: `docker-compose up -d redis`
- Check REDIS_URL in .env
- Try: `docker-compose restart redis`

### "Database connection failed"
- Ensure PostgreSQL is running
- Run migrations: `npx prisma migrate dev`
- Check DATABASE_URL in .env

### "Module not found" errors
- Rebuild TypeScript: `npm run build`
- Check tsconfig.json paths
- Try: `rm -rf node_modules && npm install`

### Scraper not saving jobs
- Check database connection in worker.py
- Verify source_url is unique (used for upsert)
- Check worker logs: `docker-compose logs scraper`

### Port already in use
- Change PORT in .env
- Or stop other services: `lsof -i :3000`

## Default Users (After Seeding)

| Email | Password | Role |
|-------|----------|------|
| head@company.com | password123 | Head |
| senior@company.com | password123 | Senior Staff |
| staff@company.com | password123 | Staff |

## Project Layers Explained

### Domain Layer (Innermost)
- Contains pure business logic
- No dependencies on external frameworks
- Entities, Value Objects, Repository Interfaces

### Application Layer
- Use cases and business workflows
- Coordinates domain objects
- (Not fully implemented yet - can be added)

### Infrastructure Layer (Outermost)
- Database connections
- External API clients
- Queue systems
- Implementation of repository interfaces

### Presentation Layer
- HTTP handling
- Route definitions
- Middleware
- Input/Output handling

## Directory Structure Summary

| Directory | Purpose |
|-----------|----------|
| `src/domain/` | Business entities & rules |
| `src/infrastructure/` | External integrations |
| `src/presentation/` | HTTP handling |
| `src/shared/` | Shared utilities |
| `prisma/` | Database schema |

## Contributing

1. Follow the DDD architecture pattern
2. Use TypeScript for all new code
3. Add Zod validation for API inputs
4. Write proper error handling
5. Use the logger (not console.log)
6. Test your changes locally before submitting

## License

MIT
