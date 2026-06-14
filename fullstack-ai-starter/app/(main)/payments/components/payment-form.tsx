'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';

export function PaymentForm() {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    amount: '',
    currency: 'EUR',
    description: '',
    orderId: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload: Record<string, unknown> = {
        amount: formData.amount,
        currency: formData.currency,
        description: formData.description,
      };

      // Add metadata if orderId is provided
      if (formData.orderId) {
        payload.metadata = { orderId: formData.orderId };
      }

      const response = await fetch('/api/payments/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || 'Failed to create payment');
      }

      const payment = result.data?.payment || result.payment;

      // Redirect to Stripe Checkout
      if (payment.stripeCheckoutUrl) {
        window.location.href = payment.stripeCheckoutUrl;
      } else {
        throw new Error('No checkout URL received');
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to create payment');
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="amount">Amount</Label>
        <Input
          id="amount"
          type="text"
          placeholder="10.00"
          pattern="^\d+\.\d{2}$"
          required
          value={formData.amount}
          onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
        />
        <p className="text-sm text-muted-foreground mt-1">Format: 10.00</p>
      </div>

      <div>
        <Label htmlFor="currency">Currency</Label>
        <Select
          value={formData.currency}
          onValueChange={(value) => setFormData({ ...formData, currency: value })}
        >
          <SelectTrigger id="currency">
            <SelectValue placeholder="Select currency" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="EUR">EUR (€)</SelectItem>
            <SelectItem value="USD">USD ($)</SelectItem>
            <SelectItem value="GBP">GBP (£)</SelectItem>
            <SelectItem value="CHF">CHF</SelectItem>
            <SelectItem value="PLN">PLN</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div>
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          placeholder="Payment for..."
          required
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
        />
      </div>

      <div>
        <Label htmlFor="orderId">Order ID (Optional)</Label>
        <Input
          id="orderId"
          type="text"
          placeholder="order_123"
          value={formData.orderId}
          onChange={(e) => setFormData({ ...formData, orderId: e.target.value })}
        />
      </div>

      <Button type="submit" disabled={loading} className="w-full">
        {loading ? 'Creating payment...' : 'Pay with Stripe'}
      </Button>
    </form>
  );
}
