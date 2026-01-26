import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './i18n'
import App from './App.tsx'
import { ErrorBoundary } from './components/ErrorBoundary'
import { useAppStore } from './stores/appStore'
import { workerService } from './services/worker'

// Initialize theme on app startup before rendering
const initializeTheme = () => {
  const root = window.document.documentElement;
  const theme = useAppStore.getState().theme;
  
  const applyTheme = (themeToApply: 'light' | 'dark') => {
    root.classList.remove('light', 'dark');
    root.classList.add(themeToApply);
  };

  if (theme === 'system') {
    const systemPreference = window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';
    applyTheme(systemPreference);
  } else {
    applyTheme(theme);
  }
};

// Apply theme immediately on module load
initializeTheme();

// Initialize service worker for caching and offline support
workerService.initialize();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
)
