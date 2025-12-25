// Application Types
export interface JobApplication {
  id: string;
  job_id: string;
  job_title: string;
  company: string;
  location: string;
  status: ApplicationStatus;
  applied_date: string;
  resume_id?: string;
  cover_letter_id?: string;
  notes?: string;
  follow_up_date?: string;
  interview_date?: string;
  offer_amount?: number;
  created_at: string;
  updated_at: string;
}

export const ApplicationStatus = {
  DRAFT: 'draft',
  APPLIED: 'applied',
  UNDER_REVIEW: 'under_review',
  INTERVIEW_SCHEDULED: 'interview_scheduled',
  INTERVIEW_COMPLETED: 'interview_completed',
  OFFER_RECEIVED: 'offer_received',
  OFFER_ACCEPTED: 'offer_accepted',
  OFFER_DECLINED: 'offer_declined',
  REJECTED: 'rejected',
  WITHDRAWN: 'withdrawn',
} as const;

export type ApplicationStatus = typeof ApplicationStatus[keyof typeof ApplicationStatus];

// Resume Types
export interface Resume {
  id: string;
  title?: string;
  filename: string;
  original_filename: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  file_type?: string;
  content?: string;
  skills: string[];
  experience_years: number;
  education: Education[];
  certifications: Certification[];
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface Education {
  degree: string;
  institution: string;
  year: number;
  gpa?: number;
}

export interface Certification {
  name: string;
  issuer: string;
  year: number;
  expiry_date?: string;
}

// Cover Letter Types
export interface CoverLetter {
  id?: string;
  job_title: string;
  company: string;
  content: string;
  file_path?: string;
  tone: string;
  word_count: number;
  status?: 'draft' | 'final' | 'sent';
  generated_at?: string;
  created_at?: string;
  updated_at?: string;
}

// Job Types
export interface Job {
  id?: string;
  title: string;
  company: string;
  location: string;
  url: string;
  portal: string;
  description?: string;
  salary?: string;
  posted_date?: string;
  experience_level?: ExperienceLevel;
  job_type?: JobType;
  requirements?: string[];
  benefits?: string[];
  skills?: string[];
  created_at?: string;
  updated_at?: string;
}

export const JobType = {
  FULL_TIME: 'full_time',
  PART_TIME: 'part_time',
  CONTRACT: 'contract',
  INTERNSHIP: 'internship',
  FREELANCE: 'freelance',
} as const;

export type JobType = typeof JobType[keyof typeof JobType];

export const ExperienceLevel = {
  ENTRY: 'entry',
  JUNIOR: 'junior',
  MID: 'mid',
  SENIOR: 'senior',
  LEAD: 'lead',
  EXECUTIVE: 'executive',
} as const;

export type ExperienceLevel = typeof ExperienceLevel[keyof typeof ExperienceLevel];

export const JobSource = {
  LINKEDIN: 'linkedin',
  INDEED: 'indeed',
  GLASSDOOR: 'glassdoor',
  GOOGLE_JOBS: 'google_jobs',
  COMPANY_WEBSITE: 'company_website',
  REFERRAL: 'referral',
} as const;

export type JobSource = typeof JobSource[keyof typeof JobSource];

// AI Service Types
export interface AIOptimizationRequest {
  resume_id: string;
  job_description: string;
  optimization_type: 'skills' | 'experience' | 'format' | 'all';
}

export interface AIOptimizationResponse {
  optimized_content: string;
  suggestions: string[];
  skills_gap: string[];
  confidence_score: number;
}

export interface CoverLetterRequest {
  job_title: string;
  company: string;
  job_description: string;
  resume_id: string;
  tone: 'professional' | 'friendly' | 'enthusiastic' | 'formal';
}

export interface CoverLetterResponse {
  cover_letter: string;
  suggestions: string[];
  confidence_score: number;
}

// User Types
export interface User {
  id: string;
  email: string;
  name: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  location?: string;
  bio?: string;
  avatar?: string;
  preferences: UserPreferences;
  created_at: string;
  updated_at: string;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  notifications: NotificationPreferences;
  privacy: PrivacySettings;
  ai: AISettings;
}

export interface AISettings {
  openai_api_key?: string;
  openai_model?: string;
  openai_base_url?: string;
  openrouter_api_key?: string;
  openrouter_model?: string;
  openrouter_base_url?: string;
  local_base_url?: string;
  local_model?: string;
  provider_preference: 'openai' | 'openrouter' | 'local_ai';
}

export interface NotificationPreferences {
  email: boolean;
  push: boolean;
  follow_up_reminders: boolean;
  interview_reminders: boolean;
  application_updates: boolean;
}

export interface PrivacySettings {
  profile_visibility: 'public' | 'private' | 'connections';
  data_sharing: boolean;
  analytics_tracking: boolean;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
  };
}

// Form Types
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'textarea' | 'select' | 'checkbox' | 'date' | 'file';
  required: boolean;
  placeholder?: string;
  options?: { value: string; label: string }[];
  validation?: ValidationRule[];
}

export interface ValidationRule {
  type: 'required' | 'min' | 'max' | 'pattern' | 'custom';
  value?: any;
  message: string;
}

// UI Component Types
export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'success' | 'warning' | 'info' | 'default';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
  icon?: React.ReactNode;
}

export interface InputProps {
  name: string;
  label?: string;
  type?: 'text' | 'email' | 'password' | 'textarea' | 'number';
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  error?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  success?: boolean;
  icon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  as?: 'input' | 'textarea';
  rows?: number;
  helpText?: string;
  ref?: React.Ref<HTMLInputElement | HTMLTextAreaElement>;
}

// Navigation Types
export interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  current?: boolean;
  badge?: string | number;
}

// Statistics Types
export interface ApplicationStats {
  total_applications: number;
  applications_by_status: Record<ApplicationStatus, number>;
  success_rate: number;
  average_response_time: number;
  top_companies: Array<{ company: string; count: number }>;
  monthly_trends: Array<{ month: string; count: number }>;
}

// File Types
export interface FileMetadata {
  id: string;
  filename: string;
  original_filename: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  uploaded_at: string;
  file_hash: string;
}

// Error Types
export interface AppError {
  code: string;
  message: string;
  details?: any;
  timestamp: string;
}

// Loading States
export interface LoadingState {
  isLoading: boolean;
  error?: AppError;
}

// React Query Types
export interface MutationResult<TData, TError, TVariables> {
  data?: TData;
  error: TError | null;
  isLoading: boolean;
  isSuccess: boolean;
  isError: boolean;
  mutate: (variables: TVariables) => void;
  mutateAsync: (variables: TVariables) => Promise<TData>;
  reset: () => void;
}

// Search and Filter Types
export interface SearchFilters {
  status?: ApplicationStatus[];
  company?: string;
  location?: string;
  date_range?: {
    start: string;
    end: string;
  };
  skills?: string[];
}

export interface SortOptions {
  field: keyof JobApplication;
  direction: 'asc' | 'desc';
}
