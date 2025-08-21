import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Suspense, lazy, useEffect } from 'react';
import Layout from './components/layout/Layout';
import Spinner from './components/ui/Spinner';

// Lazy load all page components for code splitting
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Applications = lazy(() => import('./pages/Applications'));
const Resumes = lazy(() => import('./pages/Resumes'));
const CoverLetters = lazy(() => import('./pages/CoverLetters'));
const JobSearch = lazy(() => import('./pages/JobSearch'));
const AIServices = lazy(() => import('./pages/AIServices'));
const Analytics = lazy(() => import('./pages/Analytics'));
const Settings = lazy(() => import('./pages/Settings'));
const Login = lazy(() => import('./pages/Login'));
const NotFound = lazy(() => import('./pages/NotFound'));

// Loading component for Suspense fallback
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="text-center">
      <Spinner size="lg" />
      <p className="mt-4 text-gray-600">Loading page...</p>
    </div>
  </div>
);

// Create a client with performance optimizations
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
      retry: 3,
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
      refetchOnMount: false,
    },
    mutations: {
      retry: 1,
      retryDelay: 1000,
    },
  },
});

function App() {
  // Performance monitoring
  useEffect(() => {
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
          entries.forEach((entry: PerformanceEntry) => {
            if ('processingStart' in entry && 'startTime' in entry) {
              const firstInputEntry = entry as PerformanceEventTiming;
              console.log('FID:', firstInputEntry.processingStart - firstInputEntry.startTime);
            }
          });
        });
        fidObserver.observe({ entryTypes: ['first-input'] });

        // Monitor Cumulative Layout Shift (CLS)
        const clsObserver = new PerformanceObserver((list) => {
          let clsValue = 0;
          const entries = list.getEntries();
          entries.forEach((entry: PerformanceEntry) => {
            if ('hadRecentInput' in entry && 'value' in entry) {
              const layoutShiftEntry = entry as any;
              if (!layoutShiftEntry.hadRecentInput) {
                clsValue += layoutShiftEntry.value;
              }
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
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={
              <Suspense fallback={<PageLoader />}>
                <Login />
              </Suspense>
            } />
            
            {/* Protected routes */}
            <Route path="/" element={<Layout />}>
              <Route index element={
                <Suspense fallback={<PageLoader />}>
                  <Dashboard />
                </Suspense>
              } />
              <Route path="applications" element={
                <Suspense fallback={<PageLoader />}>
                  <Applications />
                </Suspense>
              } />
              <Route path="resumes" element={
                <Suspense fallback={<PageLoader />}>
                  <Resumes />
                </Suspense>
              } />
              <Route path="cover-letters" element={
                <Suspense fallback={<PageLoader />}>
                  <CoverLetters />
                </Suspense>
              } />
              <Route path="job-search" element={
                <Suspense fallback={<PageLoader />}>
                  <JobSearch />
                </Suspense>
              } />
              <Route path="ai-services" element={
                <Suspense fallback={<PageLoader />}>
                  <AIServices />
                </Suspense>
              } />
              <Route path="analytics" element={
                <Suspense fallback={<PageLoader />}>
                  <Analytics />
                </Suspense>
              } />
              <Route path="settings" element={
                <Suspense fallback={<PageLoader />}>
                  <Settings />
                </Suspense>
              } />
            </Route>
            
            {/* 404 route */}
            <Route path="*" element={
              <Suspense fallback={<PageLoader />}>
                <NotFound />
              </Suspense>
            } />
          </Routes>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
