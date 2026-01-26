import { useEffect, useState, useCallback } from 'react';

/**
 * Interface for the beforeinstallprompt event
 */
interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

/**
 * Interface for PWA state
 */
interface PWAState {
  isInstallable: boolean;
  isInstalled: boolean;
  installApp: () => Promise<void>;
  deferredPrompt: BeforeInstallPromptEvent | null;
}

/**
 * Hook to manage PWA installation
 * Handles beforeinstallprompt event capture and provides install functionality
 */
export const usePWA = (): PWAState => {
  const [isInstallable, setIsInstallable] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);

  // Check if app is already installed
  useEffect(() => {
    // Check if running as PWA (standalone mode)
    const isRunningAsApp = window.matchMedia('(display-mode: standalone)').matches ||
      (window.navigator as any).standalone === true;
    setIsInstalled(isRunningAsApp);
  }, []);

  // Handle beforeinstallprompt event
  useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      // Prevent the mini-infobar from appearing on mobile
      e.preventDefault();
      
      // Store the event for later use
      const event = e as BeforeInstallPromptEvent;
      setDeferredPrompt(event);
      setIsInstallable(true);
    };

    const handleAppInstalled = () => {
      // App was installed
      setIsInstalled(true);
      setIsInstallable(false);
      setDeferredPrompt(null);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  // Function to trigger the install prompt
  const installApp = useCallback(async () => {
    if (!deferredPrompt) {
      console.warn('Install prompt is not available');
      return;
    }

    try {
      // Show the install prompt
      await deferredPrompt.prompt();

      // Wait for user choice
      const { outcome } = await deferredPrompt.userChoice;

      if (outcome === 'accepted') {
        // User accepted the install prompt
        setIsInstalled(true);
        setIsInstallable(false);
      }

      // Clear the deferred prompt
      setDeferredPrompt(null);
    } catch (error) {
      console.error('Error during PWA installation:', error);
    }
  }, [deferredPrompt]);

  return {
    isInstallable,
    isInstalled,
    installApp,
    deferredPrompt,
  };
};

/**
 * Utility function to check if PWA is supported
 */
export const isPWASupported = (): boolean => {
  return 'serviceWorker' in navigator && 'caches' in window;
};
