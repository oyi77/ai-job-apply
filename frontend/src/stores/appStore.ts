import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { 
  JobApplication, 
  Resume, 
  CoverLetter, 
  Job, 
  User, 
  SearchFilters,
  SortOptions
} from '../types';
import { ApplicationStatus } from '../types';

// Application State Interface
interface AppState {
  // User state
  user: User | null;
  isAuthenticated: boolean;
  
  // Theme state
  theme: 'light' | 'dark' | 'system';
  
  // Data state
  applications: JobApplication[];
  resumes: Resume[];
  coverLetters: CoverLetter[];
  jobs: Job[];
  
  // UI state
  sidebarOpen: boolean;
  notifications: Notification[];
  loading: boolean;
  error: string | null;
  
  // Search and filters
  searchFilters: SearchFilters;
  sortOptions: SortOptions;
  
  // Actions
  setUser: (user: User | null) => void;
  setAuthenticated: (authenticated: boolean) => void;
  logout: () => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  
  // Application actions
  setApplications: (applications: JobApplication[]) => void;
  addApplication: (application: JobApplication) => void;
  updateApplication: (id: string, updates: Partial<JobApplication>) => void;
  deleteApplication: (id: string) => void;
  
  // Resume actions
  setResumes: (resumes: Resume[]) => void;
  addResume: (resume: Resume) => void;
  updateResume: (id: string, updates: Partial<Resume>) => void;
  deleteResume: (id: string) => void;
  setDefaultResume: (id: string) => void;
  
  // Cover letter actions
  setCoverLetters: (coverLetters: CoverLetter[]) => void;
  addCoverLetter: (coverLetter: CoverLetter) => void;
  updateCoverLetter: (id: string, updates: Partial<CoverLetter>) => void;
  deleteCoverLetter: (id: string) => void;
  
  // Job actions
  setJobs: (jobs: Job[]) => void;
  addJob: (job: Job) => void;
  
  // UI actions
  setSidebarOpen: (open: boolean) => void;
  setNotifications: (notifications: Notification[]) => void;
  addNotification: (notification: Notification) => void;
  removeNotification: (id: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // Search and filter actions
  setSearchFilters: (filters: SearchFilters) => void;
  setSortOptions: (options: SortOptions) => void;
  clearFilters: () => void;
  
  // Computed values
  getApplicationById: (id: string) => JobApplication | undefined;
  getResumeById: (id: string) => Resume | undefined;
  getCoverLetterById: (id: string) => CoverLetter | undefined;
  getJobById: (id: string) => Job | undefined;
  
  // Statistics
  getApplicationStats: () => {
    total: number;
    byStatus: Record<ApplicationStatus, number>;
    successRate: number;
  };
}

// Notification interface
interface Notification {
  id: string;
  type: 'success' | 'warning' | 'error' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
}

// Initial state
const initialState = {
  user: null,
  isAuthenticated: false,
  theme: 'system' as const,
  applications: [],
  resumes: [],
  coverLetters: [],
  jobs: [],
  sidebarOpen: false,
  notifications: [],
  loading: false,
  error: null,
  searchFilters: {},
  sortOptions: { field: 'created_at' as keyof JobApplication, direction: 'desc' as const },
};

// Create store
export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,
        
        // User actions
        setUser: (user) => set({ user, isAuthenticated: !!user }),
        setAuthenticated: (authenticated) => set({ isAuthenticated: authenticated }),
        logout: () => {
          // Clear tokens
          localStorage.removeItem('auth_token');
          localStorage.removeItem('refresh_token');
          // Clear user state
          set({ user: null, isAuthenticated: false });
        },
        setTheme: (theme) => set({ theme }),
        
        // Application actions
        setApplications: (applications) => set({ applications }),
        addApplication: (application) => set((state) => ({
          applications: [...state.applications, application],
        })),
        updateApplication: (id, updates) => set((state) => ({
          applications: state.applications.map((app) =>
            app.id === id ? { ...app, ...updates } : app
          ),
        })),
        deleteApplication: (id) => set((state) => ({
          applications: state.applications.filter((app) => app.id !== id),
        })),
        
