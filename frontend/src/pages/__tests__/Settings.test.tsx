import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Settings from '../Settings';
import { useAppStore } from '../../stores/appStore';
import { authService } from '../../services/api';
import { useTranslation } from 'react-i18next';

// Mock dependencies
vi.mock('react-router-dom', () => ({
  useNavigate: () => vi.fn(),
}));

// Mock the store
vi.mock('../../stores/appStore', () => ({
  useAppStore: vi.fn(),
}));

// Mock i18next
vi.mock('react-i18next', () => ({
  useTranslation: vi.fn(),
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
  const mockChangeLanguage = vi.fn();

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

    (useTranslation as any).mockReturnValue({
      t: (key: string) => {
        const translations: Record<string, string> = {
          'settings.title': 'Settings',
          'settings.description': 'Manage your account preferences and application settings.',
          'settings.language.title': 'Language & Region',
          'settings.language.description': 'Set your preferred language and regional settings.',
          'settings.language.current': 'Current:',
          'settings.language.button': 'Change Language',
          'common.close': 'Close',
        };
        return translations[key] || key;
      },
      i18n: {
        language: 'en',
        changeLanguage: mockChangeLanguage,
      },
    });
  });

  it('renders correctly', () => {
    render(<Settings />);
    expect(screen.getByText('Settings')).toBeInTheDocument();
    expect(screen.getByText('Manage your account preferences and application settings.')).toBeInTheDocument();
  });

  it('opens profile modal when Edit Profile is clicked', async () => {
    const user = userEvent.setup();
    render(<Settings />);
    // Using translation key or text if it matches translation mock
    const editButton = screen.getByText('settings.profile.button');
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
    await user.click(screen.getByText('settings.profile.button'));

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

  it('opens language modal when clicking change language button', () => {
    render(<Settings />);

    const changeLanguageBtn = screen.getByText('Change Language');
    fireEvent.click(changeLanguageBtn);

    expect(screen.getByText('Choose Language')).toBeInTheDocument();
    expect(screen.getAllByText('English')[0]).toBeInTheDocument();
    expect(screen.getByText('Español')).toBeInTheDocument();
  });

  it('calls changeLanguage when selecting a new language', () => {
    render(<Settings />);

    // Open modal
    fireEvent.click(screen.getByText('Change Language'));

    // Click Spanish option
    const spanishOption = screen.getByText('Español');
    fireEvent.click(spanishOption);

    expect(mockChangeLanguage).toHaveBeenCalledWith('es');
  });
});
