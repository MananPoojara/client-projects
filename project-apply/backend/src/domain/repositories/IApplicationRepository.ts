import { Application, CreateApplicationDTO, UpdateApplicationDTO, ApplicationFilters } from '../entities/Application';
import { PaginatedResult } from './ICandidateRepository';

export interface IApplicationRepository {
  findById(id: string): Promise<Application | null>;
  create(data: CreateApplicationDTO): Promise<Application>;
  update(id: string, data: UpdateApplicationDTO): Promise<Application>;
  delete(id: string): Promise<void>;
  findAll(filters: ApplicationFilters, page: number, limit: number): Promise<PaginatedResult<Application>>;
  findByCandidate(candidateId: string): Promise<Application[]>;
  findByJob(jobId: string): Promise<Application[]>;
  findByStaff(staffId: string): Promise<Application[]>;
  findPendingReview(): Promise<Application[]>;
  bulkCreate(applications: CreateApplicationDTO[]): Promise<Application[]>;
  approve(id: string, reviewerId: string): Promise<Application>;
  reject(id: string, reviewerId: string, reason: string): Promise<Application>;
  markSubmitted(id: string): Promise<Application>;
}
