import { Router } from 'express';
import { z } from 'zod';
import { v4 as uuidv4 } from 'uuid';
import { prisma, redisQueue } from '../../infrastructure';
import { authenticate } from '../middleware/auth.middleware';
import { asyncHandler } from '../middleware/asyncHandler.middleware';
import { validateBody, validateQuery } from '../middleware/validation.middleware';
import { NotFoundError, BadRequestError } from '../../shared/errors';

const router = Router();
router.use(authenticate);

const createJobSchema = z.object({
  title: z.string().min(1).max(255),
  company: z.string().min(1).max(255),
  location: z.string().optional(),
  description: z.string().optional(),
  requirements: z.array(z.string()).optional(),
  skillsRequired: z.array(z.string()).optional(),
  salaryMin: z.number().int().optional(),
  salaryMax: z.number().int().optional(),
  sourceUrl: z.string().url().optional(),
  sourcePortal: z.string().optional(),
  jobType: z.enum(['full_time', 'part_time', 'contract', 'internship', 'temporary']).optional(),
  remoteType: z.enum(['remote', 'hybrid', 'onsite']).optional(),
  postedDate: z.string().optional(),
});

const filtersSchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  status: z.enum(['active', 'inactive', 'closed']).optional(),
  workType: z.enum(['remote', 'hybrid', 'onsite']).optional(),
  location: z.string().optional(),
  source: z.string().optional(),
  datePosted: z.coerce.number().int().optional(),
  search: z.string().optional(),
  skills: z.string().optional(),
});

const syncJobSchema = z.object({
  board: z.enum(['jooble', 'remotive', 'indeed', 'linkedin', 'all']),
  keywords: z.array(z.string()).min(1).max(10),
  location: z.string().optional().default(''),
  options: z.object({
    country: z.string().optional(),
    datePosted: z.number().int().min(1).max(30).optional(),
  }).optional(),
});

router.get('/', validateQuery(filtersSchema), asyncHandler(async (req, res) => {
  const { page, limit, status, workType, location, source, datePosted, search, skills } = req.query;
  
  const where: any = {};
  if (status) where.status = status;
  if (workType) where.remoteType = workType;
  if (location) where.location = { contains: location, mode: 'insensitive' };
  if (source) where.sourcePortal = source;
  if (search) {
    where.OR = [
      { title: { contains: search, mode: 'insensitive' } },
      { company: { contains: search, mode: 'insensitive' } },
    ];
  }
  if (skills) {
    where.skillsRequired = { hasSome: skills.split(',').map(s => s.trim()) };
  }

  const skip = (Number(page) - 1) * Number(limit);
  const [data, total] = await Promise.all([
    prisma.job.findMany({ where, skip, take: Number(limit), orderBy: { createdAt: 'desc' } }),
    prisma.job.count({ where }),
  ]);

  res.json({ success: true, data, pagination: { page: Number(page), limit: Number(limit), total, totalPages: Math.ceil(total / Number(limit)) } });
}));

router.post('/', validateBody(createJobSchema), asyncHandler(async (req, res) => {
  const job = await prisma.job.create({ data: req.body });
  res.status(201).json({ success: true, data: job });
}));

router.post('/sync', validateBody(syncJobSchema), asyncHandler(async (req, res) => {
  const { board, keywords, location, options } = req.body;

  const jobId = uuidv4();

  const scrapeJob = {
    id: jobId,
    board,
    keywords,
    location: location || '',
    options: options || {},
    createdAt: new Date().toISOString(),
  };

  await redisQueue.enqueueScrapeJob(scrapeJob);
  await redisQueue.setJobStatus(jobId, 'pending');

  res.status(202).json({
    success: true,
    data: {
      jobId,
      status: 'pending',
      board,
      keywords,
      location,
    },
    message: `Scrape job ${jobId} queued successfully`,
  });
}));

router.get('/sync/status/:jobId', asyncHandler(async (req, res) => {
  const { jobId } = req.params;

  const status = await redisQueue.getJobStatus(jobId);
  const result = await redisQueue.getJobResult(jobId);

  if (!status) {
    throw new NotFoundError('Job not found');
  }

  res.json({
    success: true,
    data: {
      jobId,
      status,
      result,
    },
  });
}));

router.get('/:id', asyncHandler(async (req, res) => {
  const job = await prisma.job.findUnique({ where: { id: req.params.id } });
  if (!job) throw new NotFoundError('Job not found');
  res.json({ success: true, data: job });
}));

router.put('/:id', validateBody(createJobSchema.partial()), asyncHandler(async (req, res) => {
  const job = await prisma.job.update({ where: { id: req.params.id }, data: req.body });
  res.json({ success: true, data: job });
}));

router.delete('/:id', asyncHandler(async (req, res) => {
  await prisma.job.delete({ where: { id: req.params.id } });
  res.json({ success: true, message: 'Job deleted' });
}));

export default router;
