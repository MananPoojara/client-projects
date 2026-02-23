import 'dotenv/config';
import express, { Express } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { database, redisQueue } from '../infrastructure';
import logger from '../shared/utils/logger';
import authRoutes from '../presentation/routes/auth.routes';
import candidateRoutes from '../presentation/routes/candidate.routes';
import jobRoutes from '../presentation/routes/job.routes';
import applicationRoutes from '../presentation/routes/application.routes';
import dashboardRoutes from '../presentation/routes/dashboard.routes';
import reportRoutes from '../presentation/routes/report.routes';
import { errorHandler } from '../presentation/middleware/errorHandler.middleware';
import { notFoundHandler } from '../presentation/middleware/errorHandler.middleware';
import { authLimiter, apiLimiter } from '../presentation/middleware/rateLimiter.middleware';

export async function createApp(): Promise<Express> {
  const app = express();

  app.use(helmet());
  app.use(cors());
  app.use(express.json({ limit: '10mb' }));
  app.use(express.urlencoded({ extended: true, limit: '10mb' }));

  app.use('/api/auth/login', authLimiter);
  app.use('/api/auth/refresh', authLimiter);
  app.use('/api', apiLimiter);

  app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
  });

  app.get('/api/health', async (req, res) => {
    const [dbHealth, redisHealth] = await Promise.all([
      database.healthCheck(),
      redisQueue.getClient().ping().then(() => ({ status: 'connected' })).catch((e) => ({ status: 'error', error: e.message }))
    ]);
    
    res.json({
      status: 'ok',
      timestamp: new Date().toISOString(),
      services: { database: dbHealth, redis: redisHealth },
    });
  });

  app.use('/api/auth', authRoutes);
  app.use('/api/candidates', candidateRoutes);
  app.use('/api/jobs', jobRoutes);
  app.use('/api/applications', applicationRoutes);
  app.use('/api/dashboard', dashboardRoutes);
  app.use('/api/reports', reportRoutes);

  app.use(notFoundHandler);
  app.use(errorHandler);

  return app;
}
