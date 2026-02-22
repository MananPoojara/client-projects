PRD: Scalable Job Board Scraping & Orchestration System
1. Overview

Build a scalable scraping orchestration system capable of collecting ~500,000 structured candidate/job records per day from 25 compliant job boards.

The system will use:

Node.js (API + Bull queue orchestrator)

React (Monitoring dashboard)

PostgreSQL (Structured storage)

Redis (Queue + caching)

Bull (Job scheduling & orchestration)

Python (Scrapy for static boards + Playwright for JS-heavy boards)

Dockerized deployment on VM (Kubernetes-ready architecture)

The system runs twice daily batch crawls with board-specific throttling and zero manual intervention.

2. Goals

Collect up to 5 lakh structured records per day

Support 25 independent job board scrapers

Fully automated retry & failure handling

Hybrid deduplication strategy

Horizontally scalable architecture

Dockerized microservice-ready design

Zero-cost infrastructure friendly

3. Quality Gates

These commands must pass for every user story:

Node Services:

npm run lint

npm run test

Python Scrapers:

pytest

flake8

For UI stories:

Manual browser verification required

4. User Stories
US-001: Setup Queue Orchestrator Service

Description: As a system, I want a Bull-based orchestrator so that scraping jobs can be scheduled and distributed reliably.

Acceptance Criteria:

 Redis connection established

 Bull queue created for each board

 Queue supports repeatable jobs

 Failed jobs move to dead-letter queue

 Exponential backoff retry configured

US-002: Implement Board Scheduler

Description: As a system, I want twice-daily repeatable jobs so that scraping runs automatically.

Acceptance Criteria:

 Bull repeatable job configured (2x daily)

 Each board has configurable schedule

 Jobs logged with timestamp

 Manual trigger endpoint available

US-003: Create Scrapy Worker Base Template

Description: As a developer, I want a reusable Scrapy base class so that static job boards can be implemented consistently.

Acceptance Criteria:

 Base spider class created

 Board config file supported

 Structured output JSON schema enforced

 Throttle config per board supported

US-004: Create Playwright Worker Base Template

Description: As a developer, I want a reusable Playwright scraping template for JS-heavy boards.

Acceptance Criteria:

 Headless Playwright setup

 Timeout handling

 Rate limiting applied

 Structured data extraction standardized

US-005: Structured Data Normalization Service

Description: As a system, I want scraped data normalized before DB insertion.

Acceptance Criteria:

 Common schema defined

 Required fields validated

 Invalid entries rejected

 Timestamp and source fields auto-added

US-006: Hybrid Deduplication Engine

Description: As a system, I want duplicate records prevented before insertion.

Acceptance Criteria:

 Unique by job_board_id if available

 Fallback hash of (name + title + company)

 Duplicate records logged

 DB unique index created

US-007: Dead Letter Queue Handling

Description: As a system, I want failed jobs isolated for monitoring.

Acceptance Criteria:

 Failed jobs retried with exponential backoff

 After max attempts, moved to DLQ

 DLQ records stored in DB

 Failure reason logged

US-008: Monitoring Dashboard

Description: As an admin, I want visibility into scraping health.

Acceptance Criteria:

 Show jobs processed per board

 Show success/failure count

 Show queue depth

 Show last run timestamp

 DLQ metrics displayed

US-009: Board-Specific Throttling Configuration

Description: As a system, I want per-board rate control to prevent blocking.

Acceptance Criteria:

 Each board has config file

 Delay per request configurable

 Concurrency configurable

 Throttle values applied in runtime

US-010: Dockerized Service Setup

Description: As a developer, I want services containerized for deployment.

Acceptance Criteria:

 Dockerfile for Node service

 Dockerfile for Python worker

 Docker Compose for full stack

 Environment variables configurable

5. Functional Requirements

FR-1: System must schedule scraping twice daily.
FR-2: Each board must run independently.
FR-3: Failures must retry with exponential backoff.
FR-4: After max retries, jobs move to DLQ.
FR-5: Only structured parsed data must be stored.
FR-6: Deduplication must occur before DB insert.
FR-7: PostgreSQL must enforce unique constraint.
FR-8: Throttling must be board-specific.
FR-9: System must support horizontal scaling.
FR-10: All services must be Dockerized.

6. Non-Goals

Scraping boards that disallow crawling

Storing raw HTML

Manual failure processing

Paid proxy integration

Real-time scraping

AI-based parsing (future phase)

7. Technical Considerations

Use Redis as central queue backbone

Use separate worker containers per board

DB indexing critical for 5 lakh/day scale

Partition tables monthly for performance

Use connection pooling

Keep Playwright workers isolated (memory heavy)

Use structured logging (JSON logs)

8. Success Metrics

5 lakh records/day achieved

<5% job failure rate

Zero manual intervention required

System stable under 25 parallel boards

Average job completion time within SLA

9. Open Questions

Should we introduce Kafka in future for high-scale streaming?

Should we implement auto-scaling workers?

Should we add distributed locking for multi-instance scaling?

