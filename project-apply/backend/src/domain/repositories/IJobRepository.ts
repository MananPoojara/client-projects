import { Job, CreateJobDTO, UpdateJobDTO, JobFilters } from '../entities/Job';
import { PaginatedResult } from './ICandidateRepository';

export interface IJobRepository {
  findById(id: string): Promise<Job | null>;
  create(data: CreateJobDTO): Promise<Job>;
  update(id: string, data: UpdateJobDTO): Promise<Job>;
  delete(id: string): Promise<void>;
  findAll(filters: JobFilters, page: number, limit: number): Promise<PaginatedResult<Job>>;
  findBySkills(skills: string[]): Promise<Job[]>;
  findBySource(source: string): Promise<Job[]>;
  bulkCreate(jobs: CreateJobDTO[]): Promise<Job[]>;
}
