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

// Request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Generic API response handler
const handleApiResponse = <T>(response: AxiosResponse<ApiResponse<T>>): T => {
  if (response.data.success && response.data.data) {
    return response.data.data;
  }
  throw new Error(response.data.message || 'API request failed');
};

// Health Check
export const healthCheck = async (): Promise<{ status: string }> => {
  const response = await apiClient.get('/health');
  return response.data;
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
    const response = await apiClient.post('/api/v1/applications', application);
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
  createCoverLetter: async (coverLetter: Omit<CoverLetter, 'id' | 'created_at' | 'updated_at'>): Promise<CoverLetter> => {
    const response = await apiClient.post('/api/v1/cover-letters', coverLetter);
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
    const searchParams = new URLSearchParams();
    searchParams.append('query', params.query);
    if (params.location) searchParams.append('location', params.location);
    if (params.job_type) searchParams.append('job_type', params.job_type);
    if (params.experience_level) searchParams.append('experience_level', params.experience_level);
    if (params.sort_by) searchParams.append('sort_by', params.sort_by);
    if (params.sort_order) searchParams.append('sort_order', params.sort_order);

    const response = await apiClient.get(`/api/v1/jobs/search?${searchParams.toString()}`);
    return { data: response.data };
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
  applicationService,
  resumeService,
  coverLetterService,
  aiService,
  jobSearchService,
  fileService,
};
