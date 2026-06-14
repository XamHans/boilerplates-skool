import type { NextRequest } from 'next/server';
import { withAuth } from '@/lib/api/handlers';
import { parseRequestBody } from '@/lib/validation/parse';
import { paymentService } from '@/modules/payments/services/payment.service';
import type { CreatePaymentInput } from '@/modules/payments/types';
import { z } from 'zod';

const createPaymentSchema = z.object({
  amount: z.string().regex(/^\d+\.\d{2}$/, 'Amount must be in format: 10.00'),
  currency: z.enum(['EUR', 'USD', 'GBP', 'CHF', 'PLN'], {
    errorMap: () => ({ message: 'Invalid currency' }),
  }),
  description: z.string().min(1),
  metadata: z.record(z.any()).optional(),
});

/**
 * POST /api/payments/create
 * Create a new payment via Stripe Checkout
 */
export const POST = withAuth(async (session, request: NextRequest) => {
  const bodyResult = await parseRequestBody(request, createPaymentSchema);
  if (!bodyResult.success) return bodyResult;

  const data = bodyResult.data as CreatePaymentInput; // Type assertion since schema matches

  return paymentService.createPayment(data, session.user.id);
});
