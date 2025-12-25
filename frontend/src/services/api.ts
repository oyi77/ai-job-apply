import axios from 'axios';
import type { AxiosInstance, AxiosResponse } from 'axios';
import type {
  JobApplication,
  Resume,
  CoverLetter,
  Job,
  ApiResponse,
  PaginatedResponse,
  AIOptimizationRequest,
  AIOptimizationResponse,
  CoverLetterRequest,
  CoverLetterResponse,
  CareerInsightsRequest,
  CareerInsightsResponse,
  ApplicationStats,
  SearchFilters,
  SortOptions
} from '../types';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});
// Token storage keys
const ACCESS_TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

// Token refresh helper
let isRefreshing = false;
let failedQueue: Array<{ resolve: (value?: any) => void; reject: (reason?: any) => void }> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Enhanced response interceptor with token refresh
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't tried to refresh yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return apiClient(originalRequest);
          })
          .catch(err => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      if (!refreshToken) {
        // No refresh token, logout
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        window.location.href = '/login';
        processQueue(error, null);
        return Promise.reject(error);
      }

      try {
        const response = await apiClient.post('/api/v1/auth/refresh', {
          refresh_token: refreshToken,
        });
        const { access_token, refresh_token: newRefreshToken } = response.data;

        localStorage.setItem(ACCESS_TOKEN_KEY, access_token);
        if (newRefreshToken) {
          localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken);
        }

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        processQueue(null, access_token);
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        window.location.href = '/login';
        processQueue(refreshError, null);
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // Enhanced error handling with user-friendly messages
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data;

      switch (status) {
        case 401:
          // Handle unauthorized access (after refresh attempt failed)
          localStorage.removeItem(ACCESS_TOKEN_KEY);
          localStorage.removeItem(REFRESH_TOKEN_KEY);
          window.location.href = '/login';
          break;
        case 403:
          console.error('Access forbidden:', data?.detail || 'You do not have permission to access this resource');
          break;
        case 404:
          console.error('Resource not found:', data?.detail || 'The requested resource was not found');
          break;
        case 422:
          console.error('Validation error:', data?.detail || 'Invalid request data');
          break;
        case 500:
          console.error('Server error:', data?.detail || 'An internal server error occurred');
          break;
        default:
          console.error('API error:', data?.detail || error.message || 'An error occurred');
      }
    } else if (error.request) {
      console.error('Network error: No response received from server. Please check your connection.');
    } else {
      console.error('Request error:', error.message || 'An unexpected error occurred');
    }

    return Promise.reject(error);
  }
);

// Update request interceptor to use correct token key
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Health Check
export const healthCheck = async (): Promise<{ status: string }> => {
  const response = await apiClient.get('/health');
  return response.data;
};

// Authentication Services
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserProfile {
  id: string;
  email: string;
  name?: string;
  created_at: string;
  updated_at: string;
}

export interface UserRegister {
  email: string;
  password: string;
  name?: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export const authService = {
  // Register new user
  register: async (data: UserRegister): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/api/v1/auth/register', data);
    const tokens = response.data;
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
    return tokens;
  },

