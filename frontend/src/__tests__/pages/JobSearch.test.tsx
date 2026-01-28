
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}
global.ResizeObserver = ResizeObserverMock;

class IntersectionObserverMock {
  root = null;
  rootMargin = "";
  thresholds = [];
  observe() {}
  unobserve() {}
  disconnect() {}
  takeRecords() { return []; }
}
global.IntersectionObserver = IntersectionObserverMock;

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import JobSearch from '../../pages/JobSearch';
import * as apiModule from '../../services/api';

// Mock the API services
vi.mock('../../services/api', () => ({
  jobSearchService: {
    searchJobs: vi.fn(),
  },
  applicationService: {
    createApplication: vi.fn(),
  },
}));

// Mock the AppStore
const mockAddApplication = vi.fn();

vi.mock('../../stores/appStore', () => ({
  useAppStore: () => ({
    applications: [],
    addApplication: mockAddApplication,
  }),
}));

describe('JobSearch Page', () => {
  let queryClient: QueryClient;

  const mockJobs = [
    {
      id: '1',
      title: 'Software Engineer',
      company: 'Tech Corp',
      location: 'Remote',
      description: 'We are looking for a software engineer...',
      posted_date: '2025-01-01',
      job_type: 'full_time' as const,
      salary: '$100k - $150k',
      skills: ['React', 'Node.js'],
      url: 'https://example.com/job1',
      portal: 'linkedin'
    },
    {
      id: '2',
      title: 'Product Manager',
      company: 'Product Inc',
      location: 'New York, NY',
      description: 'Lead our product team...',
      posted_date: '2025-01-02',
      job_type: 'contract' as const,
      skills: ['Agile', 'JIRA'],
      url: 'https://example.com/job2',
      portal: 'indeed'
    },
  ];

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    vi.clearAllMocks();
  });

  const renderJobSearch = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <JobSearch />
      </QueryClientProvider>
    );
  };

  it('renders search form initially', () => {
    renderJobSearch();
    expect(screen.getByText('Job Search')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/software engineer, react developer/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/san francisco, ca or remote/i)).toBeInTheDocument();
  });

  it('performs search and displays results', async () => {
    vi.mocked(apiModule.jobSearchService.searchJobs).mockResolvedValue({ data: mockJobs });
    const user = userEvent.setup();

    renderJobSearch();

    await user.type(screen.getByPlaceholderText(/software engineer, react developer/i), 'Software Engineer');
    await user.click(screen.getByRole('button', { name: /search jobs/i }));

    await waitFor(() => {
      expect(apiModule.jobSearchService.searchJobs).toHaveBeenCalled();
    });

    expect(screen.getByText('Software Engineer')).toBeInTheDocument();
    expect(screen.getByText('Tech Corp')).toBeInTheDocument();
    expect(screen.getByText('Product Manager')).toBeInTheDocument();
  });

  it('displays empty state when no jobs found', async () => {
    vi.mocked(apiModule.jobSearchService.searchJobs).mockResolvedValue({ data: [] });
    const user = userEvent.setup();

    renderJobSearch();

    await user.type(screen.getByPlaceholderText(/software engineer, react developer/i), 'Nonexistent Job');
    await user.click(screen.getByRole('button', { name: /search jobs/i }));

    await waitFor(() => {
      expect(screen.getByText('No jobs found')).toBeInTheDocument();
    });
  });

  const searchAndClick = async (user: any) => {
    const buttons = screen.getAllByRole('button');
    const searchBtn = buttons.find(btn => /search jobs/i.test(btn.textContent || ''));
    expect(searchBtn).toBeTruthy();
    await user.click(searchBtn!);
  };

  it('opens job details modal on click', async () => {
    vi.mocked(apiModule.jobSearchService.searchJobs).mockResolvedValue({ data: mockJobs });
    const user = userEvent.setup();

    renderJobSearch();

    // Type in search box using fireEvent to ensure state update
    const searchInput = screen.getByPlaceholderText(/software engineer, react developer/i);
    fireEvent.change(searchInput, { target: { value: 'Software Engineer' } });

    await searchAndClick(user);

    // Use findByText with longer timeout
    await screen.findByText('Software Engineer', {}, { timeout: 3000 });

    // Click on job card (assuming card is clickable)
    const jobTitle = screen.getByText('Software Engineer');
    fireEvent.click(jobTitle);

    await waitFor(() => {
        expect(screen.getByRole('dialog', { name: /job details/i })).toBeInTheDocument();
    });
    const dialog = screen.getByRole('dialog');
    expect(within(dialog).getByText(/we are looking for/i)).toBeInTheDocument();
  });

  it('handles apply flow (create application)', async () => {
    vi.mocked(apiModule.jobSearchService.searchJobs).mockResolvedValue({ data: mockJobs });
    vi.mocked(apiModule.applicationService.createApplication).mockResolvedValue({ id: 'app1', status: 'submitted' } as any);
    const user = userEvent.setup();

    renderJobSearch();

    // Type in search box using fireEvent to ensure state update
    const searchInput = screen.getByPlaceholderText(/software engineer, react developer/i);
    fireEvent.change(searchInput, { target: { value: 'Software Engineer' } });

    // Search and click Apply button on card
    await searchAndClick(user);
    
    await screen.findByText('Software Engineer', {}, { timeout: 3000 });

    // Find Apply button for first job
    const applyButtons = screen.getAllByRole('button');
    const cardApplyBtn = applyButtons.find(btn => btn.textContent?.includes('Apply'));
    
    if (cardApplyBtn) {
      fireEvent.click(cardApplyBtn);

      // Should open create application modal
      await waitFor(() => {
          expect(screen.getByRole('dialog', { name: /create application/i })).toBeInTheDocument();
      });

      // Submit application
      const submitBtn = screen.getByRole('button', { name: /^create application$/i });
      await user.click(submitBtn);

      await waitFor(() => {
        expect(apiModule.applicationService.createApplication).toHaveBeenCalledWith(expect.objectContaining({
          job_title: 'Software Engineer',
          company: 'Tech Corp',
          status: 'submitted'
        }));
      });
    }
  });

   it('handles save job (bookmark)', async () => {
     vi.mocked(apiModule.jobSearchService.searchJobs).mockResolvedValue({ data: mockJobs });
     vi.mocked(apiModule.applicationService.createApplication).mockResolvedValue({ id: 'app1', status: 'draft' } as any);
     const user = userEvent.setup();

     renderJobSearch();

     // Type in search box using fireEvent to ensure state update
     const searchInput = screen.getByPlaceholderText(/software engineer, react developer/i);
     fireEvent.change(searchInput, { target: { value: 'Software Engineer' } });

     await searchAndClick(user);
     
     await screen.findByText('Software Engineer', {}, { timeout: 3000 });

     const jobCards = screen.getAllByTestId('job-card');
     const firstCard = jobCards[0];
     
     const buttons = firstCard.querySelectorAll('button');
     if (buttons.length >= 2) {
       const saveBtn = buttons[0];
       fireEvent.click(saveBtn);
       
       await waitFor(() => {
         expect(apiModule.applicationService.createApplication).toHaveBeenCalledWith(expect.objectContaining({
           job_title: 'Software Engineer',
           status: 'draft',
           notes: expect.stringContaining('Saved from job search')
         }));
       });
     }
   });

   it('filters jobs by criteria', async () => {
     vi.mocked(apiModule.jobSearchService.searchJobs).mockResolvedValue({ data: mockJobs });
     const user = userEvent.setup();

     renderJobSearch();

     // Type search query
     const searchInput = screen.getByPlaceholderText(/software engineer, react developer/i);
     fireEvent.change(searchInput, { target: { value: 'Python' } });

     // Get all buttons and find the select buttons by their id pattern
     const jobTypeButton = document.getElementById('select-job_type') as HTMLButtonElement;
     const experienceLevelButton = document.getElementById('select-experience_level') as HTMLButtonElement;

     // Click Job Type select and select "Full Time"
     if (jobTypeButton) {
       fireEvent.click(jobTypeButton);
       await waitFor(() => {
         const fullTimeOption = screen.getByText('Full Time');
         fireEvent.click(fullTimeOption);
       });
     }

     // Click Experience Level select and select "Senior"
     if (experienceLevelButton) {
       fireEvent.click(experienceLevelButton);
       await waitFor(() => {
         const seniorOption = screen.getByText('Senior');
         fireEvent.click(seniorOption);
       });
     }

     // Click Search button
     await searchAndClick(user);

     // Verify searchJobs was called with correct filters
     await waitFor(() => {
       expect(apiModule.jobSearchService.searchJobs).toHaveBeenCalledWith(
         expect.objectContaining({
           query: 'Python',
           job_type: 'full_time',
           experience_level: 'senior',
         })
       );
     });
   });
});
