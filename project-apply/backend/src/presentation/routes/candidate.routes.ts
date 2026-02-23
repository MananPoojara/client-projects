import { Router, Response, NextFunction } from 'express';
import { z } from 'zod';
import { prisma } from '../../infrastructure/database';
import { authenticate } from '../middleware/auth.middleware';
import { asyncHandler } from '../middleware/asyncHandler.middleware';
import { validateBody, validateQuery } from '../middleware/validation.middleware';
import { NotFoundError, ConflictError } from '../../shared/errors';

const router = Router();

router.use(authenticate);

const createCandidateSchema = z.object({
  firstName: z.string().min(1).max(100),
  lastName: z.string().min(1).max(100),
  email: z.string().email(),
  phone: z.string().optional(),
  location: z.string().optional(),
  linkedinUrl: z.string().url().optional(),
  skills: z.array(z.string()).optional(),
  experienceYears: z.number().int().optional(),
  currentCompany: z.string().optional(),
  currentTitle: z.string().optional(),
  consentGdpr: z.boolean().optional(),
});

const updateCandidateSchema = createCandidateSchema.partial();

const filtersSchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  status: z.enum(['active', 'inactive', 'hired', 'withdrawn']).optional(),
  search: z.string().optional(),
  skills: z.string().optional(),
  minExperience: z.coerce.number().int().optional(),
  maxExperience: z.coerce.number().int().optional(),
});

router.get('/', validateQuery(filtersSchema), asyncHandler(async (req, res, next) => {
  const { page, limit, status, search, skills, minExperience, maxExperience } = req.query;
  
  const where: any = {};
  
  if (status) where.status = status;
  
  if (search) {
    where.OR = [
      { firstName: { contains: search, mode: 'insensitive' } },
      { lastName: { contains: search, mode: 'insensitive' } },
      { email: { contains: search, mode: 'insensitive' } },
    ];
  }

  if (skills) {
    const skillArray = skills.split(',').map(s => s.trim());
    where.skills = { hasSome: skillArray };
  }

  const skip = (Number(page) - 1) * Number(limit);

  const [data, total] = await Promise.all([
    prisma.candidate.findMany({
      where,
      skip,
      take: Number(limit),
      orderBy: { createdAt: 'desc' },
    }),
    prisma.candidate.count({ where }),
  ]);

  res.json({
    success: true,
    data,
    pagination: {
      page: Number(page),
      limit: Number(limit),
      total,
      totalPages: Math.ceil(total / Number(limit)),
    },
  });
}));

router.post('/', validateBody(createCandidateSchema), asyncHandler(async (req, res, next) => {
  const existing = await prisma.candidate.findUnique({
    where: { email: req.body.email.toLowerCase() },
  });

  if (existing) {
    throw new ConflictError('Candidate with this email already exists');
  }

  const candidate = await prisma.candidate.create({
    data: {
      ...req.body,
      email: req.body.email.toLowerCase(),
    },
  });

  res.status(201).json({ success: true, data: candidate, message: 'Candidate created' });
}));

router.get('/:id', asyncHandler(async (req, res, next) => {
  const candidate = await prisma.candidate.findUnique({
    where: { id: req.params.id },
  });

  if (!candidate) {
    throw new NotFoundError('Candidate not found');
  }

  res.json({ success: true, data: candidate });
}));

router.put('/:id', validateBody(updateCandidateSchema), asyncHandler(async (req, res, next) => {
  const existing = await prisma.candidate.findUnique({
    where: { id: req.params.id },
  });

  if (!existing) {
    throw new NotFoundError('Candidate not found');
  }

  if (req.body.email && req.body.email.toLowerCase() !== existing.email) {
    const emailExists = await prisma.candidate.findUnique({
      where: { email: req.body.email.toLowerCase() },
    });
    if (emailExists) {
      throw new ConflictError('Email already in use');
    }
  }

  const candidate = await prisma.candidate.update({
    where: { id: req.params.id },
    data: req.body.email ? { ...req.body, email: req.body.email.toLowerCase() } : req.body,
  });

  res.json({ success: true, data: candidate, message: 'Candidate updated' });
}));

router.delete('/:id', asyncHandler(async (req, res, next) => {
  const existing = await prisma.candidate.findUnique({
    where: { id: req.params.id },
  });

  if (!existing) {
    throw new NotFoundError('Candidate not found');
  }

  await prisma.candidate.delete({
    where: { id: req.params.id },
  });

  res.json({ success: true, message: 'Candidate deleted' });
}));

export default router;
