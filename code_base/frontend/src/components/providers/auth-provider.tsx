'use client';

import { useAuthStore } from '@/store/auth';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect } from 'react';

const publicRoutes = ['/login', '/signup'];

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { user, token } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!token && !publicRoutes.includes(pathname)) {
      router.push('/login');
    }
  }, [token, pathname, router]);

  return <>{children}</>;
} 