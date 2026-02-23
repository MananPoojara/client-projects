export const HTTP_STATUS_CODES = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  INTERNAL_SERVER_ERROR: 500,
} as const;

export const ROLE_PERMISSIONS = {
  head: [
    'candidates:read',
    'candidates:write',
    'candidates:delete',
    'jobs:read',
    'jobs:write',
    'jobs:delete',
    'applications:read',
    'applications:write',
    'applications:approve',
    'applications:reject',
    'staff:read',
    'staff:write',
    'reports:read',
    'reports:export',
  ],
  senior_staff: [
    'candidates:read',
    'candidates:write',
    'jobs:read',
    'jobs:write',
    'applications:read',
    'applications:write',
    'applications:approve',
    'applications:reject',
    'reports:read',
  ],
  staff: [
    'candidates:read',
    'candidates:write',
    'jobs:read',
    'applications:read',
    'applications:write',
  ],
} as const;

export const APPLICATION_STATUS = {
  DRAFT: 'draft',
  PENDING_REVIEW: 'pending_review',
  APPROVED: 'approved',
  REJECTED: 'rejected',
  SUBMITTED: 'submitted',
} as const;

export const CANDIDATE_STATUS = {
  ACTIVE: 'active',
  INACTIVE: 'inactive',
  HIRED: 'hired',
  WITHDRAWN: 'withdrawn',
} as const;

export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 20,
  MAX_LIMIT: 100,
} as const;

export const JWT_CONFIG = {
  ACCESS_TOKEN_EXPIRY: '15m',
  REFRESH_TOKEN_EXPIRY: '7d',
} as const;

export const FILE_UPLOAD = {
  MAX_FILE_SIZE: 5 * 1024 * 1024,
  ALLOWED_TYPES: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
  ALLOWED_EXTENSIONS: ['.pdf', '.doc', '.docx'],
} as const;
