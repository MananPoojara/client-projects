import { Candidate, CreateCandidateDTO, UpdateCandidateDTO } from '../entities/Candidate';

export interface CandidateFilters {
  status?: string;
  search?: string;
  skills?: string[];
  minExperience?: number;
  maxExperience?: number;
}

export interface PaginatedResult<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface ICandidateRepository {
  findById(id: string): Promise<Candidate | null>;
  findByEmail(email: string): Promise<Candidate | null>;
  create(data: CreateCandidateDTO): Promise<Candidate>;
  update(id: string, data: UpdateCandidateDTO): Promise<Candidate>;
  delete(id: string): Promise<void>;
  findAll(filters: CandidateFilters, page: number, limit: number): Promise<PaginatedResult<Candidate>>;
  updateResumePath(id: string, path: string): Promise<Candidate>;
  findBySkills(skills: string[]): Promise<Candidate[]>;
}
