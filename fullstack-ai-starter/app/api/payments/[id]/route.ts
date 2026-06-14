import type { NextRequest } from 'next/server';
import { ApiError, withAuthentication } from '@/lib/api/base';
import { paymentService } from '@/modules/payments/services/payment.service';

/**
 * GET /api/payments/[id]
 * Get payment details by ID
 *
 * Requires authentication
 * Authorization: User can only view their own payments
 */
export const GET = withAuthentication(async (session, request: NextRequest, context, logger) => {

  const params = await context.params;
  const id = params?.id as string;

  if (!id) {
    throw new ApiError(400, 'Payment ID is required', 'MISSING_ID');
  }

  logger?.info('Fetching payment details', {
    operation: 'getPayment',
    paymentId: id,
    userId: session.user.id,
  });

  const payment = await paymentService.getPaymentById(id);

  if (!payment) {
    throw new ApiError(404, 'Payment not found', 'PAYMENT_NOT_FOUND');
  }

  // Authorization check - user can only view their own payments
  if (payment.userId !== session.user.id) {
    logger?.warn('Unauthorized payment access attempt', {
      operation: 'getPayment',
      paymentId: id,
      requestingUserId: session.user.id,
      paymentUserId: payment.userId,
    });
    throw new ApiError(403, 'You do not have permission to view this payment', 'FORBIDDEN');
  }

  return { payment };
});
