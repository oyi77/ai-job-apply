import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AutoApply from '../../pages/AutoApply';
import * as apiModule from '../../services/api';

// Mock API services
vi.mock('../../services/api', () => ({
  autoApplyService: {
    getConfig: vi.fn(),
    updateConfig: vi.fn(),
    start: vi.fn(),
    stop: vi.fn(),
    getActivity: vi.fn()
  }
}));

describe('AutoApply Page', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false }
      }
    });
    vi.clearAllMocks();
  });

  const renderAutoApply = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <AutoApply />
      </QueryClientProvider>
    );
  };

  it('renders configuration form', async () => {
    vi.mocked(apiModule.autoApplyService.getConfig).mockResolvedValue({
      keywords: ['Python'],
      locations: ['Remote'],
      min_salary: 100000,
      daily_limit: 5,
      is_active: false
    });

    renderAutoApply();

    await waitFor(() => {
      expect(screen.getByDisplayValue('Python')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Remote')).toBeInTheDocument();
      expect(screen.getByDisplayValue('100000')).toBeInTheDocument();
    });
  });

  it('toggles auto-apply status', async () => {
    vi.mocked(apiModule.autoApplyService.getConfig).mockResolvedValue({
      is_active: false,
      keywords: [],
      locations: [],
      daily_limit: 5
    });

    renderAutoApply();
    
    const toggle = await screen.findByLabelText(/auto apply status/i);
    await userEvent.click(toggle);

    expect(apiModule.autoApplyService.start).toHaveBeenCalled();
  });

  it('updates configuration', async () => {
    vi.mocked(apiModule.autoApplyService.getConfig).mockResolvedValue({
      keywords: [],
      locations: [],
      daily_limit: 5,
      is_active: false
    });

    renderAutoApply();

    const keywordsInput = await screen.findByPlaceholderText(/e.g. Python/i);
    await userEvent.type(keywordsInput, 'React');

    const saveButton = screen.getByText(/save configuration/i);
    await userEvent.click(saveButton);

    expect(apiModule.autoApplyService.updateConfig).toHaveBeenCalledWith(
      expect.objectContaining({
        keywords: ['React']
      })
    );
  });
});
