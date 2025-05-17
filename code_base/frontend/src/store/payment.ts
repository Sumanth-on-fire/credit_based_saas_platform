import { create } from 'zustand';
import api from '@/lib/api';

interface PaymentState {
  loading: boolean;
  error: string | null;
  createPayment: (amount: number) => Promise<void>;
}

export const usePaymentStore = create<PaymentState>((set) => ({
  loading: false,
  error: null,

  createPayment: async (amount: number) => {
    set({ loading: true, error: null });
    try {
      // Create payment order on backend
      const response = await api.post('/payments/create', { amount });

      // Initialize Razorpay
      const options = {
        key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID,
        amount: response.data.amount,
        currency: 'INR',
        name: 'Credit-Based Image Processing',
        description: 'Purchase Credits',
        order_id: response.data.order_id,
        handler: async (response: any) => {
          try {
            // Verify payment on backend
            await api.post('/payments/verify', {
              order_id: response.data.order_id,
              payment_id: response.razorpay_payment_id,
              signature: response.razorpay_signature,
            });
          } catch (error) {
            set({ error: 'Payment verification failed' });
          }
        },
        prefill: {
          name: 'User Name',
          email: 'user@example.com',
        },
        theme: {
          color: '#6366f1',
        },
      };

      const razorpay = new (window as any).Razorpay(options);
      razorpay.open();
    } catch (error) {
      set({ error: 'Failed to create payment' });
    } finally {
      set({ loading: false });
    }
  },
})); 