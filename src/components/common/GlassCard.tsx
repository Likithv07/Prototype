import React, { ReactNode } from 'react';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  glow?: boolean;
  interactive?: boolean;
  onClick?: () => void;
  id?: string;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className = '',
  glow = false,
  interactive = false,
  onClick,
  id,
}) => {
  return (
    <div
      id={id}
      onClick={onClick}
      className={`
        rounded-2xl
        transition-all duration-300
        ${glow ? 'glass-panel-glow' : 'glass-panel'}
        ${interactive ? 'glass-card-interactive cursor-pointer' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  );
};
