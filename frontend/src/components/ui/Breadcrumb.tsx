import React from 'react';
import { ChevronRightIcon, HomeIcon } from '@heroicons/react/24/outline';

export interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: React.ComponentType<{ className?: string }>;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
  onNavigate?: (href: string) => void;
  className?: string;
}

const Breadcrumb: React.FC<BreadcrumbProps> = ({ 
  items, 
  onNavigate, 
  className = '' 
}) => {
  const handleClick = (href: string, e: React.MouseEvent) => {
    e.preventDefault();
    if (onNavigate) {
      onNavigate(href);
    }
  };

  return (
    <nav className={`flex ${className}`} aria-label="Breadcrumb">
      <ol className="flex items-center space-x-2">
        <li>
          <a
            href="#"
            onClick={(e) => handleClick('/', e)}
            className="text-gray-400 hover:text-gray-500 transition-colors"
          >
            <HomeIcon className="h-5 w-5" />
            <span className="sr-only">Home</span>
          </a>
        </li>
        
        {items.map((item, index) => (
          <li key={index} className="flex items-center">
            <ChevronRightIcon className="h-5 w-5 text-gray-400 mx-2" />
            
            {index === items.length - 1 ? (
              <span className="text-gray-900 font-medium flex items-center">
                {item.icon && <item.icon className="h-4 w-4 mr-2" />}
                {item.label}
              </span>
            ) : (
              <a
                href={item.href || '#'}
                onClick={(e) => item.href && handleClick(item.href, e)}
                className="text-gray-500 hover:text-gray-700 transition-colors flex items-center"
              >
                {item.icon && <item.icon className="h-4 w-4 mr-2" />}
                {item.label}
              </a>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
};

export default Breadcrumb;
