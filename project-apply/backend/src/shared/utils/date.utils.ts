export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toISOString();
}

export function formatDateLocal(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function addDays(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

export function subtractDays(date: Date, days: number): Date {
  return addDays(date, -days);
}

export function isWithinDays(date: Date, days: number): boolean {
  const now = new Date();
  const daysAgo = subtractDays(now, days);
  return date >= daysAgo && date <= now;
}

export function getDateRange(startDate?: Date, endDate?: Date): { start: Date; end: Date } {
  const now = new Date();
  return {
    start: startDate || subtractDays(now, 30),
    end: endDate || now,
  };
}
