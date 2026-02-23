# Job Discovery System

A comprehensive job discovery, application tracking, and candidate management system with built-in job scraping capabilities.

## Overview

This system helps staffing agencies manage job applications for multiple candidates. Staff can:
- **Discover Jobs**: Scrape jobs from multiple job boards (Indeed, Jooble, Remotive, LinkedIn)
- **Manage Candidates**: Track candidate profiles, skills, and resumes
- **Track Applications**: Manage application workflow from draft to submission
- **Generate Applications**: Bulk generate job applications for candidates
- **Staff Collaboration**: Track staff progress and team performance

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Job Discovery System                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────────────────┐ │
│   │   Frontend  │     │   Backend   │     │       Scraper          │ │
│   │  (React)    │◄───►│  (Node.js)  │     │      (Python)          │ │
│   │   (Next.js) │     │  Express +  │     │  Selenium + APIs       │ │
│   │             │     │   Prisma     │     │                        │ │
│   └─────────────┘     └──────┬──────┘     └───────────┬─────────────┘ │
│                              │                         │               │
│                              ▼                         ▼               │
│                       ┌─────────────┐          ┌─────────────┐          │
│                       │  PostgreSQL │◄────────│    Redis   │          │
│                       │  Database   │          │   Queue    │          │
│                       └─────────────┘          └─────────────┘          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Tech Stack

### Backend
- **Runtime**: Node.js 20 LTS
- **Framework**: Express.js
- **Database**: PostgreSQL 15
- **ORM**: Prisma
- **Queue**: Redis
- **Auth**: JWT + bcrypt
- **Validation**: Zod

### Scraper
- **Runtime**: Python 3.11+
- **APIs**: requests, aiohttp
- **Browser**: Selenium, Playwright
- **DB**: asyncpg

### Frontend (Coming Soon)
- React + Next.js
- TypeScript
- Tailwind CSS

## Features

### Job Discovery
- [x] Scrape from Jooble (free API)
- [x] Scrape from Remotive (free API)
- [ ] Scrape from Indeed (Selenium)
- [ ] Scrape from LinkedIn (Selenium)
- [x] Redis queue for background jobs
- [x] Job status tracking

### Candidate Management
- [x] CRUD operations
- [x] Resume upload & parsing
- [x] Skills tracking
- [x] Bulk import (CSV)
- [x] GDPR consent

### Application Workflow
- [x] Create applications
- [x] Bulk generate (60 per candidate)
- [x] Approval workflow (draft → review → approve/reject → submit)
- [x] Auto-fill data generation
- [x] Staff notes

### Dashboard & Reports
- [x] Staff statistics
- [x] Activity tracking
- [x] Team progress
- [x] Leaderboard

### Security
- [x] JWT authentication
- [x] Role-based access (Head, Senior Staff, Staff)
- [x] Rate limiting
- [x] Input validation

## Project Structure

```
project-apply/
├── backend/                    # Node.js API server
│   ├── src/
│   │   ├── domain/           # Business entities & rules
│   │   ├── infrastructure/   # Database & external services
│   │   ├── presentation/    # API routes & middleware
│   │   └── shared/          # Utilities
│   ├── prisma/              # Database schema
│   └── docker-compose.yml   # All services
│
├── tasks/                    # Task specifications
│   └── architecture.md      # System architecture
│
└── uploads/                  # File uploads
    └── resumes/             # Candidate resumes
```

## Getting Started

### Prerequisites
- Node.js 20+
- Python 3.11+
- Docker & Docker Compose (recommended)

### Quick Start

```bash
# Clone and navigate to project
cd project-apply/backend

# Start all services
docker-compose up -d

# Or for local development
npm install
cp .env.example .env
npx prisma migrate dev
npm run dev
```

See [backend/README.md](backend/README.md) for detailed setup instructions.

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token
- `POST /api/auth/logout` - Logout

### Jobs
- `GET /api/jobs` - List jobs (with filters)
- `POST /api/jobs` - Create job manually
- `POST /api/jobs/sync` - Trigger scraper
- `GET /api/jobs/sync/status/:id` - Check scrape status

### Candidates
- `GET /api/candidates` - List candidates
- `POST /api/candidates` - Create candidate
- `PUT /api/candidates/:id` - Update candidate

### Applications
- `GET /api/applications` - List applications
- `POST /api/applications` - Create application
- `POST /api/applications/:id/approve` - Approve
- `POST /api/applications/:id/reject` - Reject

### Dashboard
- `GET /api/dashboard/stats` - Staff statistics
- `GET /api/dashboard/activity` - Recent activity

### Reports (Head only)
- `GET /api/reports/staff-progress` - Staff progress
- `GET /api/reports/team-stats` - Team stats

## Job Filters

Jobs can be filtered using query parameters:
```
GET /api/jobs?workType=remote&location=USA&source=jooble&datePosted=7&skills=python,javascript
```

| Parameter | Description |
|-----------|-------------|
| `workType` | remote, hybrid, onsite |
| `location` | Location name |
| `source` | jooble, remotive, indeed, linkedin |
| `datePosted` | Days since posted (1, 3, 7, 30) |
| `skills` | Comma-separated skills |
| `search` | Search in title/company |
| `page` | Page number |
| `limit` | Items per page |

## Roles & Permissions

| Role | Description |
|------|-------------|
| **Head** | Full access to all features |
| **Senior Staff** | Candidates, Jobs, Applications, approve/reject |
| **Staff** | View/create applications for assigned candidates |

## Scraping Jobs

```bash
# Trigger a scrape
curl -X POST http://localhost:3000/api/jobs/sync \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "board": "jooble",
    "keywords": ["python", "javascript"],
    "location": "remote"
  }'

# Check status
curl http://localhost:3000/api/jobs/sync/status/<JOB_ID>
```

## Default Users (After Seeding)

| Email | Password | Role |
|-------|----------|------|
| head@company.com | password123 | Head |
| senior@company.com | password123 | Senior Staff |
| staff@company.com | password123 | Staff |

## Environment Variables

Create `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/job_discovery
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key-min-32-chars
JWT_REFRESH_SECRET=your-refresh-secret-key
PORT=3000
NODE_ENV=development
```

## Development

### Running Tests
```bash
cd backend
npm run typecheck    # TypeScript checking
npm run db:studio   # Database GUI
```

### Adding New Features
1. Define entity in `src/domain/entities/`
2. Create repository interface in `src/domain/repositories/`
3. Implement in `src/infrastructure/database/repositories/`
4. Add route in `src/presentation/routes/`
5. Add validation in middleware

See [backend/README.md](backend/README.md) for detailed development guide.

## Roadmap

- [ ] Frontend (React + Next.js)
- [ ] Indeed scraper (Selenium)
- [ ] LinkedIn scraper (Selenium)
- [ ] Resume parsing service
- [ ] Skill matching algorithm
- [ ] Cover letter generation
- [ ] Email notifications
- [ ] Export to CSV/Excel

## License

MIT
