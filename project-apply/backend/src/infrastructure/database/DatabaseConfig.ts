import { PrismaClient } from '@prisma/client';
import logger from '../../shared/utils/logger';

class DatabaseConfig {
  private static instance: DatabaseConfig;
  private client: PrismaClient;
  private isConnected: boolean = false;

  private constructor() {
    this.client = new PrismaClient({
      log: process.env.NODE_ENV === 'development' 
        ? ['query', 'info', 'warn', 'error'] 
        : ['warn', 'error'],
    });
  }

  static getInstance(): DatabaseConfig {
    if (!DatabaseConfig.instance) {
      DatabaseConfig.instance = new DatabaseConfig();
    }
    return DatabaseConfig.instance;
  }

  async connect(): Promise<void> {
    if (this.isConnected) return;

    try {
      await this.client.$connect();
      this.isConnected = true;
      logger.info('Database connected successfully');
    } catch (error) {
      logger.error('Database connection failed:', error);
      throw error;
    }
  }

  async disconnect(): Promise<void> {
    if (!this.isConnected) return;
    
    await this.client.$disconnect();
    this.isConnected = false;
    logger.info('Database disconnected');
  }

  getClient(): PrismaClient {
    return this.client;
  }

  async healthCheck(): Promise<{ status: string; timestamp?: string; error?: string }> {
    try {
      if (!this.isConnected) {
        return { status: 'disconnected' };
      }
      await this.client.$queryRaw`SELECT 1`;
      return { status: 'connected', timestamp: new Date().toISOString() };
    } catch (error) {
      return { status: 'error', error: (error as Error).message };
    }
  }
}

export const database = DatabaseConfig.getInstance();
export const prisma = database.getClient();
