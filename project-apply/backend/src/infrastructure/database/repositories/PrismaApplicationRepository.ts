import { PrismaClient, Application, ApplicationStatus } from '@prisma/client';
import { IApplicationRepository } from '../../domain/repositories/IApplicationRepository';
import { CreateApplicationDTO, UpdateApplicationDTO, ApplicationFilters } from '../../domain/entities/Application';
import { PaginatedResult } from '../../domain/repositories/ICandidateRepository';

export class PrismaApplicationRepository implements IApplicationRepository {
  constructor(private prisma: PrismaClient) {}

  async findById(id: string): Promise<Application | null> {
    return this.prisma.application.findUnique({ where: { id } });
  }

  async create(data: CreateApplicationDTO): Promise<Application> {
    return this.prisma.application.create({
      data: {
        candidateId: data.candidateId,
        jobId: data.jobId,
        staffId: data.staffId,
        coverLetter: data.coverLetter,
        staffNotes: data.staffNotes,
      },
    });
  }

  async update(id: string, data: UpdateApplicationDTO): Promise<Application> {
    return this.prisma.application.update({
      where: { id },
      data,
    });
  }

  async delete(id: string): Promise<void> {
    await this.prisma.application.delete({ where: { id } });
  }

  async findAll(filters: ApplicationFilters, page: number, limit: number): Promise<PaginatedResult<Application>> {
    const where: any = {};

    if (filters.status) {
      where.status = filters.status as ApplicationStatus;
    }

    if (filters.staffId) {
      where.staffId = filters.staffId;
    }

    if (filters.candidateId) {
      where.candidateId = filters.candidateId;
    }

    const [data, total] = await Promise.all([
      this.prisma.application.findMany({
        where,
        skip: (page - 1) * limit,
        take: limit,
        orderBy: { createdAt: 'desc' },
        include: {
          candidate: true,
          job: true,
        },
      }),
      this.prisma.application.count({ where }),
    ]);

    return {
      data,
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit),
    };
  }

  async findByCandidate(candidateId: string): Promise<Application[]> {
    return this.prisma.application.findMany({
      where: { candidateId },
      orderBy: { createdAt: 'desc' },
    });
  }

  async findByJob(jobId: string): Promise<Application[]> {
    return this.prisma.application.findMany({
      where: { jobId },
      orderBy: { createdAt: 'desc' },
    });
  }

  async findByStaff(staffId: string): Promise<Application[]> {
    return this.prisma.application.findMany({
      where: { staffId },
      orderBy: { createdAt: 'desc' },
    });
  }

  async findPendingReview(): Promise<Application[]> {
    return this.prisma.application.findMany({
      where: { status: ApplicationStatus.PENDING_REVIEW },
      orderBy: { createdAt: 'asc' },
      include: {
        candidate: true,
        job: true,
        staff: true,
      },
    });
  }

  async bulkCreate(applications: CreateApplicationDTO[]): Promise<Application[]> {
    return this.prisma.application.createManyAndReturn({
      data: applications.map(app => ({
        candidateId: app.candidateId,
        jobId: app.jobId,
        staffId: app.staffId,
        coverLetter: app.coverLetter,
        staffNotes: app.staffNotes,
      })),
    });
  }

  async approve(id: string, reviewerId: string): Promise<Application> {
    return this.prisma.application.update({
      where: { id },
      data: {
        status: ApplicationStatus.APPROVED,
        reviewerId,
        reviewedAt: new Date(),
      },
    });
  }

  async reject(id: string, reviewerId: string, reason: string): Promise<Application> {
    return this.prisma.application.update({
      where: { id },
      data: {
        status: ApplicationStatus.REJECTED,
        reviewerId,
        reviewedAt: new Date(),
        staffNotes: reason,
      },
    });
  }

  async markSubmitted(id: string): Promise<Application> {
    return this.prisma.application.update({
      where: { id },
      data: {
        status: ApplicationStatus.SUBMITTED,
        submittedAt: new Date(),
      },
    });
  }
}