  // Login user
  login: async (data: UserLogin): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/api/v1/auth/login', data);
    const tokens = response.data;
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
    return tokens;
  },

  // Refresh token
  refreshToken: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    });
    const tokens = response.data;
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
    return tokens;
  },

  // Logout user
  logout: async (): Promise<void> => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (refreshToken) {
      try {
        await apiClient.post('/api/v1/auth/logout', {
          refresh_token: refreshToken,
        });
      } catch (error) {
        console.error('Logout error:', error);
      }
    }
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },

  // Get current user profile
  getProfile: async (): Promise<UserProfile> => {
    const response = await apiClient.get<UserProfile>('/api/v1/auth/me');
    return response.data;
  },

  // Update user profile
  updateProfile: async (updates: Partial<UserProfile>): Promise<UserProfile> => {
    const response = await apiClient.put<UserProfile>('/api/v1/auth/me', updates);
    return response.data;
  },

  // Change password
  changePassword: async (currentPassword: string, newPassword: string): Promise<void> => {
    await apiClient.post('/api/v1/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },

  // Check if user is authenticated
  isAuthenticated: (): boolean => {
    return !!localStorage.getItem(ACCESS_TOKEN_KEY);
  },

  // Get stored access token
  getAccessToken: (): string | null => {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  },

  // Get stored refresh token
  getRefreshToken: (): string | null => {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  },
};

// Helper to handle API responses
const handleApiResponse = <T>(response: AxiosResponse<ApiResponse<T>>): T => {
  if (response.data && (response.data.success === true || response.data.data !== undefined)) {
    return (response.data.data !== undefined ? response.data.data : response.data) as T;
  }
  throw new Error(response.data?.message || 'API request failed');
};

// Application Services
export const applicationService = {
  // Get all applications
  getApplications: async (filters?: SearchFilters, sort?: SortOptions, page = 1, limit = 10): Promise<PaginatedResponse<JobApplication>> => {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status.join(','));
    if (filters?.company) params.append('company', filters.company);
    if (filters?.location) params.append('location', filters.location);
    if (filters?.date_range?.start) params.append('start_date', filters.date_range.start);
    if (filters?.date_range?.end) params.append('end_date', filters.date_range.end);
    if (filters?.skills) params.append('skills', filters.skills.join(','));
    if (sort?.field) params.append('sort_by', sort.field);
    if (sort?.direction) params.append('sort_direction', sort.direction);
    params.append('page', page.toString());
    params.append('limit', limit.toString());

    const response = await apiClient.get(`/api/v1/applications?${params.toString()}`);
    return response.data;
  },

  // Get application by ID
  getApplication: async (id: string): Promise<JobApplication> => {
    const response = await apiClient.get(`/api/v1/applications/${id}`);
    return handleApiResponse(response);
  },

  // Create new application
  createApplication: async (application: Omit<JobApplication, 'id' | 'created_at' | 'updated_at'>): Promise<JobApplication> => {
    const response = await apiClient.post('/api/v1/applications/', application);
    return handleApiResponse(response);
  },

  // Update application
  updateApplication: async (id: string, application: Partial<JobApplication>): Promise<JobApplication> => {
    const response = await apiClient.put(`/api/v1/applications/${id}`, application);
    return handleApiResponse(response);
  },

  // Delete application
  deleteApplication: async (id: string): Promise<boolean> => {
    const response = await apiClient.delete(`/api/v1/applications/${id}`);
    return handleApiResponse(response);
  },

  // Get application statistics
  getStats: async (): Promise<ApplicationStats> => {
    const response = await apiClient.get('/api/v1/applications/stats');
    return handleApiResponse(response);
  },
};

// Resume Services
export const resumeService = {
  // Get all resumes
  getResumes: async (): Promise<Resume[]> => {
    const response = await apiClient.get('/api/v1/resumes');
    return handleApiResponse(response);
  },

  // Get resume by ID
  getResume: async (id: string): Promise<Resume> => {
    const response = await apiClient.get(`/api/v1/resumes/${id}`);
    return handleApiResponse(response);
  },

  // Upload resume
  uploadResume: async (file: File, metadata?: Partial<Resume>): Promise<Resume> => {
    const formData = new FormData();
    formData.append('file', file);
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    }

    const response = await apiClient.post('/api/v1/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return handleApiResponse(response);
  },

  // Update resume
  updateResume: async (id: string, updates: Partial<Resume>): Promise<Resume> => {
    const response = await apiClient.put(`/api/v1/resumes/${id}`, updates);
    return handleApiResponse(response);
  },

  // Delete resume
  deleteResume: async (id: string): Promise<boolean> => {
    const response = await apiClient.delete(`/api/v1/resumes/${id}`);
    return handleApiResponse(response);
  },

  // Set default resume
  setDefaultResume: async (id: string): Promise<Resume> => {
    const response = await apiClient.patch(`/api/v1/resumes/${id}/default`);
    return handleApiResponse(response);
  },
};

// Cover Letter Services
export const coverLetterService = {
  // Get all cover letters
  getCoverLetters: async (): Promise<CoverLetter[]> => {
    const response = await apiClient.get('/api/v1/cover-letters');
    return handleApiResponse(response);
  },

  // Get cover letter by ID
  getCoverLetter: async (id: string): Promise<CoverLetter> => {
    const response = await apiClient.get(`/api/v1/cover-letters/${id}`);
    return handleApiResponse(response);
  },

  // Create cover letter
  createCoverLetter: async (coverLetter: Omit<CoverLetter, 'id' | 'created_at' | 'updated_at' | 'generated_at'>): Promise<CoverLetter> => {
    // Calculate word count from content
    const wordCount = coverLetter.content.trim().split(/\s+/).length;

    // Prepare the request with correct field names
    const requestBody = {
      job_title: coverLetter.job_title,
      company: coverLetter.company,
      content: coverLetter.content,
      tone: coverLetter.tone || 'professional',
      word_count: wordCount,
      file_path: coverLetter.file_path
    };

    const response = await apiClient.post('/api/v1/cover-letters/', requestBody);
    return handleApiResponse(response);
  },

  // Update cover letter
  updateCoverLetter: async (id: string, updates: Partial<CoverLetter>): Promise<CoverLetter> => {
    const response = await apiClient.put(`/api/v1/cover-letters/${id}`, updates);
    return handleApiResponse(response);
  },

  // Delete cover letter
  deleteCoverLetter: async (id: string): Promise<boolean> => {
    const response = await apiClient.delete(`/api/v1/cover-letters/${id}`);
    return handleApiResponse(response);
  },
};

