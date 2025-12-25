import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import Settings from '../Settings';
import { useAppStore } from '../../stores/appStore';
import { useTranslation } from 'react-i18next';

// Mock dependencies
vi.mock('react-router-dom', () => ({
  useNavigate: () => vi.fn(),
}));

vi.mock('../../stores/appStore', () => ({
  useAppStore: vi.fn(),
}));

// Mock i18next
vi.mock('react-i18next', () => ({
  useTranslation: vi.fn(),
}));

// Mock api services
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
}));

describe('Settings Page', () => {
  const mockSetTheme = vi.fn();
  const mockSetUser = vi.fn();
  const mockUpdateAISettings = vi.fn();
  const mockChangeLanguage = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();

    (useAppStore as any).mockReturnValue({
      user: { name: 'Test User', email: 'test@example.com' },
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

  it('renders settings page correctly', () => {
    render(<Settings />);
    expect(screen.getByText('Settings')).toBeInTheDocument();
    expect(screen.getByText('Manage your account preferences and application settings.')).toBeInTheDocument();
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
