import { PrismaClient, Job, RemoteType } from '@prisma/client';
import { IJobRepository } from '../../domain/repositories/IJobRepository';
import { CreateJobDTO, UpdateJobDTO, JobFilters } from '../../domain/entities/Job';
import { PaginatedResult } from '../../domain/repositories/ICandidateRepository';

export class PrismaJobRepository implements IJobRepository {
  constructor(private prisma: PrismaClient) {}

  async findById(id: string): Promise<Job | null> {
    return this.prisma.job.findUnique({ where: { id } });
  }

  async create(data: CreateJobDTO): Promise<Job> {
    return this.prisma.job.create({
      data: {
        title: data.title,
        company: data.company,
        location: data.location,
        description: data.description,
        requirements: data.requirements || [],
        skillsRequired: data.skillsRequired || [],
        salaryMin: data.salaryMin,
        salaryMax: data.salaryMax,
        sourceUrl: data.sourceUrl,
        sourcePortal: data.sourcePortal,
        jobType: data.jobType,
        remoteType: data.remoteType,
        postedDate: data.postedDate,
      },
    });
  }

  async update(id: string, data: UpdateJobDTO): Promise<Job> {
    return this.prisma.job.update({
      where: { id },
      data,
    });
  }

  async delete(id: string): Promise<void> {
    await this.prisma.job.delete({ where: { id } });
  }

  async findAll(filters: JobFilters, page: number, limit: number): Promise<PaginatedResult<Job>> {
    const where: any = {};

    if (filters.status) {
      where.status = filters.status;
    }

    if (filters.workType) {
      where.remoteType = filters.workType as RemoteType;
    }

    if (filters.location) {
      where.location = { contains: filters.location, mode: 'insensitive' };
    }

    if (filters.source) {
      where.sourcePortal = filters.source;
    }

    if (filters.datePosted) {
      const date = new Date();
      date.setDate(date.getDate() - filters.datePosted);
      where.postedDate = { gte: date };
    }

    if (filters.search) {
      where.OR = [
        { title: { contains: filters.search, mode: 'insensitive' } },
        { company: { contains: filters.search, mode: 'insensitive' } },
        { description: { contains: filters.search, mode: 'insensitive' } },
      ];
    }

    if (filters.skills && filters.skills.length > 0) {
      where.skillsRequired = { hasSome: filters.skills };
    }

    const [data, total] = await Promise.all([
      this.prisma.job.findMany({
        where,
        skip: (page - 1) * limit,
        take: limit,
        orderBy: { createdAt: 'desc' },
      }),
      this.prisma.job.count({ where }),
    ]);

    return {
      data,
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit),
    };
  }

  async findBySkills(skills: string[]): Promise<Job[]> {
    return this.prisma.job.findMany({
      where: {
        skillsRequired: { hasSome: skills },
        status: 'active',
      },
    });
  }

  async findBySource(source: string): Promise<Job[]> {
    return this.prisma.job.findMany({
      where: { sourcePortal: source },
      orderBy: { createdAt: 'desc' },
    });
  }

  async bulkCreate(jobs: CreateJobDTO[]): Promise<Job[]> {
    const created = await this.prisma.job.createManyAndReturn({
      data: jobs.map(job => ({
        title: job.title,
        company: job.company,
        location: job.location,
        description: job.description,
        requirements: job.requirements || [],
        skillsRequired: job.skillsRequired || [],
        salaryMin: job.salaryMin,
        salaryMax: job.salaryMax,
        sourceUrl: job.sourceUrl,
        sourcePortal: job.sourcePortal,
        jobType: job.jobType,
        remoteType: job.remoteType,
        postedDate: job.postedDate,
      })),
    });
    return created;
  }
}
