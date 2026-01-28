import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AIServices from '../../pages/AIServices';
import * as apiModule from '../../services/api';

// Polyfill for Headless UI / JSDOM
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

class IntersectionObserverMock {
  root = null;
  rootMargin = "";
  thresholds = [];
  observe() {}
  unobserve() {}
  disconnect() {}
  takeRecords() { return []; }
}

global.ResizeObserver = ResizeObserverMock;
global.IntersectionObserver = IntersectionObserverMock;

// Mock the API services
vi.mock('../../services/api', () => ({
  aiService: {
    getStatus: vi.fn(),
    optimizeResume: vi.fn(),
    generateCoverLetter: vi.fn(),
    analyzeJobMatch: vi.fn(),
    extractSkills: vi.fn(),
    prepareInterview: vi.fn(),
    generateCareerInsights: vi.fn(),
  },
  resumeService: {
    getResume: vi.fn(),
  },
}));

// Mock the AppStore
vi.mock('../../stores/appStore', () => ({
  useAppStore: () => ({
    resumes: [
      { id: '1', title: 'Resume 1', content: 'Resume content' },
      { id: '2', title: 'Resume 2', content: 'Resume content 2' },
    ],
    applications: [
      { id: '1', job_title: 'Job 1', company: 'Company 1' },
    ],
  }),
}));

