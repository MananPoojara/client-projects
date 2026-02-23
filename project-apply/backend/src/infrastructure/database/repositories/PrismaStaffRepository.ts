import { PrismaClient, Staff, Role } from '@prisma/client';
import { IStaffRepository } from '../../domain/repositories/IStaffRepository';
import { CreateStaffDTO } from '../../domain/entities/Staff';

export class PrismaStaffRepository implements IStaffRepository {
  constructor(private prisma: PrismaClient) {}

  async findById(id: string): Promise<Staff | null> {
    return this.prisma.staff.findUnique({ where: { id } });
  }

  async findByEmail(email: string): Promise<Staff | null> {
    return this.prisma.staff.findUnique({ where: { email: email.toLowerCase() } });
  }

  async create(data: CreateStaffDTO & { passwordHash: string }): Promise<Staff> {
    return this.prisma.staff.create({
      data: {
        email: data.email.toLowerCase(),
        passwordHash: data.passwordHash,
        firstName: data.firstName,
        lastName: data.lastName,
        role: data.role as Role,
        department: data.department,
      },
    });
  }

  async update(id: string, data: Partial<Staff>): Promise<Staff> {
    return this.prisma.staff.update({
      where: { id },
      data,
    });
  }

  async updateLastLogin(id: string): Promise<void> {
    await this.prisma.staff.update({
      where: { id },
      data: { lastLogin: new Date() },
    });
  }

  async findAll(): Promise<Staff[]> {
    return this.prisma.staff.findMany({
      orderBy: { createdAt: 'desc' },
    });
  }

  async findByRole(role: string): Promise<Staff[]> {
    return this.prisma.staff.findMany({
      where: { role: role as Role },
      orderBy: { createdAt: 'desc' },
    });
  }

  async deactivate(id: string): Promise<void> {
    await this.prisma.staff.update({
      where: { id },
      data: { isActive: false },
    });
  }

  async activate(id: string): Promise<void> {
    await this.prisma.staff.update({
      where: { id },
      data: { isActive: true },
    });
  }
}
