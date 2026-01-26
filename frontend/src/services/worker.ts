/**
 * Service Worker Management
 * Handles registration and unregistration of service workers for PWA support
 */

/**
 * Check if service workers are supported in the browser
 */
const isServiceWorkerSupported = (): boolean => {
  return 'serviceWorker' in navigator;
};

/**
 * Register the service worker
 * @param swPath - Path to the service worker file (default: '/sw.js')
 * @returns Promise resolving to ServiceWorkerRegistration or null if failed
 */
export const registerServiceWorker = async (
  swPath: string = '/sw.js'
): Promise<ServiceWorkerRegistration | null> => {
  if (!isServiceWorkerSupported()) {
    console.warn('Service Workers are not supported in this browser');
    return null;
  }

  try {
    const registration = await navigator.serviceWorker.register(swPath);
    console.log('Service Worker registered successfully:', registration);
    return registration;
  } catch (error) {
    console.error('Service Worker registration failed:', error);
    return null;
  }
};

/**
 * Unregister all service workers
 * @returns Promise resolving to true if successful, false otherwise
 */
export const unregisterServiceWorker = async (): Promise<boolean> => {
  if (!isServiceWorkerSupported()) {
    return false;
  }

  try {
    const registrations = await navigator.serviceWorker.getRegistrations();
    for (const registration of registrations) {
      await registration.unregister();
    }
    console.log('All Service Workers unregistered');
    return true;
  } catch (error) {
    console.error('Error unregistering Service Workers:', error);
    return false;
  }
};

/**
 * Initialize service worker registration
 * Should be called once during app startup
 * Only registers in production environment
 */
export const initializeServiceWorker = (): void => {
  if (process.env.NODE_ENV !== 'production') {
    return;
  }

  if (!isServiceWorkerSupported()) {
    return;
  }

  // Register on load event to ensure DOM is ready
  if (document.readyState === 'loading') {
    window.addEventListener('load', () => {
      registerServiceWorker();
    });
  } else {
    // DOM is already loaded
    registerServiceWorker();
  }
};

/**
 * Service worker management object
 * Provides a clean API for service worker operations
 */
export const workerService = {
  register: registerServiceWorker,
  unregister: unregisterServiceWorker,
  initialize: initializeServiceWorker,
  isSupported: isServiceWorkerSupported,
};