describe('AIServices Page', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    vi.clearAllMocks();

    // Default mocks for all services to avoid undefined errors
    vi.mocked(apiModule.aiService.getStatus).mockResolvedValue({ status: 'online', available: true, model: 'Gemini Pro' });
    vi.mocked(apiModule.aiService.optimizeResume).mockResolvedValue({ 
      optimized_content: 'Optimized content',
      suggestions: ['Add more keywords'],
      skills_gap: [],
      confidence_score: 0.85
    });
    vi.mocked(apiModule.aiService.generateCoverLetter).mockResolvedValue({ 
      cover_letter: 'Cover letter content',
      suggestions: [],
      confidence_score: 0.9
    });
    vi.mocked(apiModule.aiService.analyzeJobMatch).mockResolvedValue({ 
      match_score: 85, 
      suggestions: [] 
    });
    vi.mocked(apiModule.aiService.extractSkills).mockResolvedValue({ skills: ['React'], confidence: 0.9 });
     vi.mocked(apiModule.aiService.prepareInterview).mockResolvedValue({ questions: [] });
     vi.mocked(apiModule.aiService.generateCareerInsights).mockResolvedValue({ 
       market_analysis: 'Good', 
       salary_insights: { 
         estimated_range: '$100k - $120k',
         market_trend: 'Growing',
         location_factor: 'High demand'
       },
       recommended_roles: [],
       skill_gaps: [],
       strategic_advice: [],
       confidence_score: 0.9
     });
     vi.mocked(apiModule.resumeService.getResume).mockResolvedValue({ 
       id: '1', 
       title: 'Resume 1', 
       content: 'Resume content',
       filename: 'resume.pdf',
       file_path: '/path/to/resume.pdf',
       skills: ['React', 'TypeScript'],
       experience_years: 5,
       education: [],
       certifications: [],
       is_default: true,
       created_at: new Date().toISOString(),
       updated_at: new Date().toISOString()
     });
   });

  const renderAIServices = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <AIServices />
      </QueryClientProvider>
    );
  };

  const waitForLoading = async () => {
    await waitFor(() => {
      expect(screen.queryByRole('status')).not.toBeInTheDocument();
    });
  };

  it('renders page header', async () => {
    vi.mocked(apiModule.aiService.getStatus).mockResolvedValue({ status: 'online', available: true, model: 'Gemini Pro' });
    renderAIServices();
    await waitForLoading();
    expect(screen.getByRole('heading', { level: 1, name: /ai services/i })).toBeInTheDocument();
  });

  it('renders AI status', async () => {
    vi.mocked(apiModule.aiService.getStatus).mockResolvedValue({ status: 'online', available: true, model: 'Gemini Pro' });
    renderAIServices();
    await waitForLoading();
    expect(screen.getByText('AI services are ready to use')).toBeInTheDocument();
    expect(screen.getByText(/Gemini Pro/)).toBeInTheDocument();
  });

  it('opens Resume Optimization modal', async () => {
    vi.mocked(apiModule.aiService.getStatus).mockResolvedValue({ status: 'online', available: true });
    const user = userEvent.setup();
    renderAIServices();
    await waitForLoading();

    const buttons = screen.getAllByRole('button');
    const btn = buttons.find(b => /optimize resume/i.test(b.textContent || ''));
    expect(btn).toBeTruthy();
    await user.click(btn!);
    
    await waitFor(() => {
      // Check for title text instead of role to avoid accessibility computation issues
      expect(screen.getByRole('dialog', { name: /resume optimization/i })).toBeInTheDocument();
    });
  });

  it('opens Cover Letter Generation modal', async () => {
    vi.mocked(apiModule.aiService.getStatus).mockResolvedValue({ status: 'online', available: true });
    const user = userEvent.setup();
    renderAIServices();
    await waitForLoading();

    const buttons = screen.getAllByRole('button');
    const btn = buttons.find(b => /generate cover letter/i.test(b.textContent || ''));
    expect(btn).toBeTruthy();
    await user.click(btn!);
    
    await waitFor(() => {
      expect(screen.getByRole('dialog', { name: /generate cover letter/i })).toBeInTheDocument();
    });
  });

  it('opens Job Matching modal', async () => {
    vi.mocked(apiModule.aiService.getStatus).mockResolvedValue({ status: 'online', available: true });
    const user = userEvent.setup();
    renderAIServices();
    await waitForLoading();

    const buttons = screen.getAllByRole('button');
    const btn = buttons.find(b => /analyze match/i.test(b.textContent || ''));
    expect(btn).toBeTruthy();
    await user.click(btn!);
    
    await waitFor(() => {
      expect(screen.getByText('Job Matching Analysis')).toBeInTheDocument();
    });
  });

   it('opens Interview Prep modal', async () => {
     vi.mocked(apiModule.aiService.getStatus).mockResolvedValue({ status: 'online', available: true });
     const user = userEvent.setup();
     renderAIServices();
     await waitForLoading();

     const buttons = screen.getAllByRole('button');
     const btn = buttons.find(b => /prepare for interview/i.test(b.textContent || ''));
     expect(btn).toBeTruthy();
     await user.click(btn!);
     
     await waitFor(() => {
       expect(screen.getByText('Interview Preparation')).toBeInTheDocument();
     });
   });

     it('optimizes resume successfully', async () => {
       vi.mocked(apiModule.aiService.getStatus).mockResolvedValue({ status: 'online', available: true });
       const user = userEvent.setup();
       renderAIServices();
       await waitForLoading();

       // Open Resume Optimization modal
       const buttons = screen.getAllByRole('button');
       const optimizeBtn = buttons.find(b => /optimize resume/i.test(b.textContent || ''));
       expect(optimizeBtn).toBeTruthy();
       await user.click(optimizeBtn!);

       // Wait for modal to open
       await waitFor(() => {
         expect(screen.getByRole('dialog', { name: /resume optimization/i })).toBeInTheDocument();
       });

       // Click the Select Resume button to open dropdown
       // Use robust pattern: find all buttons and search by text content
       const allButtons = screen.getAllByRole('button');
       const resumeSelectBtn = allButtons.find(btn => {
         const text = btn.textContent || '';
         return text.includes('Choose a resume to optimize') || text.includes('Resume 1') || text.includes('Resume 2');
       });
       expect(resumeSelectBtn).toBeTruthy();
       await user.click(resumeSelectBtn!);
      
      // Wait for options and select first resume
      await waitFor(() => {
        const options = screen.getAllByRole('option');
        expect(options.length).toBeGreaterThan(0);
      });
      const options = screen.getAllByRole('option');
      await user.click(options[0]);

      // Fill in job description textarea
      const textareas = screen.getAllByRole('textbox');
      const jobDescriptionField = textareas.find(ta => 
        ta.getAttribute('placeholder')?.includes('job description')
      );
      expect(jobDescriptionField).toBeTruthy();
      await user.type(jobDescriptionField!, 'Senior React Developer needed for fintech startup');

      // Submit the form
      const submitButtons = screen.getAllByRole('button');
      const submitBtn = submitButtons.find(b => /optimize resume/i.test(b.textContent || '') && b !== optimizeBtn && b !== resumeSelectBtn);
      expect(submitBtn).toBeTruthy();
      await user.click(submitBtn!);

     // Wait for result to appear
     await waitFor(() => {
       expect(screen.getByText(/optimization result/i)).toBeInTheDocument();
     });

     // Verify the optimized content is displayed
     expect(screen.getByText(/optimized content/i)).toBeInTheDocument();
   });

     it('displays match score', async () => {
       vi.mocked(apiModule.aiService.getStatus).mockResolvedValue({ status: 'online', available: true });
       const user = userEvent.setup();
       renderAIServices();
       await waitForLoading();

       // Open Job Matching modal
       const buttons = screen.getAllByRole('button');
       const matchBtn = buttons.find(b => /analyze match/i.test(b.textContent || ''));
       expect(matchBtn).toBeTruthy();
       await user.click(matchBtn!);

       // Wait for modal to open
       await waitFor(() => {
         expect(screen.getByText('Job Matching Analysis')).toBeInTheDocument();
       });

       // Click the Select Resume button to open dropdown
       // Use robust pattern: find all buttons and search by text content
       const allButtons = screen.getAllByRole('button');
       const resumeSelectBtn = allButtons.find(btn => {
         const text = btn.textContent || '';
         return text.includes('Choose a resume to analyze') || text.includes('Resume 1') || text.includes('Resume 2');
       });
       expect(resumeSelectBtn).toBeTruthy();
       await user.click(resumeSelectBtn!);

      // Wait for options and select first resume
      await waitFor(() => {
        const options = screen.getAllByRole('option');
        expect(options.length).toBeGreaterThan(0);
      });
      const options = screen.getAllByRole('option');
      await user.click(options[0]);

      // Fill in job description textarea
      const textareas = screen.getAllByRole('textbox');
      const jobDescriptionField = textareas.find(ta => 
        ta.getAttribute('placeholder')?.includes('job description')
      );
      expect(jobDescriptionField).toBeTruthy();
      await user.type(jobDescriptionField!, 'Looking for a React developer with 5+ years experience');

      // Submit the form
      const submitButtons = screen.getAllByRole('button');
      const submitBtn = submitButtons.find(b => /analyze match/i.test(b.textContent || '') && b !== matchBtn && b !== resumeSelectBtn);
      expect(submitBtn).toBeTruthy();
      await user.click(submitBtn!);

     // Wait for match score to appear
     await waitFor(() => {
       expect(screen.getByText(/overall match score/i)).toBeInTheDocument();
     });

     // Verify match score is displayed with percentage
     const matchScoreBadge = screen.getByText(/85%/);
     expect(matchScoreBadge).toBeInTheDocument();

     // Verify match score label is displayed
     expect(screen.getByText(/excellent match/i)).toBeInTheDocument();
   });

    it('displays interview questions', async () => {
      vi.mocked(apiModule.aiService.getStatus).mockResolvedValue({ status: 'online', available: true });
     vi.mocked(apiModule.aiService.prepareInterview).mockResolvedValue({
       questions: [
         { question: 'Tell us about your experience', type: 'behavioral', suggested_answer: 'I have 5 years of experience...', tips: ['Be specific', 'Use examples'] },
         { question: 'What is your greatest strength?', type: 'general', suggested_answer: 'Problem solving', tips: ['Relate to job'] }
       ],
       technical_questions: [
         { question: 'Explain React hooks', category: 'React', difficulty: 'medium', suggested_approach: 'Start with useState...' }
       ],
       preparation_tips: ['Research the company', 'Practice common questions'],
       key_topics: ['React', 'JavaScript', 'System Design'],
       questions_to_ask: ['What does success look like?', 'What is the team structure?'],
       company_research: 'Tech startup founded in 2020'
     });
     const user = userEvent.setup();
     renderAIServices();
     await waitForLoading();

     // Open Interview Prep modal
     const buttons = screen.getAllByRole('button');
     const interviewBtn = buttons.find(b => /prepare for interview/i.test(b.textContent || ''));
     expect(interviewBtn).toBeTruthy();
     await user.click(interviewBtn!);

      // Wait for modal to open
      await waitFor(() => {
        expect(screen.getByText('Interview Preparation')).toBeInTheDocument();
      });

        // Click the Select Job Application button to open dropdown
        // Use robust pattern: find all buttons and search by proximity to label
        const selectLabel = screen.getByText('Select Job Application');
        const selectContainer = selectLabel.parentElement?.parentElement;
        const allButtonsInContainer = selectContainer?.querySelectorAll('button');
        const applicationSelectBtn = allButtonsInContainer?.[0];
        expect(applicationSelectBtn).toBeTruthy();
        await user.click(applicationSelectBtn!);

     // Wait for options and select first application
     await waitFor(() => {
       const options = screen.getAllByRole('option');
       expect(options.length).toBeGreaterThan(0);
     });
     const options = screen.getAllByRole('option');
     // Skip the placeholder option and select the first real application
     const realOptions = options.filter(opt => opt.textContent !== 'Select a job application');
     if (realOptions.length > 0) {
       await user.click(realOptions[0]);
     }

      // Wait for the async operation to complete
      // The component shows a spinner with text "Preparing interview questions..."
      // We need to wait for this spinner to disappear and the results to appear
      await waitFor(() => {
        // Check that either the loading spinner is gone OR the results are showing
        const hasResults = screen.queryByRole('heading', { name: /interview questions/i });
        const isLoading = screen.queryByText(/preparing interview questions/i);
        expect(hasResults || !isLoading).toBeTruthy();
      }, { timeout: 10000 });

      // Verify interview questions are displayed
      expect(screen.getByRole('heading', { name: /interview questions/i })).toBeInTheDocument();

      // Verify specific questions are displayed
      expect(screen.getByText(/tell us about your experience/i)).toBeInTheDocument();
      expect(screen.getByText(/what is your greatest strength/i)).toBeInTheDocument();

      // Verify technical questions section
      expect(screen.getByRole('heading', { name: /technical questions/i })).toBeInTheDocument();
      expect(screen.getByText(/explain react hooks/i)).toBeInTheDocument();

      // Verify preparation tips
      expect(screen.getByRole('heading', { name: /preparation tips/i })).toBeInTheDocument();
      expect(screen.getByText(/research the company/i)).toBeInTheDocument();

      // Verify key topics
      expect(screen.getByRole('heading', { name: /key topics to review/i })).toBeInTheDocument();
      // Check that React appears as a badge in the key topics section
      const badges = screen.getAllByText(/React/);
      expect(badges.length).toBeGreaterThan(0);

      // Verify questions to ask
      expect(screen.getByRole('heading', { name: /questions to ask the interviewer/i })).toBeInTheDocument();
      expect(screen.getByText(/what does success look like/i)).toBeInTheDocument();

      // Verify company research
      expect(screen.getByRole('heading', { name: /company research/i })).toBeInTheDocument();
      expect(screen.getByText(/tech startup founded in 2020/i)).toBeInTheDocument();
   });
});
