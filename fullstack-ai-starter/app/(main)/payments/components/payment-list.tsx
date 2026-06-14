'use client';

import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import type { Payment } from '@/modules/payments/types';

const statusColors: Record<string, string> = {
  paid: 'bg-green-500',
  pending: 'bg-yellow-500',
  open: 'bg-blue-500',
  failed: 'bg-red-500',
  expired: 'bg-gray-500',
  canceled: 'bg-gray-500',
};

export function PaymentList() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPayments();
  }, []);

  const fetchPayments = async () => {
    try {
      const response = await fetch('/api/payments');
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || 'Failed to fetch payments');
      }

      const data = result.data?.payments || result.payments;
      setPayments(data);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to fetch payments');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-12 w-full" />
      </div>
    );
  }

  if (payments.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No payments found. Create your first payment above.
      </div>
    );
  }

  return (
    <div className="border rounded-lg">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Description</TableHead>
            <TableHead>Amount</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Created</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {payments.map((payment) => (
            <TableRow key={payment.id}>
              <TableCell className="font-medium">{payment.description}</TableCell>
              <TableCell>
                {payment.currency} {payment.amount}
              </TableCell>
              <TableCell>
                <Badge
                  className={statusColors[payment.status] || 'bg-gray-500'}
                  variant="secondary"
                >
                  {payment.status}
                </Badge>
              </TableCell>
              <TableCell>{new Date(payment.createdAt).toLocaleDateString()}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
