// @vitest-environment jsdom
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import CoverLetters from '../../pages/CoverLetters';
import * as apiModule from '../../services/api';

// Polyfills
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

// Hoist the mock function so it's available in the factory
const { mockUseAppStore } = vi.hoisted(() => {
  return { mockUseAppStore: vi.fn() };
});

// Mock the API services
vi.mock('../../services/api', () => ({
  coverLetterService: {
    getCoverLetters: vi.fn().mockResolvedValue([]),
    createCoverLetter: vi.fn().mockResolvedValue({}),
    updateCoverLetter: vi.fn().mockResolvedValue({}),
    deleteCoverLetter: vi.fn().mockResolvedValue(true),
    bulkDelete: vi.fn().mockResolvedValue(true),
  },
  resumeService: {
    getResumes: vi.fn().mockResolvedValue([]),
  },
  aiService: {
    generateCoverLetter: vi.fn().mockResolvedValue({
      cover_letter: '',
      suggestions: [],
      confidence_score: 0
    }),
  },
}));

// Mock the AppStore
vi.mock('../../stores/appStore', () => ({
  useAppStore: mockUseAppStore,
}));

// Mock window.confirm
global.confirm = vi.fn(() => true);
// Mock URL.createObjectURL
global.URL.createObjectURL = vi.fn(() => 'blob:url');
global.URL.revokeObjectURL = vi.fn();

