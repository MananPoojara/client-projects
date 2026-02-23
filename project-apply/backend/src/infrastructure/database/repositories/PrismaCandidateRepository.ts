import { PrismaClient, Candidate, CandidateStatus } from '@prisma/client';
import { ICandidateRepository, CandidateFilters, PaginatedResult } from '../../domain/repositories/ICandidateRepository';
import { CreateCandidateDTO, UpdateCandidateDTO } from '../../domain/entities/Candidate';

export class PrismaCandidateRepository implements ICandidateRepository {
  constructor(private prisma: PrismaClient) {}

  async findById(id: string): Promise<Candidate | null> {
    return this.prisma.candidate.findUnique({ where: { id } });
  }

  async findByEmail(email: string): Promise<Candidate | null> {
    return this.prisma.candidate.findUnique({ where: { email: email.toLowerCase() } });
  }

  async create(data: CreateCandidateDTO): Promise<Candidate> {
    return this.prisma.candidate.create({
      data: {
        firstName: data.firstName,
        lastName: data.lastName,
        email: data.email.toLowerCase(),
        phone: data.phone,
        location: data.location,
        linkedinUrl: data.linkedinUrl,
        skills: data.skills || [],
        experienceYears: data.experienceYears,
        currentCompany: data.currentCompany,
        currentTitle: data.currentTitle,
        consentGdpr: data.consentGdpr || false,
      },
    });
  }

  async update(id: string, data: UpdateCandidateDTO): Promise<Candidate> {
    return this.prisma.candidate.update({
      where: { id },
      data: {
        ...data,
        email: data.email?.toLowerCase(),
      },
    });
  }

  async delete(id: string): Promise<void> {
    await this.prisma.candidate.delete({ where: { id } });
  }

  async findAll(filters: CandidateFilters, page: number, limit: number): Promise<PaginatedResult<Candidate>> {
    const where: any = {};

    if (filters.status) {
      where.status = filters.status as CandidateStatus;
    }

    if (filters.search) {
      where.OR = [
        { firstName: { contains: filters.search, mode: 'insensitive' } },
        { lastName: { contains: filters.search, mode: 'insensitive' } },
        { email: { contains: filters.search, mode: 'insensitive' } },
        { currentCompany: { contains: filters.search, mode: 'insensitive' } },
        { currentTitle: { contains: filters.search, mode: 'insensitive' } },
      ];
    }

    if (filters.skills && filters.skills.length > 0) {
      where.skills = { hasSome: filters.skills };
    }

    if (filters.minExperience || filters.maxExperience) {
      where.experienceYears = {};
      if (filters.minExperience) where.experienceYears.gte = filters.minExperience;
      if (filters.maxExperience) where.experienceYears.lte = filters.maxExperience;
    }

    const [data, total] = await Promise.all([
      this.prisma.candidate.findMany({
        where,
        skip: (page - 1) * limit,
        take: limit,
        orderBy: { createdAt: 'desc' },
      }),
      this.prisma.candidate.count({ where }),
    ]);

    return {
      data,
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit),
    };
  }

  async updateResumePath(id: string, path: string): Promise<Candidate> {
    return this.prisma.candidate.update({
      where: { id },
      data: { resumePath: path },
    });
  }

  async findBySkills(skills: string[]): Promise<Candidate[]> {
    return this.prisma.candidate.findMany({
      where: {
        skills: { hasSome: skills },
        status: CandidateStatus.ACTIVE,
      },
    });
  }
}
