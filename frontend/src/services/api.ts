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
  timeout: 10000, // Default timeout for regular requests
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

  // Delete account
  deleteAccount: async (): Promise<void> => {
    await apiClient.delete('/api/v1/auth/me');
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

  // Delete account
  deleteAccount: async (password: string): Promise<void> => {
    await apiClient.delete('/api/v1/auth/account', {
      data: { password },
    });
    // Clear tokens after successful deletion
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
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

  // Bulk update applications
  bulkUpdate: async (ids: string[], updates: Partial<JobApplication>): Promise<JobApplication[]> => {
    const response = await apiClient.put('/api/v1/applications/bulk', { ids, updates });
    return handleApiResponse(response);
  },

  // Bulk delete applications
  bulkDelete: async (ids: string[]): Promise<boolean> => {
    const response = await apiClient.delete('/api/v1/applications/bulk', { data: { ids } });
    return handleApiResponse(response);
  },

  // Export applications
  exportApplications: async (ids?: string[], format = 'csv'): Promise<Blob> => {
    const response = await apiClient.post('/api/v1/applications/export', { ids, format }, {
      responseType: 'blob'
    });
    return response.data;
  },
};

// Export Services
export const exportService = {
  // Export applications
  exportApplications: async (ids?: string[], format: 'pdf' | 'csv' | 'excel' = 'csv', dateFrom?: string, dateTo?: string): Promise<Blob> => {
    const response = await apiClient.post('/api/v1/exports/applications', {
      format,
      application_ids: ids,
      date_from: dateFrom,
      date_to: dateTo,
    }, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Export resumes
  exportResumes: async (format: 'pdf' | 'csv' | 'excel' = 'csv'): Promise<Blob> => {
    const response = await apiClient.post(`/api/v1/exports/resumes?format=${format}`, {}, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Export cover letters
  exportCoverLetters: async (format: 'pdf' | 'csv' | 'excel' = 'pdf'): Promise<Blob> => {
    const response = await apiClient.post(`/api/v1/exports/cover-letters?format=${format}`, {}, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Export analytics
  exportAnalytics: async (format: 'pdf' | 'csv' | 'excel' = 'pdf', includeCharts = true): Promise<Blob> => {
    const response = await apiClient.post('/api/v1/exports/analytics', {
      format,
      include_charts: includeCharts,
    }, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Get supported formats
  getSupportedFormats: async (): Promise<string[]> => {
    const response = await apiClient.get('/api/v1/exports/formats');
    return response.data.data?.formats || ['csv', 'excel', 'pdf'];
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
      timeout: 60000, // 60 seconds for file uploads
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

  // Bulk delete resumes
  bulkDelete: async (ids: string[]): Promise<boolean> => {
    const response = await apiClient.delete('/api/v1/resumes/bulk', { data: { ids } });
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

  // Bulk delete cover letters
  bulkDelete: async (ids: string[]): Promise<boolean> => {
    const response = await apiClient.delete('/api/v1/cover-letters/bulk', { data: { ids } });
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

  // Prepare interview
  prepareInterview: async (jobDescription: string, resumeContent: string, company: string, jobTitle: string): Promise<any> => {
    const response = await apiClient.post('/api/v1/ai/interview-prep', {
      job_description: jobDescription,
      resume_content: resumeContent,
      company_name: company,
      job_title: jobTitle
    });
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
      timeout: 60000, // 60 seconds for file uploads
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

// Analytics Services
export interface SuccessRateMetrics {
  success_rate: number;
  interview_rate: number;
  rejection_rate: number;
  total_applications: number;
  status_breakdown: Record<string, number>;
}

export interface ResponseTimeMetrics {
  average_response_time: number;
  fastest_response: number;
  slowest_response: number;
  response_time_distribution: Record<string, number>;
}

export interface InterviewPerformanceMetrics {
  total_interviews: number;
  interview_to_offer_rate: number;
  average_rounds: number;
  performance_by_round: Record<string, number>;
}

export interface TrendData {
  weekly_trends: Array<{
    week: string;
    applications: number;
    interviews: number;
    offers: number;
  }>;
  application_patterns: Record<string, number>;
}

export interface SkillsGapAnalysis {
  most_requested_skills: Array<{
    skill: string;
    frequency: number;
    trend: string;
  }>;
  skill_frequency: Record<string, number>;
  ai_recommendations?: string[];
  ai_powered: boolean;
}

export interface CompanyAnalysis {
  companies: Array<{
    company: string;
    total_applications: number;
    success_rate: number;
    average_response_time: number;
  }>;
}

export interface AnalyticsDashboard {
  success_metrics: SuccessRateMetrics;
  response_time_metrics: ResponseTimeMetrics;
  interview_metrics: InterviewPerformanceMetrics;
  trends: TrendData;
  skills_gap: SkillsGapAnalysis;
  companies: CompanyAnalysis;
  ai_powered?: boolean;
}

// Notification Services
export interface EmailTemplate {
  id: string;
  name: string;
  description: string;
}

export interface NotificationSettings {
  email_enabled: boolean;
  follow_up_reminders: boolean;
  interview_reminders: boolean;
  application_status_updates: boolean;
  marketing_emails: boolean;
}

export interface SendEmailRequest {
  to_email: string;
  template_name: string;
  template_data: Record<string, any>;
  attachments?: Array<{
    filename: string;
    content: string;
    mime_type: string;
  }>;
  tags?: string[];
}

export const notificationService = {
  // Get notification settings
  getSettings: async (): Promise<NotificationSettings> => {
    const response = await apiClient.get('/api/v1/notifications/settings');
    return response.data.data || response.data;
  },

  // Update notification settings
  updateSettings: async (settings: NotificationSettings): Promise<NotificationSettings> => {
    const response = await apiClient.post('/api/v1/notifications/settings', settings);
    return response.data.data || response.data;
  },

  // Get available email templates
  getTemplates: async (): Promise<EmailTemplate[]> => {
    const response = await apiClient.get('/api/v1/notifications/email/templates');
    return response.data.data?.templates || [];
  },

  // Send test email
  sendTestEmail: async (toEmail: string, templateName?: string): Promise<{ test_sent_to: string }> => {
    const response = await apiClient.post('/api/v1/notifications/email/test', {
      to_email: toEmail,
      template_name: templateName,
    });
    return response.data.data || response.data;
  },

  // Send email notification
  sendEmail: async (request: SendEmailRequest): Promise<{ message_id: string }> => {
    const response = await apiClient.post('/api/v1/notifications/email', request);
    return response.data.data || response.data;
  },
};

// Analytics Services
export const analyticsService = {
  // Get comprehensive analytics dashboard
  getDashboard: async (days = 30): Promise<AnalyticsDashboard> => {
    const response = await apiClient.get(`/api/v1/analytics/dashboard?days=${days}`);
    return response.data.data || response.data;
  },

  // Get success rate metrics
  getSuccessRate: async (startDate?: string, endDate?: string): Promise<SuccessRateMetrics> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await apiClient.get(`/api/v1/analytics/metrics/success-rate?${params.toString()}`);
    return response.data.data || response.data;
  },

  // Get trend analysis
  getTrends: async (days = 30): Promise<TrendData> => {
    const response = await apiClient.get(`/api/v1/analytics/trends?days=${days}`);
    return response.data.data || response.data;
  },

  // Get skills gap analysis
  getSkillsGap: async (): Promise<SkillsGapAnalysis> => {
    const response = await apiClient.get('/api/v1/analytics/insights/skills-gap');
    return response.data.data || response.data;
  },

  // Get company analysis
  getCompanyAnalysis: async (): Promise<CompanyAnalysis> => {
    const response = await apiClient.get('/api/v1/analytics/insights/companies');
    return response.data.data || response.data;
  },

  // Get response time metrics
  getResponseTime: async (startDate?: string, endDate?: string): Promise<ResponseTimeMetrics> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await apiClient.get(`/api/v1/analytics/metrics/response-time?${params.toString()}`);
    return response.data.data || response.data;
  },

  // Get interview performance metrics
  getInterviewPerformance: async (startDate?: string, endDate?: string): Promise<InterviewPerformanceMetrics> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await apiClient.get(`/api/v1/analytics/metrics/interview-performance?${params.toString()}`);
    return response.data.data || response.data;
  },
};
