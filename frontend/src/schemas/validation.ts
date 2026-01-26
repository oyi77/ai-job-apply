import { z } from 'zod';
import { ApplicationStatus } from '../types';

// Helper to get values from the ApplicationStatus constant
const statusValues = Object.values(ApplicationStatus) as [string, ...string[]];

export const applicationSchema = z.object({
  job_title: z.string().min(2, 'Job title must be at least 2 characters'),
  company: z.string().min(2, 'Company name must be at least 2 characters'),
  location: z.string().optional(),
  salary: z.string().optional(),
  job_description: z.string().optional(),
  status: z.enum(statusValues).default(ApplicationStatus.DRAFT),
  applied_date: z.string().optional(),
  follow_up_date: z.string().optional(),
  notes: z.string().optional(),
});

export const resumeSchema = z.object({
  title: z.string().min(2, 'Title must be at least 2 characters'),
  // File validation is tricky in Zod alone if it's a FileList or File object from input
  // We'll refine it to check if it's truthy and has size if it's a File
  file: z.any().refine((file) => {
    if (!file) return false;
    if (file instanceof File) return file.size > 0;
    if (file instanceof FileList) return file.length > 0;
    return true; // If it's something else (like existing file ID), we assume it's valid or handled elsewhere
  }, 'Resume file is required'),
});

export const settingsSchema = z.object({
  email_notifications: z.boolean(),
  push_notifications: z.boolean(),
  theme: z.enum(['light', 'dark', 'system']),
  language: z.string().default('en'),
});

export type ApplicationFormData = z.infer<typeof applicationSchema>;
export type ResumeFormData = z.infer<typeof resumeSchema>;
export type SettingsFormData = z.infer<typeof settingsSchema>;
