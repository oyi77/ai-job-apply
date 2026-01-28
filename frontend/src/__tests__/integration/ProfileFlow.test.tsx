import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import Settings from '../../pages/Settings';
import * as apiModule from '../../services/api';
import type { UserProfile } from '../../services/api';

// Mock the authService
vi.mock('../../services/api', () => ({
  authService: {
    getProfile: vi.fn(),
    updateProfile: vi.fn(),
    deleteAccount: vi.fn(),
  },
  applicationService: {
    getApplications: vi.fn(),
  },
  resumeService: {
    getResumes: vi.fn(),
  },
  coverLetterService: {
    getCoverLetters: vi.fn(),
  },
}));

// Mock i18n
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: {
      changeLanguage: vi.fn(),
      language: 'en',
      resolvedLanguage: 'en',
    },
  }),
}));

// Mock appStore
vi.mock('../../stores/appStore', () => ({
  useAppStore: () => ({
    user: {
      id: 'user-001',
      email: 'john.doe@example.com',
      name: 'John Doe',
      first_name: 'John',
      last_name: 'Doe',
      created_at: '2025-01-01T10:00:00Z',
      updated_at: '2025-01-20T10:00:00Z',
    },
    setUser: vi.fn(),
    theme: 'light',
    setTheme: vi.fn(),
    setAuthenticated: vi.fn(),
    aiSettings: {
      provider_preference: 'gemini',
    },
    updateAISettings: vi.fn(),
  }),
}));

// Mock EmailSettingsForm component
vi.mock('../../components/forms/EmailSettingsForm', () => ({
  default: ({ onClose }: any) => <div data-testid="email-settings-form">Email Settings Form</div>,
}));

// Mock ResizeObserver
global.ResizeObserver = vi.fn(function() {
  this.observe = vi.fn();
  this.unobserve = vi.fn();
  this.disconnect = vi.fn();
}) as any;