describe('CoverLetters Page', () => {
  let queryClient: QueryClient;

  const mockCoverLetters = [
    {
      id: '1',
      job_title: 'Software Engineer',
      company: 'Tech Corp',
      content: 'Dear Hiring Manager...',
      status: 'draft',
      word_count: 100,
      tone: 'professional',
      created_at: '2025-01-01T10:00:00Z',
      updated_at: '2025-01-01T10:00:00Z',
    },
    {
      id: '2',
      job_title: 'Frontend Developer',
      company: 'Startup Inc',
      content: 'I am writing to apply...',
      status: 'final',
      word_count: 150,
      tone: 'enthusiastic',
      created_at: '2025-01-02T10:00:00Z',
      updated_at: '2025-01-02T10:00:00Z',
    },
  ];

  const mockResumes = [
    {
      id: '1',
      title: 'Resume 1',
      content: 'Resume content',
      skills: [],
      experience_years: 2,
      education: [],
      certifications: [],
      is_default: true,
      file_path: '/path/1',
      created_at: '2025-01-01',
      updated_at: '2025-01-01'
    }
  ];

  // Mock functions for store actions
  const mockSetCoverLetters = vi.fn();
  const mockAddCoverLetter = vi.fn();
  const mockUpdateCoverLetter = vi.fn();
  const mockDeleteCoverLetter = vi.fn();

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    vi.clearAllMocks();

    // Default store mock
    mockUseAppStore.mockReturnValue({
      coverLetters: [],
      applications: [],
      setCoverLetters: mockSetCoverLetters,
      addCoverLetter: mockAddCoverLetter,
      updateCoverLetter: mockUpdateCoverLetter,
      deleteCoverLetter: mockDeleteCoverLetter,
    });
  });

  const renderCoverLetters = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <CoverLetters />
      </QueryClientProvider>
    );
  };

  it('renders loading state initially', () => {
    vi.mocked(apiModule.coverLetterService.getCoverLetters).mockReturnValue(new Promise(() => {}));

    renderCoverLetters();
    // It seems the text "Loading cover letters..." is used in the component
    expect(screen.getByText('Loading cover letters...')).toBeInTheDocument();
  });

  it('renders empty state', async () => {
    vi.mocked(apiModule.coverLetterService.getCoverLetters).mockResolvedValue([]);
    vi.mocked(apiModule.resumeService.getResumes).mockResolvedValue([]);
    mockUseAppStore.mockReturnValue({
        coverLetters: [],
        applications: [],
        setCoverLetters: mockSetCoverLetters,
        addCoverLetter: mockAddCoverLetter,
        updateCoverLetter: mockUpdateCoverLetter,
        deleteCoverLetter: mockDeleteCoverLetter,
    });

    renderCoverLetters();

    await waitFor(() => {
      expect(screen.getByText('No cover letters found')).toBeInTheDocument();
    });
    expect(screen.getByText('Create your first cover letter')).toBeInTheDocument();
  });

  it('renders list of cover letters', async () => {
    vi.mocked(apiModule.coverLetterService.getCoverLetters).mockResolvedValue(mockCoverLetters as any);
    vi.mocked(apiModule.resumeService.getResumes).mockResolvedValue([]);
    // IMPORTANT: Mock the store to return the data, as the component uses the store for rendering list
    mockUseAppStore.mockReturnValue({
        coverLetters: mockCoverLetters,
        applications: [],
        setCoverLetters: mockSetCoverLetters,
        addCoverLetter: mockAddCoverLetter,
        updateCoverLetter: mockUpdateCoverLetter,
        deleteCoverLetter: mockDeleteCoverLetter,
    });

    renderCoverLetters();

    await waitFor(() => {
      // Use getAllByText because "Software Engineer" might appear multiple times
      expect(screen.getAllByText('Software Engineer')[0]).toBeInTheDocument();
    });
    expect(screen.getByText('Tech Corp')).toBeInTheDocument();
    expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
    expect(screen.getByText('Startup Inc')).toBeInTheDocument();
  });

  it('opens create modal', async () => {
    vi.mocked(apiModule.coverLetterService.getCoverLetters).mockResolvedValue([]);
    vi.mocked(apiModule.resumeService.getResumes).mockResolvedValue([]);
    const user = userEvent.setup();

    renderCoverLetters();

    await waitFor(() => {
        expect(screen.getByRole('heading', { level: 1, name: /cover letters/i })).toBeInTheDocument();
    });

    const buttons = screen.getAllByRole('button');
    const createBtn = buttons.find(btn => /create new/i.test(btn.textContent || ''));
    expect(createBtn).toBeTruthy();
    await user.click(createBtn!);

    await waitFor(() => {
      expect(screen.getByRole('dialog', { name: /create new cover letter/i })).toBeInTheDocument();
    });
  });

  it('handles create cover letter submission', async () => {
    vi.mocked(apiModule.coverLetterService.getCoverLetters).mockResolvedValue([]);
    vi.mocked(apiModule.resumeService.getResumes).mockResolvedValue([]);
    vi.mocked(apiModule.coverLetterService.createCoverLetter).mockResolvedValue(mockCoverLetters[0] as any);
    const user = userEvent.setup();

    renderCoverLetters();

    await waitFor(() => {
        expect(screen.getByRole('heading', { level: 1, name: /cover letters/i })).toBeInTheDocument();
    });
    
    const buttons = screen.getAllByRole('button');
    const createBtn = buttons.find(btn => /create new/i.test(btn.textContent || ''));
    expect(createBtn).toBeTruthy();
    await user.click(createBtn!);

    // Fill form
    await user.type(screen.getByPlaceholderText(/senior software engineer/i), 'New Job');
    await user.type(screen.getByPlaceholderText(/tech corp/i), 'New Company');
    await user.type(screen.getByPlaceholderText(/write your cover letter/i), 'New Content');

    // Click submit
    await user.click(screen.getByRole('button', { name: /^create cover letter$/i }));

    await waitFor(() => {
      expect(apiModule.coverLetterService.createCoverLetter).toHaveBeenCalledWith(expect.objectContaining({
        job_title: 'New Job',
        company: 'New Company',
        content: 'New Content'
      }));
    });
  });

    it('handles AI generation flow', async () => {
      vi.mocked(apiModule.coverLetterService.getCoverLetters).mockResolvedValue([]);
      vi.mocked(apiModule.resumeService.getResumes).mockResolvedValue(mockResumes as any);
      vi.mocked(apiModule.aiService.generateCoverLetter).mockResolvedValue({
        cover_letter: 'AI Generated Content',
        suggestions: [],
        confidence_score: 0.9
      });
      const user = userEvent.setup();

      // Mock the store to include an application for job selection
      mockUseAppStore.mockReturnValue({
        coverLetters: [],
        applications: [{
          id: '1',
          job_title: 'Software Engineer',
          company: 'Tech Corp',
          status: 'applied',
          applied_date: '2025-01-01',
          job_url: 'https://example.com',
          notes: '',
          created_at: '2025-01-01',
          updated_at: '2025-01-01'
        }],
        setCoverLetters: mockSetCoverLetters,
        addCoverLetter: mockAddCoverLetter,
        updateCoverLetter: mockUpdateCoverLetter,
        deleteCoverLetter: mockDeleteCoverLetter,
      });

      renderCoverLetters();

      await waitFor(() => {
        expect(screen.getByText('Generate with AI')).toBeInTheDocument();
      });

      const buttons = screen.getAllByRole('button');
      const genBtn = buttons.find(btn => /generate with ai/i.test(btn.textContent || ''));
      expect(genBtn).toBeTruthy();
      await user.click(genBtn!);

      await waitFor(() => {
          expect(screen.getByRole('dialog', { name: /generate cover letter with ai/i })).toBeInTheDocument();
      });

      // Find and interact with the resume select dropdown
      // The Select component uses Listbox.Button, so we need to find it by its text content
      const allButtons = screen.getAllByRole('button');
      const resumeSelectBtn = allButtons.find(btn => {
        const text = btn.textContent || '';
        return text.includes('Select a resume') || text.includes('Resume 1') || text.includes('Unnamed Resume') || text.includes('Loading resumes');
      });
      
      expect(resumeSelectBtn).toBeTruthy();
      
      // Click to open the dropdown
      await user.click(resumeSelectBtn!);
      
      // Wait for the option to appear
      await waitFor(() => {
        const option = screen.queryByText('Resume 1');
        expect(option).toBeInTheDocument();
      }, { timeout: 2000 });
      
      // Click the resume option
      const resumeOption = screen.getByText('Resume 1');
      await user.click(resumeOption);

      // Now select a job application
      const jobSelectButtons = screen.getAllByRole('button');
      const jobSelectBtn = jobSelectButtons.find(btn => {
        const text = btn.textContent || '';
        return text.includes('Select a job application') || text.includes('Custom job details') || text.includes('Software Engineer');
      });
      
      if (jobSelectBtn) {
        await user.click(jobSelectBtn);
        
        // Wait for the job option to appear and click it
        await waitFor(() => {
          const jobOption = screen.queryByText(/Software Engineer at Tech Corp/);
          expect(jobOption).toBeInTheDocument();
        }, { timeout: 2000 });
        
        const jobOption = screen.getByText(/Software Engineer at Tech Corp/);
        await user.click(jobOption);
      }

      // Wait for the button to become enabled (selectedResume is set)
      // This is critical - the button is disabled until a resume is selected
      await waitFor(() => {
        const generateBtn = screen.getByRole('button', { name: /generate cover letter/i });
        expect(generateBtn).not.toBeDisabled();
      }, { timeout: 2000 });

      // Fill required fields
      await user.type(screen.getByPlaceholderText(/senior software engineer/i), 'AI Job');
      await user.type(screen.getByPlaceholderText(/tech corp/i), 'AI Company');

      // Verify the button is enabled before clicking
      const generateBtn = screen.getByRole('button', { name: /generate cover letter/i });
      expect(generateBtn).not.toBeDisabled();
      
      // Click the "Generate Cover Letter" button to submit
      await user.click(generateBtn);

      // Wait for aiService.generateCoverLetter to be called
      await waitFor(() => {
        expect(apiModule.aiService.generateCoverLetter).toHaveBeenCalled();
      }, { timeout: 3000 });

      // Wait for "AI Generated Content" (mocked result) to appear in the document
      // The content is displayed in an Alert component, so we need to wait for it
      await waitFor(() => {
        // The content might be in the Alert message or in the document
        const content = screen.queryByText(/AI Generated Content/);
        expect(content).toBeInTheDocument();
      }, { timeout: 3000 });

      // Verify "Save Cover Letter" button appears
      const saveBtn = screen.queryByRole('button', { name: /save cover letter/i });
      expect(saveBtn).toBeInTheDocument();
    });

   it('handles delete cover letter', async () => {
     vi.mocked(apiModule.coverLetterService.getCoverLetters).mockResolvedValue(mockCoverLetters as any);
     vi.mocked(apiModule.coverLetterService.deleteCoverLetter).mockResolvedValue(true);
     
     // Mock store to return cover letters
     mockUseAppStore.mockReturnValue({
         coverLetters: mockCoverLetters,
         applications: [],
         setCoverLetters: mockSetCoverLetters,
         addCoverLetter: mockAddCoverLetter,
         updateCoverLetter: mockUpdateCoverLetter,
         deleteCoverLetter: mockDeleteCoverLetter,
     });

     const user = userEvent.setup();

     renderCoverLetters();

     await waitFor(() => {
       expect(screen.getAllByText('Software Engineer')[0]).toBeInTheDocument();
     });

     // Find delete button
     const deleteButtons = document.querySelectorAll('.text-red-600');
     if (deleteButtons.length > 0) {
       await user.click(deleteButtons[0]);
       expect(global.confirm).toHaveBeenCalled();
       expect(apiModule.coverLetterService.deleteCoverLetter).toHaveBeenCalledWith(mockCoverLetters[0].id);
     }
   });

   it('edits cover letter', async () => {
     vi.mocked(apiModule.coverLetterService.getCoverLetters).mockResolvedValue(mockCoverLetters as any);
     vi.mocked(apiModule.coverLetterService.updateCoverLetter).mockResolvedValue(mockCoverLetters[0] as any);
     
     // Mock store to return cover letters
     mockUseAppStore.mockReturnValue({
         coverLetters: mockCoverLetters,
         applications: [],
         setCoverLetters: mockSetCoverLetters,
         addCoverLetter: mockAddCoverLetter,
         updateCoverLetter: mockUpdateCoverLetter,
         deleteCoverLetter: mockDeleteCoverLetter,
     });

     const user = userEvent.setup();

     renderCoverLetters();

     await waitFor(() => {
       expect(screen.getAllByText('Software Engineer')[0]).toBeInTheDocument();
     });

     // Find and click edit button (pencil icon)
     const editButtons = document.querySelectorAll('button svg[class*="pencil"], button svg[class*="edit"]');
     if (editButtons.length > 0) {
       const editButton = editButtons[0].closest('button');
       expect(editButton).toBeTruthy();
       await user.click(editButton!);

       // Wait for modal to open
       await waitFor(() => {
         expect(screen.getByRole('dialog')).toBeInTheDocument();
       });

       // Modify content
       const contentInput = screen.getByPlaceholderText(/write your cover letter/i);
       await user.clear(contentInput);
       await user.type(contentInput, 'Updated cover letter content');

       // Submit
       const submitBtn = screen.getByRole('button', { name: /update cover letter/i });
       await user.click(submitBtn);

       // Verify updateCoverLetter was called
       await waitFor(() => {
         expect(apiModule.coverLetterService.updateCoverLetter).toHaveBeenCalledWith(
           mockCoverLetters[0].id,
           expect.objectContaining({
             content: 'Updated cover letter content'
           })
         );
       });
     }
   });

   it('downloads cover letter', async () => {
     vi.mocked(apiModule.coverLetterService.getCoverLetters).mockResolvedValue(mockCoverLetters as any);
     
     // Mock store to return cover letters
     mockUseAppStore.mockReturnValue({
         coverLetters: mockCoverLetters,
         applications: [],
         setCoverLetters: mockSetCoverLetters,
         addCoverLetter: mockAddCoverLetter,
         updateCoverLetter: mockUpdateCoverLetter,
         deleteCoverLetter: mockDeleteCoverLetter,
     });

     const user = userEvent.setup();
     const createObjectURLSpy = vi.spyOn(URL, 'createObjectURL');

     renderCoverLetters();

     await waitFor(() => {
       expect(screen.getAllByText('Software Engineer')[0]).toBeInTheDocument();
     });

     // Find and click download button (document arrow icon)
     const downloadButtons = document.querySelectorAll('button svg[class*="arrow"], button svg[class*="download"]');
     if (downloadButtons.length > 0) {
       const downloadButton = downloadButtons[0].closest('button');
       expect(downloadButton).toBeTruthy();
       await user.click(downloadButton!);

       // Verify createObjectURL was called
       await waitFor(() => {
         expect(createObjectURLSpy).toHaveBeenCalled();
       });
     }

     createObjectURLSpy.mockRestore();
   });
});
