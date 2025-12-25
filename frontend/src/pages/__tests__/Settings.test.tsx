import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Settings from '../Settings';
import { useAppStore } from '../../stores/appStore';
import { authService } from '../../services/api';

// Mock the store
vi.mock('../../stores/appStore', () => ({
  useAppStore: vi.fn(),
}));

// Mock the API service
vi.mock('../../services/api', () => ({
  applicationService: {
    getApplications: vi.fn().mockResolvedValue({ data: [], total: 0 }),
  },
  resumeService: {
    getResumes: vi.fn().mockResolvedValue([]),
  },
  coverLetterService: {
    getCoverLetters: vi.fn().mockResolvedValue([]),
  },
  authService: {
    updateProfile: vi.fn(),
  },
}));

describe('Settings', () => {
  const mockSetUser = vi.fn();
  const mockSetTheme = vi.fn();
  const mockUpdateAISettings = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useAppStore as any).mockReturnValue({
      user: {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        first_name: 'Test',
        last_name: 'User',
        preferences: {
          theme: 'light',
          notifications: {},
          privacy: {},
          ai: { provider_preference: 'openai' },
        },
      },
      setUser: mockSetUser,
      theme: 'light',
      setTheme: mockSetTheme,
      aiSettings: { provider_preference: 'openai' },
      updateAISettings: mockUpdateAISettings,
    });
  });

  it('renders correctly', () => {
    render(<Settings />);
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('opens profile modal when Edit Profile is clicked', async () => {
    const user = userEvent.setup();
    render(<Settings />);
    const editButton = screen.getByText('Edit Profile');
    await user.click(editButton);
    expect(screen.getByText('Edit Profile', { selector: 'h3' })).toBeInTheDocument();
  });

  it('calls API and updates user state when profile is updated', async () => {
    const user = userEvent.setup();
    const updatedProfile = {
      name: 'Updated User',
      email: 'updated@example.com',
    };
    (authService.updateProfile as any).mockResolvedValue(updatedProfile);

    render(<Settings />);

    // Open modal
    await user.click(screen.getByText('Edit Profile'));

    // Fill form
    const firstNameInput = screen.getByPlaceholderText('Enter your first name');
    const lastNameInput = screen.getByPlaceholderText('Enter your last name');
    const emailInput = screen.getByPlaceholderText('Enter your email');

    await user.clear(firstNameInput);
    await user.type(firstNameInput, 'Updated');

    await user.clear(lastNameInput);
    await user.type(lastNameInput, 'User');

    await user.clear(emailInput);
    await user.type(emailInput, 'updated@example.com');

    // Submit form
    const submitButton = screen.getByText('Save Changes');
    await user.click(submitButton);

    await waitFor(() => {
      // The updateProfile call arguments should contain the form data
      // Note: We might need to be more permissive with the expectation if exact object structure fails
      // due to extra fields or structure mismatch.
      // But looking at the implementation:
      // apiData = { ...data, name: ... }
      // So it should contain first_name, last_name, email, and name.
      expect(authService.updateProfile).toHaveBeenCalledWith(expect.objectContaining({
        first_name: 'Updated',
        last_name: 'User',
        email: 'updated@example.com',
      }));
    });

    expect(mockSetUser).toHaveBeenCalledWith(expect.objectContaining({
        ...updatedProfile,
        first_name: 'Updated',
        last_name: 'User'
    }));
  });
});
