import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from '../Dashboard';
import { useAppStore } from '../../stores/appStore';

vi.mock('../../stores/appStore');
vi.mock('../../services/api', () => ({
  applicationService: {
    getStats: vi.fn().mockResolvedValue({
      total: 10,
      by_status: { applied: 5, under_review: 3, rejected: 2 },
      success_rate: 0.3,
      avg_response_time: 5,
    }),
  },
}));

describe('Dashboard', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
    vi.clearAllMocks();
  });

  const renderDashboard = () => {
    (useAppStore as any).mockReturnValue({
      applications: [
        { id: '1', job_title: 'Software Engineer', company: 'Tech Corp', status: 'applied' },
        { id: '2', job_title: 'Developer', company: 'Dev Inc', status: 'under_review' },
      ],
      resumes: [{ id: '1', name: 'Resume.pdf' }],
      coverLetters: [{ id: '1', job_title: 'Engineer', company_name: 'Corp' }],
    });

    return render(
      <QueryClientProvider client={queryClient}>
        <Dashboard />
      </QueryClientProvider>
    );
  };

  it('renders dashboard', () => {
    renderDashboard();
    expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
  });

  it('displays application statistics', async () => {
    renderDashboard();
    await waitFor(() => {
      expect(screen.getByText(/total applications/i)).toBeInTheDocument();
    });
  });

  it('displays recent applications', () => {
    renderDashboard();
    expect(screen.getByText(/recent applications/i)).toBeInTheDocument();
  });
});

