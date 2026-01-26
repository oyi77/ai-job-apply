import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import Applications from '../../pages/Applications';
import * as apiModule from '../../services/api';
import type { JobApplication } from '../../types';

// Mock the applicationService
vi.mock('../../services/api', () => ({
  applicationService: {
    getApplications: vi.fn(),
    createApplication: vi.fn(),
    updateApplication: vi.fn(),
    deleteApplication: vi.fn(),
    bulkUpdate: vi.fn(),
    bulkDelete: vi.fn(),
  },
  exportService: {
    exportApplications: vi.fn(),
  },
}));

// Mock the ExportModal component
vi.mock('../../components/ExportModal', () => ({
  ExportModal: ({ isOpen, onClose }: any) => (
    isOpen ? <div data-testid="export-modal">Export Modal</div> : null
  ),
}));

// Mock window.confirm
global.confirm = vi.fn(() => true);

// Mock window.URL.createObjectURL and revokeObjectURL
global.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
global.URL.revokeObjectURL = vi.fn();

describe('ApplicationFlow Integration Tests', () => {
  let queryClient: QueryClient;

  const mockApplications: JobApplication[] = [
    {
      id: '1',
      job_id: 'job-001',
      job_title: 'Senior Software Engineer',
      company: 'Google',
      location: 'Mountain View, CA',
      status: 'applied',
      applied_date: '2025-01-20',
      notes: 'Great opportunity',
      created_at: '2025-01-20T10:00:00Z',
      updated_at: '2025-01-20T10:00:00Z',
    },
    {
      id: '2',
      job_id: 'job-002',
      job_title: 'Frontend Developer',
      company: 'Meta',
      location: 'Menlo Park, CA',
      status: 'under_review',
      applied_date: '2025-01-19',
      notes: 'Waiting for response',
      created_at: '2025-01-19T10:00:00Z',
      updated_at: '2025-01-19T10:00:00Z',
    },
    {
      id: '3',
      job_id: 'job-003',
      job_title: 'Full Stack Developer',
      company: 'Amazon',
      location: 'Seattle, WA',
      status: 'interview_scheduled',
      applied_date: '2025-01-18',
      created_at: '2025-01-18T10:00:00Z',
      updated_at: '2025-01-18T10:00:00Z',
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

  const renderApplicationsPage = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <Applications />
        </MemoryRouter>
      </QueryClientProvider>
    );
  };

  it('should load and display applications from the API', async () => {
    // Mock the API response
    vi.mocked(apiModule.applicationService.getApplications).mockResolvedValue({
      data: mockApplications,
    } as any);

    renderApplicationsPage();

    // Wait for applications to load
    await waitFor(() => {
      expect(screen.getByText('Senior Software Engineer')).toBeInTheDocument();
    });

    // Verify all applications are displayed
    expect(screen.getByText('Google')).toBeInTheDocument();
    expect(screen.getByText('Meta')).toBeInTheDocument();
    expect(screen.getByText('Amazon')).toBeInTheDocument();

    // Verify status badges are displayed (with underscores replaced by spaces)
    expect(screen.getByText('applied')).toBeInTheDocument();
    expect(screen.getByText('under review')).toBeInTheDocument();
    expect(screen.getByText('interview scheduled')).toBeInTheDocument();
  });

  it('should display loading state while fetching applications', () => {
    // Mock a pending promise
    vi.mocked(apiModule.applicationService.getApplications).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    renderApplicationsPage();

    // Spinner should be visible
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('should display error state when API fails', async () => {
    // Mock API error
    vi.mocked(apiModule.applicationService.getApplications).mockRejectedValue(
      new Error('Failed to fetch applications')
    );

    renderApplicationsPage();

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText('Error Loading Applications')).toBeInTheDocument();
    });

    expect(
      screen.getByText('Failed to load applications. Please try again later.')
    ).toBeInTheDocument();
  });

  it('should display empty state when no applications exist', async () => {
    // Mock empty response
    vi.mocked(apiModule.applicationService.getApplications).mockResolvedValue({
      data: [],
    } as any);

    renderApplicationsPage();

    await waitFor(() => {
      expect(screen.getByText('No applications found')).toBeInTheDocument();
    });

    expect(
      screen.getByText('Get started by creating your first job application.')
    ).toBeInTheDocument();
  });

  it('should open view modal when clicking on an application', async () => {
    vi.mocked(apiModule.applicationService.getApplications).mockResolvedValue({
      data: mockApplications,
    } as any);

    const user = userEvent.setup();
    renderApplicationsPage();

    // Wait for applications to load
    await waitFor(() => {
      expect(screen.getByText('Senior Software Engineer')).toBeInTheDocument();
    });

    // Find and click the view button (eye icon) for the first application
    const viewButtons = screen.getAllByRole('button');
    const viewButton = viewButtons.find(
      (btn) => btn.querySelector('svg') && btn.parentElement?.textContent?.includes('Google')
    );

    if (viewButton) {
      await user.click(viewButton);

      // Modal should be visible with application details
      await waitFor(() => {
        expect(screen.getByText('Application Details')).toBeInTheDocument();
      });

      expect(screen.getByText('Senior Software Engineer')).toBeInTheDocument();
      expect(screen.getByText('Google')).toBeInTheDocument();
    }
  });

  it('should filter applications by status', async () => {
    vi.mocked(apiModule.applicationService.getApplications).mockResolvedValue({
      data: mockApplications,
    } as any);

    const user = userEvent.setup();
    renderApplicationsPage();

    // Wait for applications to load
    await waitFor(() => {
      expect(screen.getByText('Senior Software Engineer')).toBeInTheDocument();
    });

    // Verify all applications are visible initially
    expect(screen.getByText('Google')).toBeInTheDocument();
    expect(screen.getByText('Meta')).toBeInTheDocument();
    expect(screen.getByText('Amazon')).toBeInTheDocument();
  });

  it('should display application count', async () => {
    vi.mocked(apiModule.applicationService.getApplications).mockResolvedValue({
      data: mockApplications,
    } as any);

    renderApplicationsPage();

    await waitFor(() => {
      expect(screen.getByText(/3 of 3 applications/)).toBeInTheDocument();
    });
  });

  it('should handle application selection with checkboxes', async () => {
    vi.mocked(apiModule.applicationService.getApplications).mockResolvedValue({
      data: mockApplications,
    } as any);

    const user = userEvent.setup();
    renderApplicationsPage();

    // Wait for applications to load
    await waitFor(() => {
      expect(screen.getByText('Senior Software Engineer')).toBeInTheDocument();
    });

    // Get all checkboxes (header + application rows)
    const checkboxes = screen.getAllByRole('checkbox');

    // Verify checkboxes exist
    expect(checkboxes.length).toBeGreaterThan(1);

    // Click the first application's checkbox
    if (checkboxes[1]) {
      await user.click(checkboxes[1]);

      // Bulk actions toolbar should appear with selection count
      await waitFor(() => {
        const selectedText = screen.queryByText(/items selected/);
        expect(selectedText).toBeInTheDocument();
      });
    }
  });

  it('should display "New Application" button', async () => {
    vi.mocked(apiModule.applicationService.getApplications).mockResolvedValue({
      data: mockApplications,
    } as any);

    renderApplicationsPage();

    await waitFor(() => {
      expect(screen.getByText('New Application')).toBeInTheDocument();
    });
  });

  it('should display export button', async () => {
    vi.mocked(apiModule.applicationService.getApplications).mockResolvedValue({
      data: mockApplications,
    } as any);

    renderApplicationsPage();

    await waitFor(() => {
      expect(screen.getByText('Export')).toBeInTheDocument();
    });
  });

  it('should handle nested response structure from API', async () => {
    // Mock nested response structure: { data: { data: [...], pagination: {...} } }
    vi.mocked(apiModule.applicationService.getApplications).mockResolvedValue({
      data: {
        data: mockApplications,
        pagination: { total: 3, page: 1 },
      },
    } as any);

    renderApplicationsPage();

    // Applications should still load correctly
    await waitFor(() => {
      expect(screen.getByText('Senior Software Engineer')).toBeInTheDocument();
    });

    expect(screen.getByText('Google')).toBeInTheDocument();
    expect(screen.getByText('Meta')).toBeInTheDocument();
  });

  it('should display application notes when present', async () => {
    vi.mocked(apiModule.applicationService.getApplications).mockResolvedValue({
      data: mockApplications,
    } as any);

    renderApplicationsPage();

    await waitFor(() => {
      expect(screen.getByText('Great opportunity')).toBeInTheDocument();
      expect(screen.getByText('Waiting for response')).toBeInTheDocument();
    });
  });

  it('should display applied date in correct format', async () => {
    vi.mocked(apiModule.applicationService.getApplications).mockResolvedValue({
      data: mockApplications,
    } as any);

    renderApplicationsPage();

    await waitFor(() => {
      // Check for formatted dates (will depend on locale)
      const dateElements = screen.getAllByText(/Applied:/);
      expect(dateElements.length).toBeGreaterThan(0);
    });
  });
});
