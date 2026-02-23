import { Response, NextFunction } from 'express';
import { AuthRequest } from './auth.middleware';
import { ForbiddenError } from '../../shared/errors';
import { ROLE_PERMISSIONS } from '../../shared/constants';

export const authorize = (...allowedPermissions: string[]) => {
  return (req: Request, res: Response, next: NextFunction): void => {
    const authReq = req as AuthRequest;
    
    if (!authReq.staff) {
      next(new ForbiddenError('Not authenticated'));
      return;
    }

    const userPermissions = ROLE_PERMISSIONS[authReq.staff.role as keyof typeof ROLE_PERMISSIONS] || [];
    const hasPermission = allowedPermissions.some(permission => 
      userPermissions.includes(permission as any)
    );

    if (!hasPermission) {
      next(new ForbiddenError('Insufficient permissions'));
      return;
    }

    next();
  };
};

export const isHead = (req: Request, res: Response, next: NextFunction): void => {
  const authReq = req as AuthRequest;
  
  if (!authReq.staff || authReq.staff.role !== 'head') {
    next(new ForbiddenError('Head access required'));
    return;
  }
  
  next();
};

export const isSeniorOrHead = (req: Request, res: Response, next: NextFunction): void => {
  const authReq = req as AuthRequest;
  
  if (!authReq.staff || !['head', 'senior_staff'].includes(authReq.staff.role)) {
    next(new ForbiddenError('Senior staff or head access required'));
    return;
  }
  
  next();
};