        // Resume actions
        setResumes: (resumes) => set({ resumes }),
        addResume: (resume) => set((state) => ({
          resumes: [...state.resumes, resume],
        })),
        updateResume: (id, updates) => set((state) => ({
          resumes: state.resumes.map((resume) =>
            resume.id === id ? { ...resume, ...updates } : resume
          ),
        })),
        deleteResume: (id) => set((state) => ({
          resumes: state.resumes.filter((resume) => resume.id !== id),
        })),
        setDefaultResume: (id) => set((state) => ({
          resumes: state.resumes.map((resume) => ({
            ...resume,
            is_default: resume.id === id,
          })),
        })),
        
        // Cover letter actions
        setCoverLetters: (coverLetters) => set({ coverLetters }),
        addCoverLetter: (coverLetter) => set((state) => ({
          coverLetters: [...state.coverLetters, coverLetter],
        })),
        updateCoverLetter: (id, updates) => set((state) => ({
          coverLetters: state.coverLetters.map((letter) =>
            letter.id === id ? { ...letter, ...updates } : letter
          ),
        })),
        deleteCoverLetter: (id) => set((state) => ({
          coverLetters: state.coverLetters.filter((letter) => letter.id !== id),
        })),
        
        // Job actions
        setJobs: (jobs) => set({ jobs }),
        addJob: (job) => set((state) => ({
          jobs: [...state.jobs, job],
        })),
        
        // UI actions
        setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
        setNotifications: (notifications) => set({ notifications }),
        addNotification: (notification) => set((state) => ({
          notifications: [...state.notifications, notification],
        })),
        removeNotification: (id) => set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        })),
        setLoading: (loading) => set({ loading }),
        setError: (error) => set({ error }),
        
        // Search and filter actions
        setSearchFilters: (searchFilters) => set({ searchFilters }),
        setSortOptions: (sortOptions) => set({ sortOptions }),
        clearFilters: () => set({ 
          searchFilters: {}, 
          sortOptions: { field: 'created_at', direction: 'desc' } 
        }),
        
        // Computed values
        getApplicationById: (id) => {
          const state = get();
          return state.applications.find((app) => app.id === id);
        },
        getResumeById: (id) => {
          const state = get();
          return state.resumes.find((resume) => resume.id === id);
        },
        getCoverLetterById: (id) => {
          const state = get();
          return state.coverLetters.find((letter) => letter.id === id);
        },
        getJobById: (id) => {
          const state = get();
          return state.jobs.find((job) => job.id === id);
        },
        
        // Statistics
        getApplicationStats: () => {
          const state = get();
          const total = state.applications.length;
          const byStatus = state.applications.reduce((acc, app) => {
            acc[app.status] = (acc[app.status] || 0) + 1;
            return acc;
          }, {} as Record<ApplicationStatus, number>);
          
          const successful = (byStatus[ApplicationStatus.OFFER_ACCEPTED] || 0) + 
                           (byStatus[ApplicationStatus.OFFER_RECEIVED] || 0);
          const successRate = total > 0 ? (successful / total) * 100 : 0;
          
          return {
            total,
            byStatus,
            successRate: Math.round(successRate * 100) / 100,
          };
        },
      }),
      {
        name: 'ai-job-apply-store',
        partialize: (state) => ({
          theme: state.theme,
          searchFilters: state.searchFilters,
          sortOptions: state.sortOptions,
        }),
      }
    ),
    {
      name: 'ai-job-apply-store',
    }
  )
);

// Selector hooks for better performance
export const useApplications = () => useAppStore((state) => state.applications);
export const useResumes = () => useAppStore((state) => state.resumes);
export const useCoverLetters = () => useAppStore((state) => state.coverLetters);
export const useJobs = () => useAppStore((state) => state.jobs);
export const useUser = () => useAppStore((state) => state.user);
export const useIsAuthenticated = () => useAppStore((state) => state.isAuthenticated);
export const useTheme = () => useAppStore((state) => state.theme);
export const useSidebarOpen = () => useAppStore((state) => state.sidebarOpen);
export const useNotifications = () => useAppStore((state) => state.notifications);
export const useLoading = () => useAppStore((state) => state.loading);
export const useError = () => useAppStore((state) => state.error);
export const useSearchFilters = () => useAppStore((state) => state.searchFilters);
export const useSortOptions = () => useAppStore((state) => state.sortOptions);
export const useApplicationStats = () => useAppStore((state) => state.getApplicationStats());
