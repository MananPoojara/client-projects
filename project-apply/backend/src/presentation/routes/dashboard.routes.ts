import { Router } from 'express';
import { prisma } from '../../infrastructure/database';
import { authenticate, AuthRequest } from '../middleware/auth.middleware';
import { asyncHandler } from '../middleware/asyncHandler.middleware';

const router = Router();
router.use(authenticate);

router.get('/stats', asyncHandler(async (req, res) => {
  const authReq = req as AuthRequest;
  const staffId = authReq.staff!.id;

  const [totalApplications, pendingReview, approved, submitted] = await Promise.all([
    prisma.application.count({ where: { staffId } }),
    prisma.application.count({ where: { staffId, status: 'pending_review' } }),
    prisma.application.count({ where: { staffId, status: 'approved' } }),
    prisma.application.count({ where: { staffId, status: 'submitted' } }),
  ]);

  res.json({
    success: true,
    data: { totalApplications, pendingReview, approved, submitted },
  });
}));

router.get('/activity', asyncHandler(async (req, res) => {
  const authReq = req as AuthRequest;
  
  const activities = await prisma.staffActivity.findMany({
    where: { staffId: authReq.staff!.id },
    orderBy: { createdAt: 'desc' },
    take: 20,
  });

  res.json({ success: true, data: activities });
}));

export default router;
