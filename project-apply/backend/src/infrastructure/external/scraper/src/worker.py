import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime

import redis
import asyncpg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScraperWorker:
    def __init__(self):
        self.redis_client = None
        self.db_pool = None
        self.running = True
        
    async def connect(self):
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/job_discovery')
        
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.db_pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10)
        
        logger.info("Connected to Redis and PostgreSQL")
    
    async def disconnect(self):
        if self.db_pool:
            await self.db_pool.close()
        if self.redis_client:
            self.redis_client.close()
        logger.info("Disconnected from Redis and PostgreSQL")
    
    async def process_job(self, job_data: dict):
        job_id = job_data['id']
        board = job_data['board']
        keywords = job_data['keywords']
        location = job_data.get('location', '')
        
        logger.info(f"Processing job {job_id} for board: {board}")
        
        self.redis_client.hset(f"scrape:status:{job_id}", "status", "running")
        
        try:
            jobs = await self.scrape_board(board, keywords, location)
            
            saved_count = 0
            for job in jobs:
                await self.save_job_to_db(job)
                saved_count += 1
            
            result = {
                'jobId': job_id,
                'status': 'success' if saved_count > 0 else 'failed',
                'jobsFound': len(jobs),
                'jobsSaved': saved_count,
                'completedAt': datetime.utcnow().isoformat()
            }
            
            self.redis_client.publish('scrape:results', json.dumps(result))
            self.redis_client.hset(f"scrape:status:{job_id}", mapping={
                'status': 'completed',
                'result': json.dumps(result)
            })
            self.redis_client.expire(f"scrape:status:{job_id}", 3600)
            
            logger.info(f"Job {job_id} completed: {saved_count} jobs saved")
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            result = {
                'jobId': job_id,
                'status': 'failed',
                'jobsFound': 0,
                'jobsSaved': 0,
                'errors': [str(e)],
                'completedAt': datetime.utcnow().isoformat()
            }
            self.redis_client.publish('scrape:results', json.dumps(result))
            self.redis_client.hset(f"scrape:status:{job_id}", mapping={
                'status': 'failed',
                'result': json.dumps(result)
            })
    
    async def scrape_board(self, board: str, keywords: list, location: str) -> list:
        if board == 'jooble' or board == 'all':
            return await self.scrape_jooble(keywords, location)
        elif board == 'remotive':
            return await self.scrape_remotive(keywords)
        elif board == 'indeed':
            return await self.scrape_indeed(keywords, location)
        else:
            logger.warning(f"Unknown board: {board}")
            return []
    
    async def scrape_jooble(self, keywords: list, location: str) -> list:
        import requests
        
        results = []
        for keyword in keywords:
            try:
                response = requests.post(
                    "https://jooble.org/api/",
                    json={"keywords": keyword, "location": location, "page": 1, "results_per_page": 20},
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    for job in data.get('jobs', []):
                        results.append({
                            'title': job.get('title', ''),
                            'company': job.get('company', ''),
                            'location': job.get('location', ''),
                            'description': job.get('snippet', ''),
                            'source_url': job.get('link', ''),
                            'source_portal': 'jooble',
                            'skills': self.extract_skills(job.get('snippet', '')),
                            'remote_type': 'remote' if 'remote' in job.get('location', '').lower() else 'onsite',
                        })
            except Exception as e:
                logger.error(f"Error scraping jooble: {e}")
        
        return results
    
    async def scrape_remotive(self, keywords: list) -> list:
        import requests
        
        results = []
        for keyword in keywords:
            try:
                response = requests.get(
                    f"https://remotive.com/api/remote-jobs?category=software-dev&search={keyword}",
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    for job in data.get('jobs', []):
                        results.append({
                            'title': job.get('title', ''),
                            'company': job.get('company_name', ''),
                            'location': job.get('candidate_required_location', ''),
                            'description': job.get('description', ''),
                            'source_url': job.get('url', ''),
                            'source_portal': 'remotive',
                            'skills': self.extract_skills(job.get('description', '')),
                            'remote_type': 'remote',
                        })
            except Exception as e:
                logger.error(f"Error scraping remotive: {e}")
        
        return results
    
    async def scrape_indeed(self, keywords: list, location: str) -> list:
        logger.warning("Indeed scraping requires Selenium - skipping for now")
        return []
    
    def extract_skills(self, text: str) -> list:
        common_skills = [
            'python', 'javascript', 'java', 'typescript', 'react', 'node.js',
            'django', 'flask', 'postgresql', 'mysql', 'mongodb', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git',
            'rest api', 'graphql', 'machine learning', 'tensorflow'
        ]
        if not text:
            return []
        text_lower = text.lower()
        return list(set([s for s in common_skills if s in text_lower]))[:10]
    
    async def save_job_to_db(self, job: dict):
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO jobs (
                    title, company, location, description, source_url, 
                    source_portal, skills_required, remote_type, status, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'active', NOW(), NOW())
                ON CONFLICT (source_url) DO UPDATE SET
                    title = EXCLUDED.title,
                    company = EXCLUDED.company,
                    location = EXCLUDED.location,
                    description = EXCLUDED.description,
                    updated_at = NOW()
            """,
                job.get('title', ''),
                job.get('company', ''),
                job.get('location', ''),
                job.get('description', ''),
                job.get('source_url', ''),
                job.get('source_portal', ''),
                job.get('skills', []),
                job.get('remote_type', 'unknown')
            )
    
    async def run(self):
        await self.connect()
        
        logger.info("Worker started, listening for jobs...")
        
        while self.running:
            try:
                result = self.redis_client.brpop('scrape:jobs', timeout=5)
                if result:
                    _, job_json = result
                    job_data = json.loads(job_json)
                    await self.process_job(job_data)
            except Exception as e:
                logger.error(f"Error processing job: {e}")
                await asyncio.sleep(1)
        
        await self.disconnect()


async def main():
    worker = ScraperWorker()
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
