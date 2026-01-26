/**
 * Skeleton loading component
 * Displays a shimmering placeholder while content loads
 */

import React from 'react';

export interface SkeletonProps {
  /** Width of the skeleton */
  width?: string | number;
  /** Height of the skeleton */
  height?: string | number;
  /** Border radius */
  radius?: string | number;
  /** Additional CSS classes */
  className?: string;
  /** Number of lines for text skeleton */
  lines?: number;
  /** Whether to show animation */
  animated?: boolean;
}

const Skeleton: React.FC<SkeletonProps> = ({
  width = '100%',
  height = '1rem',
  radius = '0.25rem',
  className = '',
  lines = 1,
  animated = true,
}) => {
  const baseStyles: React.CSSProperties = {
    width,
    height: lines > 1 ? 'auto' : height,
    borderRadius: radius,
    backgroundColor: '#e5e7eb',
    display: 'block',
  };

  if (lines > 1) {
    return (
      <div className={className}>
        {Array.from({ length: lines }).map((_, index) => (
          <div
            key={index}
            style={{
              ...baseStyles,
              height: index === lines - 1 ? height : '1rem',
              width: index === lines - 1 ? '60%' : '100%',
              marginBottom: index === lines - 1 ? 0 : '0.5rem',
              animation: animated ? 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' : undefined,
            }}
          />
        ))}
        <style>{`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div
      className={className}
      style={{
        ...baseStyles,
        animation: animated ? 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' : undefined,
      }}
    >
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

export default Skeleton;
