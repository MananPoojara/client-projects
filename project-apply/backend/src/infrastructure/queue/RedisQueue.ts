import Redis from 'ioredis';
import logger from '../../shared/utils/logger';

export interface ScrapeJob {
  id: string;
  board: string;
  keywords: string[];
  location: string;
  options?: {
    country?: string;
    datePosted?: number;
  };
  createdAt: string;
}

export interface ScrapeResult {
  jobId: string;
  status: 'success' | 'failed' | 'partial';
  jobsFound: number;
  jobsSaved: number;
  errors?: string[];
  completedAt: string;
}

class RedisQueue {
  private client: Redis | null = null;
  private subscriber: Redis | null = null;
  private isConnected: boolean = false;

  private readonly SCRAPE_QUEUE = 'scrape:jobs';
  private readonly SCRAPE_RESULTS = 'scrape:results';
  private readonly SCRAPE_STATUS = 'scrape:status';

  async connect(): Promise<void> {
    if (this.isConnected) return;

    const redisUrl = process.env.REDIS_URL || 'redis://localhost:6379';

    try {
      this.client = new Redis(redisUrl, {
        maxRetriesPerRequest: 3,
        retryStrategy: (times) => Math.min(times * 50, 2000),
      });

      this.subscriber = new Redis(redisUrl, {
        maxRetriesPerRequest: 3,
      });

      this.client.on('connect', () => {
        logger.info('Redis connected');
        this.isConnected = true;
      });

      this.client.on('error', (err) => {
        logger.error('Redis error:', err);
      });

      await this.client.ping();
    } catch (error) {
      logger.error('Failed to connect to Redis:', error);
      throw error;
    }
  }

  async disconnect(): Promise<void> {
    if (this.client) {
      await this.client.quit();
      this.client = null;
    }
    if (this.subscriber) {
      await this.subscriber.quit();
      this.subscriber = null;
    }
    this.isConnected = false;
    logger.info('Redis disconnected');
  }

  async enqueueScrapeJob(job: ScrapeJob): Promise<void> {
    if (!this.client) throw new Error('Redis not connected');

    await this.client.lpush(this.SCRAPE_QUEUE, JSON.stringify(job));
    logger.info(`Enqueued scrape job: ${job.id} for board: ${job.board}`);
  }

  async getScrapeJob(): Promise<ScrapeJob | null> {
    if (!this.client) throw new Error('Redis not connected');

    const job = await this.client.brpop(this.SCRAPE_QUEUE, 5);
    if (job) {
      return JSON.parse(job[1]) as ScrapeJob;
    }
    return null;
  }

  async publishResult(result: ScrapeResult): Promise<void> {
    if (!this.client) throw new Error('Redis not connected');

    await this.client.publish(this.SCRAPE_RESULTS, JSON.stringify(result));
    
    await this.client.hset(
      `${this.SCRAPE_STATUS}:${result.jobId}`,
      'result',
      JSON.stringify(result)
    );
    await this.client.expire(`${this.SCRAPE_STATUS}:${result.jobId}`, 3600);
  }

  async subscribeToResults(
    callback: (result: ScrapeResult) => void
  ): Promise<void> {
    if (!this.subscriber) throw new Error('Redis not connected');

    await this.subscriber.subscribe(this.SCRAPE_RESULTS);
    
    this.subscriber.on('message', (_, message) => {
      try {
        const result = JSON.parse(message) as ScrapeResult;
        callback(result);
      } catch (error) {
        logger.error('Error parsing scrape result:', error);
      }
    });
  }

  async setJobStatus(
    jobId: string,
    status: 'pending' | 'running' | 'completed' | 'failed'
  ): Promise<void> {
    if (!this.client) throw new Error('Redis not connected');

    await this.client.hset(
      `${this.SCRAPE_STATUS}:${jobId}`,
      'status',
      status
    );
    await this.client.expire(`${this.SCRAPE_STATUS}:${jobId}`, 3600);
  }

  async getJobStatus(jobId: string): Promise<string | null> {
    if (!this.client) throw new Error('Redis not connected');

    return await this.client.hget(`${this.SCRAPE_STATUS}:${jobId}`, 'status');
  }

  async getJobResult(jobId: string): Promise<ScrapeResult | null> {
    if (!this.client) throw new Error('Redis not connected');

    const result = await this.client.hget(
      `${this.SCRAPE_STATUS}:${jobId}`,
      'result'
    );
    return result ? JSON.parse(result) : null;
  }

  getClient(): Redis {
    if (!this.client) throw new Error('Redis not connected');
    return this.client;
  }
}

export const redisQueue = new RedisQueue();
