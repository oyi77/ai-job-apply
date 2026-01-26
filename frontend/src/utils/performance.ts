/**
 * Performance monitoring utilities for Core Web Vitals and bundle size tracking
 */

/**
 * Initialize performance monitoring for Core Web Vitals (LCP, FID, CLS) and bundle size
 * Safely handles browser support checks and gracefully degrades if APIs unavailable
 */
export function initializePerformanceMonitoring(): void {
  // Monitor Core Web Vitals
  if ('PerformanceObserver' in window) {
    try {
      // Monitor Largest Contentful Paint (LCP)
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        console.log('LCP:', lastEntry.startTime);
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

      // Monitor First Input Delay (FID)
      const fidObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry: any) => {
          if (entry.processingStart && entry.startTime) {
            console.log('FID:', entry.processingStart - entry.startTime);
          }
        });
      });
      fidObserver.observe({ entryTypes: ['first-input'] });

      // Monitor Cumulative Layout Shift (CLS)
      const clsObserver = new PerformanceObserver((list) => {
        let clsValue = 0;
        const entries = list.getEntries();
        entries.forEach((entry: any) => {
          if (!entry.hadRecentInput) {
            clsValue += entry.value;
          }
        });
        console.log('CLS:', clsValue);
      });
      clsObserver.observe({ entryTypes: ['layout-shift'] });
    } catch (error) {
      console.warn('Performance monitoring not supported:', error);
    }
  }

  // Monitor bundle size
  if (process.env.NODE_ENV === 'production') {
    const scriptTags = document.querySelectorAll('script[src]');
    let totalSize = 0;
    scriptTags.forEach((script) => {
      const src = script.getAttribute('src');
      if (src && src.includes('assets/')) {
        // Estimate size based on filename pattern
        totalSize += 100; // Rough estimate
      }
    });
    console.log('Estimated bundle size:', totalSize, 'KB');
  }
}