// AI Services
export const aiService = {
  // Get AI service status
  getStatus: async (): Promise<{ status: string; available: boolean; model?: string }> => {
    const response = await apiClient.get('/api/v1/ai/health');
    return response.data;
  },

  // Optimize resume
  optimizeResume: async (request: AIOptimizationRequest): Promise<AIOptimizationResponse> => {
    const response = await apiClient.post('/api/v1/ai/optimize-resume', request);
    return handleApiResponse(response);
  },

  // Generate cover letter
  generateCoverLetter: async (request: CoverLetterRequest): Promise<CoverLetterResponse> => {
    const response = await apiClient.post('/api/v1/ai/generate-cover-letter', request);
    return handleApiResponse(response);
  },

  // Analyze job match
  analyzeJobMatch: async (resumeId: string, jobDescription: string): Promise<{ match_score: number; suggestions: string[] }> => {
    const response = await apiClient.post('/api/v1/ai/analyze-match', {
      resume_id: resumeId,
      job_description: jobDescription,
    });
    return handleApiResponse(response);
  },

  // Extract skills
  extractSkills: async (text: string): Promise<{ skills: string[]; confidence: number }> => {
    const response = await apiClient.post('/api/v1/ai/extract-skills', { text });
    return handleApiResponse(response);
  },

  // Generate career insights
  generateCareerInsights: async (request: CareerInsightsRequest): Promise<CareerInsightsResponse> => {
    const response = await apiClient.post('/api/v1/ai/career-insights', request);
    return handleApiResponse(response);
  },
};

// Job Search Services
export const jobSearchService = {
  // Search jobs
  searchJobs: async (params: {
    query: string;
    location?: string;
    job_type?: string;
    experience_level?: string;
    sort_by?: string;
    sort_order?: string;
  }): Promise<{ data: Job[] }> => {
    // Convert to backend expected format
    const requestBody = {
      keywords: [params.query], // Backend expects keywords array
      location: params.location || "Remote",
      experience_level: params.experience_level || "entry",
      job_type: params.job_type,
      is_remote: params.location?.toLowerCase().includes('remote') || false,
      sort_by: params.sort_by || "relevance",
      sort_order: params.sort_order || "desc"
    };

    const response = await apiClient.post('/api/v1/jobs/search', requestBody);

    // Backend returns jobs grouped by portal, convert to flat array
    const allJobs: Job[] = [];
    if (response.data.jobs) {
      Object.values(response.data.jobs).forEach(portalJobs => {
        // Add jobs from each portal
        if (portalJobs && Array.isArray(portalJobs)) {
          allJobs.push(...portalJobs);
        }
      });
    }

    return { data: allJobs };
  },

  // Get job by ID
  getJob: async (id: string): Promise<Job> => {
    const response = await apiClient.get(`/api/v1/jobs/${id}`);
    return handleApiResponse(response);
  },

  // Get available job sources
  getJobSources: async (): Promise<{ name: string; available: boolean }[]> => {
    const response = await apiClient.get('/api/v1/jobs/sources');
    return handleApiResponse(response);
  },

  // Get job details
  getJobDetails: async (jobId: string, platform?: string): Promise<Job> => {
    const params = new URLSearchParams();
    if (platform) params.append('platform', platform);

    const response = await apiClient.get(`/api/v1/jobs/${jobId}/details?${params.toString()}`);
    return handleApiResponse(response);
  },
};

// File Services
export const fileService = {
  // Upload file
  uploadFile: async (file: File, category: string): Promise<{ id: string; filename: string; url: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);

    const response = await apiClient.post('/api/v1/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return handleApiResponse(response);
  },

  // Download file
  downloadFile: async (id: string): Promise<Blob> => {
    const response = await apiClient.get(`/api/v1/files/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Delete file
  deleteFile: async (id: string): Promise<boolean> => {
    const response = await apiClient.delete(`/api/v1/files/${id}`);
    return handleApiResponse(response);
  },
};

// Export all services
export default {
  healthCheck,
  authService,
  applicationService,
  resumeService,
  coverLetterService,
  aiService,
  jobSearchService,
  fileService,
};
