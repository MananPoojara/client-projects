import { createApp } from './app';
import { database, redisQueue } from './infrastructure';
import logger from './shared/utils/logger';

const PORT = process.env.PORT || 3000;

async function startServer() {
  try {
    await database.connect();
    logger.info('Database connected');

    await redisQueue.connect();
    logger.info('Redis queue connected');

    const app = await createApp();

    const server = app.listen(PORT, () => {
      logger.info(`Server started on port ${PORT}`);
      logger.info(`Health check: http://localhost:${PORT}/health`);
    });

    const gracefulShutdown = async (signal: string) => {
      logger.info(`${signal} received. Starting graceful shutdown...`);
      
      server.close(async () => {
        logger.info('HTTP server closed');
        
        await redisQueue.disconnect();
        logger.info('Redis disconnected');
        
        await database.disconnect();
        logger.info('Database disconnected');
        
        process.exit(0);
      });

      setTimeout(() => {
        logger.error('Forced shutdown after timeout');
        process.exit(1);
      }, 30000);
    };

    process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
    process.on('SIGINT', () => gracefulShutdown('SIGINT'));

    process.on('unhandledRejection', (reason, promise) => {
      logger.error({ type: 'unhandled_rejection', reason, promise });
    });

    process.on('uncaughtException', (error) => {
      logger.error({ type: 'uncaught_exception', error: error.message, stack: error.stack });
      process.exit(1);
    });

  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
}

startServer();
