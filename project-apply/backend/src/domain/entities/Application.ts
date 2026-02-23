export enum ApplicationStatus {
  DRAFT = 'draft',
  PENDING_REVIEW = 'pending_review',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  SUBMITTED = 'submitted',
}

export interface Application {
  id: string;
  candidateId: string;
  jobId: string;
  staffId: string;
  coverLetter?: string;
  status: ApplicationStatus;
  staffNotes?: string;
  reviewerId?: string;
  reviewedAt?: Date;
  submittedAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateApplicationDTO {
  candidateId: string;
  jobId: string;
  coverLetter?: string;
  staffNotes?: string;
}

export interface UpdateApplicationDTO {
  coverLetter?: string;
  staffNotes?: string;
  status?: ApplicationStatus;
}

export interface ApplicationFilters {
  status?: ApplicationStatus;
  staffId?: string;
  candidateId?: string;
  page?: number;
  limit?: number;
}
