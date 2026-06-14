import type { NextRequest } from 'next/server';
import { withAuthentication } from '@/lib/api/base';
import { paymentService } from '@/modules/payments/services/payment.service';

/**
 * GET /api/payments
 * List user's payments with optional filters
 *
 * Requires authentication
 * Supports filtering by status
 * Supports pagination via limit and offset
 */
export const GET = withAuthentication(async (session, request: NextRequest, context, logger) => {

  const { searchParams } = new URL(request.url);
  const status = searchParams.get('status') || undefined;
  const limit = Math.min(Number.parseInt(searchParams.get('limit') || '20'), 100);
  const offset = Math.max(Number.parseInt(searchParams.get('offset') || '0'), 0);

  logger?.info('Fetching user payments', {
    operation: 'getUserPayments',
    userId: session.user.id,
    status,
    limit,
    offset,
  });

  const payments = await paymentService.getUserPayments({
    userId: session.user.id,
    status,
    limit,
    offset,
  });

  logger?.debug('Payments fetched successfully', {
    operation: 'getUserPayments',
    count: payments.length,
  });

  return { payments };
});
