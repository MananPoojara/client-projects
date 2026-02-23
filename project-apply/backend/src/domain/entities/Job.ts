export enum JobType {
  FULL_TIME = 'full_time',
  PART_TIME = 'part_time',
  CONTRACT = 'contract',
  INTERNSHIP = 'internship',
  TEMPORARY = 'temporary',
}

export enum RemoteType {
  REMOTE = 'remote',
  HYBRID = 'hybrid',
  ONSITE = 'onsite',
}

export interface Job {
  id: string;
  title: string;
  company: string;
  location?: string;
  description?: string;
  requirements: string[];
  skillsRequired: string[];
  salaryMin?: number;
  salaryMax?: number;
  sourceUrl?: string;
  sourcePortal?: string;
  jobType?: JobType;
  remoteType?: RemoteType;
  status: string;
  postedDate?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateJobDTO {
  title: string;
  company: string;
  location?: string;
  description?: string;
  requirements?: string[];
  skillsRequired?: string[];
  salaryMin?: number;
  salaryMax?: number;
  sourceUrl?: string;
  sourcePortal?: string;
  jobType?: JobType;
  remoteType?: RemoteType;
  postedDate?: Date;
}

export interface UpdateJobDTO {
  title?: string;
  company?: string;
  location?: string;
  description?: string;
  requirements?: string[];
  skillsRequired?: string[];
  salaryMin?: number;
  salaryMax?: number;
  sourceUrl?: string;
  sourcePortal?: string;
  jobType?: JobType;
  remoteType?: RemoteType;
  status?: string;
  postedDate?: Date;
}

export interface JobFilters {
  status?: string;
  workType?: RemoteType;
  location?: string;
  source?: string;
  datePosted?: number;
  minMatchScore?: number;
  search?: string;
  skills?: string[];
  page?: number;
  limit?: number;
}
