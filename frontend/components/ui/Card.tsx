import { HTMLAttributes, ReactNode } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  hoverable?: boolean;
  elevated?: boolean;
}

export default function Card({
  children,
  hoverable = false,
  elevated = false,
  className = '',
  ...props
}: CardProps) {
  const baseStyles = `
    bg-white
    rounded-xl
    border border-neutral-200
    overflow-hidden
  `;

  const hoverStyles = hoverable ? `
    shadow-md hover:shadow-xl
    hover:border-neutral-300
    transform hover:-translate-y-2
    transition-all duration-300 ease-out
    cursor-pointer
  ` : 'shadow-sm';

  const elevatedStyles = elevated ? 'shadow-2xl' : '';

  return (
    <div
      className={`
        ${baseStyles}
        ${hoverStyles}
        ${elevatedStyles}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
}
