import { Router } from 'express';
import { prisma } from '../../infrastructure/database';
import { authenticate, AuthRequest } from '../middleware/auth.middleware';
import { asyncHandler } from '../middleware/asyncHandler.middleware';
import { isHead } from '../middleware/rbac.middleware';

const router = Router();
router.use(authenticate);
router.use(isHead);

router.get('/staff-progress', asyncHandler(async (req, res) => {
  const staffMembers = await prisma.staff.findMany({
    select: {
      id: true,
      firstName: true,
      lastName: true,
      role: true,
      department: true,
      _count: { select: { applications: true } },
    },
  });

  const progress = await Promise.all(
    staffMembers.map(async (staff) => {
      const submitted = await prisma.application.count({
        where: { staffId: staff.id, status: 'submitted' },
      });
      return { ...staff, submitted, total: staff._count.applications };
    })
  );

  res.json({ success: true, data: progress });
}));

router.get('/team-stats', asyncHandler(async (req, res) => {
  const [totalCandidates, totalJobs, totalApplications, byStatus] = await Promise.all([
    prisma.candidate.count(),
    prisma.job.count(),
    prisma.application.count(),
    prisma.application.groupBy({ by: ['status'], _count: { status: true } }),
  ]);

  res.json({
    success: true,
    data: { totalCandidates, totalJobs, totalApplications, byStatus },
  });
}));

export default router;
