/**
 * Test data fixtures for E2E tests
 */

export interface TestUser {
  email: string;
  password: string;
  name?: string;
}

export interface TestApplication {
  jobTitle: string;
  company: string;
  location?: string;
  status?: string;
  notes?: string;
}

export interface TestResume {
  fileName: string;
  content: string;
  skills?: string[];
}

export interface TestJob {
  title: string;
  company: string;
  location: string;
  portal: string;
}

// Test users
export const testUsers: Record<string, TestUser> = {
  valid: {
    email: 'test@example.com',
    password: 'Test123!@#',
    name: 'Test User',
  },
  invalid: {
    email: 'invalid@example.com',
    password: 'wrongpassword',
  },
  new: {
    email: 'newuser@example.com',
    password: 'NewUser123!@#',
    name: 'New User',
  },
};

// Test applications
export const testApplications: TestApplication[] = [
  {
    jobTitle: 'Senior Software Engineer',
    company: 'Tech Corp',
    location: 'San Francisco, CA',
    status: 'applied',
    notes: 'Applied through company website',
  },
  {
    jobTitle: 'Full Stack Developer',
    company: 'Startup Inc',
    location: 'Remote',
    status: 'interview',
    notes: 'Phone interview scheduled',
  },
  {
    jobTitle: 'Frontend Developer',
    company: 'Web Agency',
    location: 'New York, NY',
    status: 'offer',
    notes: 'Received offer, negotiating',
  },
];

// Test resume content
export const testResumes: TestResume[] = [
  {
    fileName: 'test-resume.pdf',
    content: `John Doe
Software Engineer
Email: john.doe@example.com
Phone: (555) 123-4567

EXPERIENCE
Senior Software Engineer | Tech Corp | 2020-Present
- Developed and maintained web applications
- Led team of 5 developers
- Implemented CI/CD pipelines

EDUCATION
BS Computer Science | University | 2016-2020

SKILLS
JavaScript, TypeScript, React, Node.js, Python`,
    skills: ['JavaScript', 'TypeScript', 'React', 'Node.js', 'Python'],
  },
];

// Test jobs
export const testJobs: TestJob[] = [
  {
    title: 'Senior Software Engineer',
    company: 'Tech Corp',
    location: 'San Francisco, CA',
    portal: 'LinkedIn',
  },
  {
    title: 'Full Stack Developer',
    company: 'Startup Inc',
    location: 'Remote',
    portal: 'Indeed',
  },
  {
    title: 'Frontend Developer',
    company: 'Web Agency',
    location: 'New York, NY',
    portal: 'Glassdoor',
  },
];

// Test AI prompts
export const testAIPrompts = {
  resumeOptimization: {
    resume: testResumes[0],
    jobDescription: 'Looking for a Senior Software Engineer with React and TypeScript experience.',
  },
  coverLetter: {
    jobTitle: 'Senior Software Engineer',
    company: 'Tech Corp',
    resume: testResumes[0],
  },
};