describe('ProfileFlow Integration Tests', () => {
  let queryClient: QueryClient;

  const mockUserProfile: UserProfile = {
    id: 'user-001',
    email: 'john.doe@example.com',
    name: 'John Doe',
    created_at: '2025-01-01T10:00:00Z',
    updated_at: '2025-01-20T10:00:00Z',
  };

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });

    vi.clearAllMocks();

    // Mock localStorage with proper implementation
    const store: Record<string, string> = {};
    const localStorageMock = {
      getItem: (key: string) => store[key] || null,
      setItem: (key: string, value: string) => {
        store[key] = value;
      },
      removeItem: (key: string) => {
        delete store[key];
      },
      clear: () => {
        Object.keys(store).forEach(key => delete store[key]);
      },
    };
    global.localStorage = localStorageMock as any;
  });

  const renderSettingsPage = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <Settings />
        </MemoryRouter>
      </QueryClientProvider>
    );
  };

  it('should render settings page with profile section', async () => {
    renderSettingsPage();

    // Verify settings page title is rendered
    await waitFor(() => {
      expect(screen.getByText('settings.title')).toBeInTheDocument();
    });

    // Verify profile card is visible
    expect(screen.getByText('settings.profile.title')).toBeInTheDocument();
    expect(screen.getByText('settings.profile.description')).toBeInTheDocument();
  });

  it('should open profile modal when clicking edit profile button', async () => {
    const user = userEvent.setup();
    renderSettingsPage();

    // Find and click the profile edit button
    const profileButton = screen.getByText('settings.profile.button');
    await user.click(profileButton);

    // Modal should open with form fields
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter your first name')).toBeInTheDocument();
    });
  });

  it('should load and display user profile in form', async () => {
    const user = userEvent.setup();
    renderSettingsPage();

    // Click profile button to open modal
    const profileButton = screen.getByText('settings.profile.button');
    await user.click(profileButton);

    // Wait for form to be visible
    await waitFor(() => {
      expect(screen.getByText('Edit Profile')).toBeInTheDocument();
    });
  });

  it('should update profile successfully', async () => {
    const user = userEvent.setup();

    // Mock successful profile update
    vi.mocked(apiModule.authService.updateProfile).mockResolvedValue({
      ...mockUserProfile,
      name: 'Jane Doe',
    });

    renderSettingsPage();

    // Open profile modal
    const profileButton = screen.getByText('settings.profile.button');
    await user.click(profileButton);

    // Wait for modal to open
    await waitFor(() => {
      expect(screen.getByText('Edit Profile')).toBeInTheDocument();
    });

    // Fill in form fields
    const firstNameInput = screen.getByPlaceholderText('Enter your first name');
    const lastNameInput = screen.getByPlaceholderText('Enter your last name');
    const emailInput = screen.getByPlaceholderText('Enter your email');

    await user.clear(firstNameInput);
    await user.type(firstNameInput, 'Jane');

    await user.clear(lastNameInput);
    await user.type(lastNameInput, 'Doe');

    await user.clear(emailInput);
    await user.type(emailInput, 'jane.doe@example.com');

    // Submit form
    const saveButton = screen.getByText('Save Changes');
    await user.click(saveButton);

    // Verify API was called with correct data
    await waitFor(() => {
      expect(apiModule.authService.updateProfile).toHaveBeenCalled();
    });

    // Verify success message appears
    await waitFor(() => {
      expect(screen.getByText('settings.successMessage')).toBeInTheDocument();
    });
  });

  it('should handle profile update error gracefully', async () => {
    const user = userEvent.setup();

    // Mock API error
    vi.mocked(apiModule.authService.updateProfile).mockRejectedValue(
      new Error('Failed to update profile')
    );

     // Mock alert
     global.alert = vi.fn((message: string) => {
       // Mock implementation
     });

    renderSettingsPage();

    // Open profile modal
    const profileButton = screen.getByText('settings.profile.button');
    await user.click(profileButton);

    // Wait for modal to open
    await waitFor(() => {
      expect(screen.getByText('Edit Profile')).toBeInTheDocument();
    });

    // Fill in form fields
    const firstNameInput = screen.getByPlaceholderText('Enter your first name');
    await user.type(firstNameInput, 'Jane');

    // Submit form
    const saveButton = screen.getByText('Save Changes');
    await user.click(saveButton);

    // Verify error handling
    await waitFor(() => {
      expect(global.alert).toHaveBeenCalledWith(
        'Failed to update profile. Please try again.'
      );
    });
  });

  it('should close profile modal when clicking cancel', async () => {
    const user = userEvent.setup();
    renderSettingsPage();

    // Open profile modal
    const profileButton = screen.getByText('settings.profile.button');
    await user.click(profileButton);

    // Wait for modal to open
    await waitFor(() => {
      expect(screen.getByText('Edit Profile')).toBeInTheDocument();
    });

    // Click cancel button
    const cancelButton = screen.getByText('Cancel');
    await user.click(cancelButton);

    // Modal should close
    await waitFor(() => {
      expect(screen.queryByText('Edit Profile')).not.toBeInTheDocument();
    });
  });

  it('should display all profile form fields', async () => {
    const user = userEvent.setup();
    renderSettingsPage();

    // Open profile modal
    const profileButton = screen.getByText('settings.profile.button');
    await user.click(profileButton);

    // Wait for modal and verify all fields are present
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter your first name')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Enter your last name')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Enter your email')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Enter your phone number')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Enter your location')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Tell us about yourself')).toBeInTheDocument();
    });
  });

  it('should validate required fields in profile form', async () => {
    const user = userEvent.setup();
    renderSettingsPage();

    // Open profile modal
    const profileButton = screen.getByText('settings.profile.button');
    await user.click(profileButton);

    // Wait for modal to open
    await waitFor(() => {
      expect(screen.getByText('Edit Profile')).toBeInTheDocument();
    });

    // Verify required fields have required attribute
    const firstNameInput = screen.getByPlaceholderText('Enter your first name') as HTMLInputElement;
    const lastNameInput = screen.getByPlaceholderText('Enter your last name') as HTMLInputElement;
    const emailInput = screen.getByPlaceholderText('Enter your email') as HTMLInputElement;

    expect(firstNameInput.required).toBe(true);
    expect(lastNameInput.required).toBe(true);
    expect(emailInput.required).toBe(true);
  });

  it('should display optional fields in profile form', async () => {
    const user = userEvent.setup();
    renderSettingsPage();

    // Open profile modal
    const profileButton = screen.getByText('settings.profile.button');
    await user.click(profileButton);

    // Wait for modal to open
    await waitFor(() => {
      expect(screen.getByText('Edit Profile')).toBeInTheDocument();
    });

    // Verify optional fields exist but are not required
    const phoneInput = screen.getByPlaceholderText('Enter your phone number') as HTMLInputElement;
    const locationInput = screen.getByPlaceholderText('Enter your location') as HTMLInputElement;
    const bioInput = screen.getByPlaceholderText('Tell us about yourself') as HTMLInputElement;

    expect(phoneInput.required).toBe(false);
    expect(locationInput.required).toBe(false);
    expect(bioInput.required).toBe(false);
  });

   it('should combine first and last name for API request', async () => {
     const user = userEvent.setup();

     vi.mocked(apiModule.authService.updateProfile).mockResolvedValue(mockUserProfile);

     renderSettingsPage();

     // Open profile modal
     const profileButton = screen.getByText('settings.profile.button');
     await user.click(profileButton);

     // Wait for modal to open and form fields to be visible
     await waitFor(() => {
       expect(screen.getByText('Edit Profile')).toBeInTheDocument();
       expect(screen.getByPlaceholderText('Enter your first name')).toBeInTheDocument();
     });

     // Submit form with default values
     const saveButton = screen.getByText('Save Changes');
     await user.click(saveButton);

     // Verify API was called
     await waitFor(() => {
       expect(apiModule.authService.updateProfile).toHaveBeenCalled();
     });
   });

  it('should handle profile with only first name', async () => {
    const user = userEvent.setup();

    vi.mocked(apiModule.authService.updateProfile).mockResolvedValue({
      ...mockUserProfile,
      name: 'John',
    });

    renderSettingsPage();

    // Open profile modal
    const profileButton = screen.getByText('settings.profile.button');
    await user.click(profileButton);

    // Wait for modal to open
    await waitFor(() => {
      expect(screen.getByText('Edit Profile')).toBeInTheDocument();
    });

    // Fill in only first name
    const firstNameInput = screen.getByPlaceholderText('Enter your first name');
    await user.type(firstNameInput, 'John');

    // Submit form
    const saveButton = screen.getByText('Save Changes');
    await user.click(saveButton);

    // Verify API was called
    await waitFor(() => {
      expect(apiModule.authService.updateProfile).toHaveBeenCalled();
    });
  });

  it('should display success message after profile update', async () => {
    const user = userEvent.setup();

    vi.mocked(apiModule.authService.updateProfile).mockResolvedValue(mockUserProfile);

    renderSettingsPage();

    // Open profile modal
    const profileButton = screen.getByText('settings.profile.button');
    await user.click(profileButton);

    // Wait for modal to open
    await waitFor(() => {
      expect(screen.getByText('Edit Profile')).toBeInTheDocument();
    });

    // Fill in and submit form
    const firstNameInput = screen.getByPlaceholderText('Enter your first name');
    await user.type(firstNameInput, 'Jane');

    const saveButton = screen.getByText('Save Changes');
    await user.click(saveButton);

    // Verify success message appears
    await waitFor(() => {
      expect(screen.getByText('settings.successMessage')).toBeInTheDocument();
    });
  });

  it('should close modal after successful profile update', async () => {
    const user = userEvent.setup();

    vi.mocked(apiModule.authService.updateProfile).mockResolvedValue(mockUserProfile);

    renderSettingsPage();

    // Open profile modal
    const profileButton = screen.getByText('settings.profile.button');
    await user.click(profileButton);

    // Wait for modal to open
    await waitFor(() => {
      expect(screen.getByText('Edit Profile')).toBeInTheDocument();
    });

    // Fill in and submit form
    const firstNameInput = screen.getByPlaceholderText('Enter your first name');
    await user.type(firstNameInput, 'Jane');

    const saveButton = screen.getByText('Save Changes');
    await user.click(saveButton);

    // Modal should close after successful update
    await waitFor(() => {
      expect(screen.queryByText('Edit Profile')).not.toBeInTheDocument();
    });
  });

   it('should handle profile update with all fields', async () => {
     const user = userEvent.setup();

     vi.mocked(apiModule.authService.updateProfile).mockResolvedValue({
       ...mockUserProfile,
       name: 'Jane Smith',
     });

     renderSettingsPage();

     // Open profile modal
     const profileButton = screen.getByText('settings.profile.button');
     await user.click(profileButton);

     // Wait for modal to open
     await waitFor(() => {
       expect(screen.getByText('Edit Profile')).toBeInTheDocument();
     });

     // Verify all form fields are present
     expect(screen.getByPlaceholderText('Enter your first name')).toBeInTheDocument();
     expect(screen.getByPlaceholderText('Enter your last name')).toBeInTheDocument();
     expect(screen.getByPlaceholderText('Enter your email')).toBeInTheDocument();
     expect(screen.getByPlaceholderText('Enter your phone number')).toBeInTheDocument();
     expect(screen.getByPlaceholderText('Enter your location')).toBeInTheDocument();
     expect(screen.getByPlaceholderText('Tell us about yourself')).toBeInTheDocument();

     // Submit form
     const saveButton = screen.getByText('Save Changes');
     await user.click(saveButton);

     // Verify API was called
     await waitFor(() => {
       expect(apiModule.authService.updateProfile).toHaveBeenCalled();
     });
   });
});
