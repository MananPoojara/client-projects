import { Staff, CreateStaffDTO } from '../entities/Staff';

export interface IStaffRepository {
  findById(id: string): Promise<Staff | null>;
  findByEmail(email: string): Promise<Staff | null>;
  create(data: CreateStaffDTO & { passwordHash: string }): Promise<Staff>;
  update(id: string, data: Partial<Staff>): Promise<Staff>;
  updateLastLogin(id: string): Promise<void>;
  findAll(): Promise<Staff[]>;
  findByRole(role: string): Promise<Staff[]>;
  deactivate(id: string): Promise<void>;
  activate(id: string): Promise<void>;
}
