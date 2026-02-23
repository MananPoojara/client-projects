import { Router, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { z } from 'zod';
import bcrypt from 'bcrypt';
import { prisma } from '../../infrastructure/database';
import { authenticate, AuthRequest } from '../middleware/auth.middleware';
import { asyncHandler } from '../middleware/asyncHandler.middleware';
import { validateBody } from '../middleware/validation.middleware';
import { UnauthorizedError, ConflictError } from '../../shared/errors';

const router = Router();

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});

const refreshSchema = z.object({
  refreshToken: z.string().min(1),
});

router.post('/login', validateBody(loginSchema), asyncHandler(async (req, res, next) => {
  const { email, password } = req.body;
  
  const staff = await prisma.staff.findUnique({
    where: { email: email.toLowerCase() },
  });

  if (!staff || !staff.isActive) {
    throw new UnauthorizedError('Invalid credentials');
  }

  const isValidPassword = await bcrypt.compare(password, staff.passwordHash);
  
  if (!isValidPassword) {
    throw new UnauthorizedError('Invalid credentials');
  }

  const secret = process.env.JWT_SECRET || 'default-secret';
  const refreshSecret = process.env.JWT_REFRESH_SECRET || 'default-refresh-secret';
  
  const accessToken = jwt.sign(
    { staffId: staff.id },
    secret,
    { expiresIn: '15m' }
  );

  const refreshToken = jwt.sign(
    { staffId: staff.id },
    refreshSecret,
    { expiresIn: '7d' }
  );

  const expiresAt = new Date();
  expiresAt.setDate(expiresAt.getDate() + 7);
  
  await prisma.refreshToken.create({
    data: {
      token: refreshToken,
      staffId: staff.id,
      expiresAt,
    },
  });

  await prisma.staff.update({
    where: { id: staff.id },
    data: { lastLogin: new Date() },
  });

  res.json({
    success: true,
    data: {
      accessToken,
      refreshToken,
      staff: {
        id: staff.id,
        email: staff.email,
        firstName: staff.firstName,
        lastName: staff.lastName,
        role: staff.role,
        department: staff.department,
      },
    },
    message: 'Login successful',
  });
}));

router.post('/refresh', validateBody(refreshSchema), asyncHandler(async (req, res, next) => {
  const { refreshToken } = req.body;
  
  const storedToken = await prisma.refreshToken.findUnique({
    where: { token: refreshToken },
    include: { staff: true },
  });

  if (!storedToken || storedToken.expiresAt < new Date()) {
    throw new UnauthorizedError('Invalid or expired refresh token');
  }

  if (!storedToken.staff.isActive) {
    throw new UnauthorizedError('Account is disabled');
  }

  await prisma.refreshToken.delete({
    where: { id: storedToken.id },
  });

  const secret = process.env.JWT_SECRET || 'default-secret';
  const refreshSecret = process.env.JWT_REFRESH_SECRET || 'default-refresh-secret';
  
  const newAccessToken = jwt.sign(
    { staffId: storedToken.staffId },
    secret,
    { expiresIn: '15m' }
  );

  const newRefreshToken = jwt.sign(
    { staffId: storedToken.staffId },
    refreshSecret,
    { expiresIn: '7d' }
  );

  const expiresAt = new Date();
  expiresAt.setDate(expiresAt.getDate() + 7);
  
  await prisma.refreshToken.create({
    data: {
      token: newRefreshToken,
      staffId: storedToken.staffId,
      expiresAt,
    },
  });

  res.json({
    success: true,
    data: { accessToken: newAccessToken, refreshToken: newRefreshToken },
    message: 'Token refreshed',
  });
}));

router.post('/logout', authenticate, asyncHandler(async (req, res, next) => {
  const authReq = req as AuthRequest;
  const { refreshToken } = req.body;
  
  if (refreshToken) {
    await prisma.refreshToken.deleteMany({
      where: { token: refreshToken },
    });
  }

  res.json({
    success: true,
    message: 'Logged out successfully',
  });
}));

router.get('/me', authenticate, asyncHandler(async (req, res, next) => {
  const authReq = req as AuthRequest;
  
  const staff = await prisma.staff.findUnique({
    where: { id: authReq.staff!.id },
    select: {
      id: true,
      email: true,
      firstName: true,
      lastName: true,
      role: true,
      department: true,
      isActive: true,
      lastLogin: true,
      createdAt: true,
    },
  });

  res.json({ success: true, data: staff });
}));

export default router;
