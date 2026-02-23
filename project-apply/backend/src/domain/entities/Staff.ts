export enum Role {
  HEAD = 'head',
  SENIOR_STAFF = 'senior_staff',
  STAFF = 'staff',
}

export interface Staff {
  id: string;
  email: string;
  passwordHash: string;
  firstName: string;
  lastName: string;
  role: Role;
  department?: string;
  isActive: boolean;
  lastLogin?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateStaffDTO {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  role: Role;
  department?: string;
}

export interface StaffLoginDTO {
  email: string;
  password: string;
}
