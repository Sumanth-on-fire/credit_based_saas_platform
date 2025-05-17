import { VariantProps } from 'class-variance-authority';
import { buttonVariants } from '@/components/ui/button';

export type ButtonVariant = NonNullable<VariantProps<typeof buttonVariants>['variant']>;
export type ButtonSize = NonNullable<VariantProps<typeof buttonVariants>['size']>; 