import type { NextRequest } from 'next/server';
import Stripe from 'stripe';
import { ApiError, withErrorHandling } from '@/lib/api/base';
import { paymentService } from '@/modules/payments/services/payment.service';

/**
 * POST /api/payments/webhook
 * Handle Stripe webhook events
 *
 * No authentication required (validated by signature)
 * Verifies webhook signature using Stripe SDK
 * Updates payment status from Stripe events
 * Records webhook event for audit trail
 */
export const POST = withErrorHandling(async (request: NextRequest, context, logger) => {

  logger?.info('Received Stripe webhook', { operation: 'webhookHandler' });

  // Get raw body for signature verification (CRITICAL for Stripe)
  const rawBody = await request.text();
  const signature = request.headers.get('stripe-signature');

  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

  if (!webhookSecret) {
    logger?.error('STRIPE_WEBHOOK_SECRET not configured', { operation: 'webhookHandler' });
    throw new ApiError(500, 'Webhook secret not configured', 'WEBHOOK_SECRET_MISSING');
  }

  if (!signature) {
    logger?.warn('Missing Stripe signature', { operation: 'webhookHandler' });
    throw new ApiError(400, 'Missing signature', 'MISSING_SIGNATURE');
  }

  let event: Stripe.Event;

  try {
    // Stripe SDK handles all signature verification
    const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || '', {
      apiVersion: '2023-10-16',
    });

    event = stripe.webhooks.constructEvent(rawBody, signature, webhookSecret);
  } catch (error) {
    logger?.warn('Invalid webhook signature', {
      operation: 'webhookHandler',
      error: error instanceof Error ? error.message : 'Unknown error',
    });
    throw new ApiError(400, 'Invalid signature', 'INVALID_SIGNATURE');
  }

  logger?.info('Webhook signature verified', {
    operation: 'webhookHandler',
    eventType: event.type,
    eventId: event.id,
  });

  // Handle relevant event types
  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object as Stripe.Checkout.Session;

      const payment = await paymentService.getPaymentByStripeSessionId(session.id);

      if (!payment) {
        logger?.warn('Payment not found for checkout session', {
          operation: 'webhookHandler',
          sessionId: session.id,
        });
        return { status: 'ignored', reason: 'payment_not_found' };
      }

      const updatedPayment = await paymentService.updatePaymentStatus({
        stripeCheckoutSessionId: session.id,
      });

      await paymentService.recordWebhookEvent(
        payment.id,
        updatedPayment.stripePaymentIntentId,
        session.id,
        event.type,
        updatedPayment.status,
        event.data.object,
      );

      logger?.info('Checkout session completed', {
        operation: 'webhookHandler',
        paymentId: payment.id,
        sessionId: session.id,
        status: updatedPayment.status,
      });

      break;
    }

    case 'payment_intent.succeeded': {
      const paymentIntent = event.data.object as Stripe.PaymentIntent;

      const payment = await paymentService.getPaymentByStripeIntentId(paymentIntent.id);

      if (!payment) {
        logger?.warn('Payment not found for payment intent', {
          operation: 'webhookHandler',
          paymentIntentId: paymentIntent.id,
        });
        return { status: 'ignored', reason: 'payment_not_found' };
      }

      const updatedPayment = await paymentService.updatePaymentStatus({
        stripePaymentIntentId: paymentIntent.id,
      });

      await paymentService.recordWebhookEvent(
        payment.id,
        paymentIntent.id,
        payment.stripeCheckoutSessionId!,
        event.type,
        updatedPayment.status,
        event.data.object,
      );

      logger?.info('Payment intent succeeded', {
        operation: 'webhookHandler',
        paymentId: payment.id,
        paymentIntentId: paymentIntent.id,
      });

      break;
    }

    case 'payment_intent.payment_failed': {
      const paymentIntent = event.data.object as Stripe.PaymentIntent;

      const payment = await paymentService.getPaymentByStripeIntentId(paymentIntent.id);

      if (!payment) {
        return { status: 'ignored', reason: 'payment_not_found' };
      }

      const updatedPayment = await paymentService.updatePaymentStatus({
        stripePaymentIntentId: paymentIntent.id,
      });

      await paymentService.recordWebhookEvent(
        payment.id,
        paymentIntent.id,
        payment.stripeCheckoutSessionId!,
        event.type,
        updatedPayment.status,
        event.data.object,
      );

      logger?.warn('Payment intent failed', {
        operation: 'webhookHandler',
        paymentId: payment.id,
        paymentIntentId: paymentIntent.id,
      });

      break;
    }

    default:
      logger?.debug('Unhandled webhook event type', {
        operation: 'webhookHandler',
        eventType: event.type,
      });
      return { status: 'ignored', reason: 'event_type_not_handled' };
  }

  return { status: 'ok' };
});
