import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.domain.entities.job import Job
from src.domain.entities.candidate import Candidate
from src.domain.services.matching_service import CandidateMatchingService
from datetime import datetime, timezone


def load_test_data():
    base_path = Path(__file__).parent / "test_data"
    
    with open(base_path / "resume.json") as f:
        resume_data = json.load(f)["candidate"]
    
    with open(base_path / "sample_jobs.json") as f:
        jobs_data = json.load(f)["jobs"]
    
    return resume_data, jobs_data


def create_candidate(data: dict) -> Candidate:
    return Candidate(
        id=data["id"],
        name=data["name"],
        email=data["email"],
        phone=data.get("phone"),
        location=data.get("location"),
        skills=data["skills"],
        experience_years=data["experience_years"],
        title=data["title"],
        summary=data.get("summary"),
        resume_url=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def create_job(data: dict) -> Job:
    posted_date = None
    if data.get("posted_date"):
        posted_date = datetime.fromisoformat(data["posted_date"].replace("Z", "+00:00"))
    
    return Job(
        id=data.get("job_board_id", ""),
        job_board_id=data["job_board_id"],
        title=data["title"],
        company=data["company"],
        location=data.get("location"),
        description=data.get("description"),
        short_description=data.get("short_description"),
        work_type=data.get("work_type", "unknown"),
        job_type=data.get("job_type", "unknown"),
        salary_min=data.get("salary_min"),
        salary_max=data.get("salary_max"),
        salary_currency=data.get("salary_currency"),
        skills=data.get("skills", []),
        source_url=data["source_url"],
        source=data["source"],
        posted_date=posted_date,
        scraped_at=datetime.now(timezone.utc),
        application_url=data.get("application_url"),
    )


def main():
    print("=" * 70)
    print("RESUME-JOB MATCHING TEST")
    print("=" * 70)
    
    resume_data, jobs_data = load_test_data()
    
    candidate = create_candidate(resume_data)
    
    print(f"\nCandidate: {candidate.name}")
    print(f"Title: {candidate.title}")
    print(f"Experience: {candidate.experience_years} years")
    print(f"Skills: {', '.join(candidate.skills)}")
    
    matcher = CandidateMatchingService(min_match_threshold=0.3)
    
    jobs = [create_job(j) for j in jobs_data]
    results = []
    
    for job in jobs:
        match_result = matcher.match_candidate_with_job(candidate, job)
        results.append({
            "job": job,
            "result": match_result
        })
    
    results.sort(key=lambda x: x["result"].score, reverse=True)
    
    qualified = [r for r in results if r["result"].is_qualified]
    not_qualified = [r for r in results if not r["result"].is_qualified]
    
    print(f"\n{'=' * 70}")
    print("RESULTS")
    print("=" * 70)
    print(f"Total Jobs: {len(jobs)}")
    print(f"Qualified: {len(qualified)}")
    print(f"Not Qualified: {len(not_qualified)}")
    print(f"Match Rate: {len(qualified)/len(jobs)*100:.1f}%")
    
    print(f"\n{'=' * 70}")
    print("TOP MATCHES (Qualified)")
    print("=" * 70)
    
    for i, r in enumerate(qualified[:10], 1):
        job = r["job"]
        result = r["result"]
        print(f"\n{i}. {job.title} at {job.company}")
        print(f"   Source: {job.source} | Location: {job.location}")
        print(f"   Work Type: {job.work_type} | Salary: ${job.salary_min or 'N/A'}-${job.salary_max or 'N/A'}")
        print(f"   Score: {result.score}")
        print(f"   Apply URL: {job.application_url or 'N/A'}")
        print(f"   Matched Skills: {', '.join(result.matched_skills[:5])}")
        print(f"   Missing Skills: {', '.join(result.missing_skills[:3])}")
    
    if not_qualified:
        print(f"\n{'=' * 70}")
        print("NOT QUALIFIED (Sample)")
        print("=" * 70)
        
        for r in not_qualified[:3]:
            job = r["job"]
            result = r["result"]
            print(f"\n- {job.title} at {job.company}")
            print(f"  Score: {result.score}")
            print(f"  Apply URL: {job.application_url or 'N/A'}")
            print(f"  Missing: {', '.join(result.missing_skills[:3])}")
    
    output_path = Path(__file__).parent / "test_data" / "matching_results.json"
    output_data = {
        "candidate": {
            "name": candidate.name,
            "title": candidate.title,
            "skills": candidate.skills
        },
        "total_jobs": len(jobs),
        "qualified_count": len(qualified),
        "not_qualified_count": len(not_qualified),
        "matches": [
            {
                "job_title": r["job"].title,
                "company": r["job"].company,
                "source": r["job"].source,
                "location": r["job"].location,
                "work_type": r["job"].work_type,
                "salary_min": r["job"].salary_min,
                "salary_max": r["job"].salary_max,
                "source_url": r["job"].source_url,
                "application_url": r["job"].application_url,
                "score": r["result"].score,
                "matched_skills": r["result"].matched_skills,
                "is_qualified": r["result"].is_qualified
            }
            for r in results
        ]
    }
    
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
