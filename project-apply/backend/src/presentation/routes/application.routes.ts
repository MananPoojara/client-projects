import { Router } from 'express';
import { z } from 'zod';
import { prisma } from '../../infrastructure/database';
import { authenticate, AuthRequest } from '../middleware/auth.middleware';
import { asyncHandler } from '../middleware/asyncHandler.middleware';
import { validateBody, validateQuery } from '../middleware/validation.middleware';
import { NotFoundError, ForbiddenError } from '../../shared/errors';

const router = Router();
router.use(authenticate);

const createApplicationSchema = z.object({
  candidateId: z.string().uuid(),
  jobId: z.string().uuid(),
  coverLetter: z.string().optional(),
  staffNotes: z.string().optional(),
});

const filtersSchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  status: z.enum(['draft', 'pending_review', 'approved', 'rejected', 'submitted']).optional(),
  staffId: z.string().uuid().optional(),
  candidateId: z.string().uuid().optional(),
});

router.get('/', validateQuery(filtersSchema), asyncHandler(async (req, res) => {
  const authReq = req as AuthRequest;
  const { page, limit, status, staffId, candidateId } = req.query;
  
  const where: any = {};
  if (status) where.status = status;
  if (staffId) where.staffId = staffId;
  if (candidateId) where.candidateId = candidateId;

  const skip = (Number(page) - 1) * Number(limit);
  const [data, total] = await Promise.all([
    prisma.application.findMany({ 
      where, 
      skip, 
      take: Number(limit), 
      orderBy: { createdAt: 'desc' },
      include: { candidate: true, job: true },
    }),
    prisma.application.count({ where }),
  ]);

  res.json({ success: true, data, pagination: { page: Number(page), limit: Number(limit), total, totalPages: Math.ceil(total / Number(limit)) } });
}));

router.post('/', validateBody(createApplicationSchema), asyncHandler(async (req, res) => {
  const authReq = req as AuthRequest;
  
  const [candidate, job] = await Promise.all([
    prisma.candidate.findUnique({ where: { id: req.body.candidateId } }),
    prisma.job.findUnique({ where: { id: req.body.jobId } }),
  ]);

  if (!candidate || !job) throw new NotFoundError('Candidate or Job not found');

  const application = await prisma.application.create({
    data: { ...req.body, staffId: authReq.staff!.id },
  });

  res.status(201).json({ success: true, data: application });
}));

router.get('/:id', asyncHandler(async (req, res) => {
  const application = await prisma.application.findUnique({ 
    where: { id: req.params.id },
    include: { candidate: true, job: true },
  });
  if (!application) throw new NotFoundError('Application not found');
  res.json({ success: true, data: application });
}));

router.put('/:id', validateBody(createApplicationSchema.partial()), asyncHandler(async (req, res) => {
  const application = await prisma.application.update({ where: { id: req.params.id }, data: req.body });
  res.json({ success: true, data: application });
}));

router.post('/:id/approve', asyncHandler(async (req, res) => {
  const authReq = req as AuthRequest;
  if (!['head', 'senior_staff'].includes(authReq.staff!.role)) {
    throw new ForbiddenError('Only head or senior staff can approve');
  }
  const application = await prisma.application.update({
    where: { id: req.params.id },
    data: { status: 'approved', reviewerId: authReq.staff!.id, reviewedAt: new Date() },
  });
  res.json({ success: true, data: application });
}));

router.post('/:id/reject', asyncHandler(async (req, res) => {
  const authReq = req as AuthRequest;
  const { reason } = req.body;
  if (!reason) throw new ForbiddenError('Rejection reason required');
  
  const application = await prisma.application.update({
    where: { id: req.params.id },
    data: { status: 'rejected', reviewerId: authReq.staff!.id, reviewedAt: new Date(), staffNotes: reason },
  });
  res.json({ success: true, data: application });
}));

router.delete('/:id', asyncHandler(async (req, res) => {
  await prisma.application.delete({ where: { id: req.params.id } });
  res.json({ success: true, message: 'Application deleted' });
}));

export default router;
