import { useEffect, useCallback, RefObject } from 'react';
import { useNavigate } from 'react-router-dom';

interface NavigationItem {
  name: string;
  href: string;
}

interface UseNavigationProps {
  items: NavigationItem[];
  onCloseMobileMenu?: () => void;
  mobileMenuOpen?: boolean;
}

export const useNavigation = ({ 
  items, 
  onCloseMobileMenu,
  mobileMenuOpen 
}: UseNavigationProps) => {
  const navigate = useNavigate();

  // Handle keyboard navigation (Alt + 1-9)
  const handleKeyboardShortcuts = useCallback((event: KeyboardEvent) => {
    // Only trigger if Alt key is pressed
    if (!event.altKey) return;

    const key = event.key;
    const index = parseInt(key) - 1;

    // Check if key is a number 1-9 and within bounds of items
    if (!isNaN(index) && index >= 0 && index < items.length) {
      event.preventDefault();
      navigate(items[index].href);
      if (onCloseMobileMenu) {
        onCloseMobileMenu();
      }
    }
  }, [items, navigate, onCloseMobileMenu]);

  // Handle Escape key to close mobile menu
  const handleEscapeKey = useCallback((event: KeyboardEvent) => {
    if (event.key === 'Escape' && mobileMenuOpen && onCloseMobileMenu) {
      event.preventDefault();
      onCloseMobileMenu();
    }
  }, [mobileMenuOpen, onCloseMobileMenu]);

  // Setup global keyboard listeners
  useEffect(() => {
    window.addEventListener('keydown', handleKeyboardShortcuts);
    window.addEventListener('keydown', handleEscapeKey);
    
    return () => {
      window.removeEventListener('keydown', handleKeyboardShortcuts);
      window.removeEventListener('keydown', handleEscapeKey);
    };
  }, [handleKeyboardShortcuts, handleEscapeKey]);

  // Trap focus within a container (for mobile menu)
  const trapFocus = (element: HTMLElement | null, event: React.KeyboardEvent | KeyboardEvent) => {
    if (!element) return;

    const focusableElements = element.querySelectorAll(
      'a[href], button:not([disabled]), textarea, input, select'
    );
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    if (event.key === 'Tab') {
      if (event.shiftKey) {
        if (document.activeElement === firstElement) {
          event.preventDefault();
          lastElement.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          event.preventDefault();
          firstElement.focus();
        }
      }
    }
  };

  // Return focus to a specific element
  const returnFocus = (ref: RefObject<HTMLElement>) => {
    if (ref.current) {
      ref.current.focus();
    }
  };

  return {
    trapFocus,
    returnFocus,
  };
};

export default useNavigation;
