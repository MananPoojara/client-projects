export enum CandidateStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  HIRED = 'hired',
  WITHDRAWN = 'withdrawn',
}

export interface Candidate {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  location?: string;
  linkedinUrl?: string;
  resumePath?: string;
  skills: string[];
  experienceYears?: number;
  currentCompany?: string;
  currentTitle?: string;
  status: CandidateStatus;
  consentGdpr: boolean;
  createdBy?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateCandidateDTO {
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  location?: string;
  linkedinUrl?: string;
  skills?: string[];
  experienceYears?: number;
  currentCompany?: string;
  currentTitle?: string;
  consentGdpr?: boolean;
}

export interface UpdateCandidateDTO {
  firstName?: string;
  lastName?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedinUrl?: string;
  skills?: string[];
  experienceYears?: number;
  currentCompany?: string;
  currentTitle?: string;
  status?: CandidateStatus;
  consentGdpr?: boolean;
}
