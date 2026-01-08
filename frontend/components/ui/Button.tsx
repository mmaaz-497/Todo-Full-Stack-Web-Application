import { ButtonHTMLAttributes, ReactNode } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  children: ReactNode;
  isLoading?: boolean;
}

export default function Button({
  variant = 'primary',
  size = 'md',
  children,
  isLoading = false,
  disabled,
  className = '',
  ...props
}: ButtonProps) {
  const baseStyles = `
    inline-flex items-center justify-center gap-2
    font-semibold tracking-wide
    rounded-lg
    transform transition-all duration-200 ease-out
    focus:outline-none
    disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
  `;

  const variants = {
    primary: `
      bg-primary-600 hover:bg-primary-700 active:bg-primary-800
      text-white
      shadow-md hover:shadow-lg
      hover:scale-[1.02] active:scale-[0.98]
      focus:ring-4 focus:ring-primary-200
    `,
    secondary: `
      bg-transparent hover:bg-neutral-100 active:bg-neutral-200
      text-primary-600 hover:text-primary-700
      border-2 border-primary-600 hover:border-primary-700
      hover:scale-[1.02] active:scale-[0.98]
      focus:ring-4 focus:ring-primary-200
    `,
    ghost: `
      bg-transparent hover:bg-neutral-100 active:bg-neutral-200
      text-neutral-700 hover:text-neutral-900
      focus:ring-2 focus:ring-neutral-300
    `,
    danger: `
      bg-error-600 hover:bg-error-700 active:bg-error-800
      text-white
      shadow-md hover:shadow-lg
      hover:scale-[1.02] active:scale-[0.98]
      focus:ring-4 focus:ring-error-200
    `,
  };

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-2.5 text-base',
    lg: 'px-8 py-3 text-lg',
  };

  return (
    <button
      className={`
        ${baseStyles}
        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <>
          <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
          <span>Loading...</span>
        </>
      ) : (
        children
      )}
    </button>
  );
}
