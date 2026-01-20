import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Badge,
  Modal,
  Form,
  FormField,
  Select,
  Input,
  Alert,
  Spinner
} from '../components';
import EmailSettingsForm from '../components/forms/EmailSettingsForm';
import { useAppStore } from '../stores/appStore';
import { applicationService, resumeService, coverLetterService, authService } from '../services/api';
import {
  UserCircleIcon,
  BellIcon,
  ShieldCheckIcon,
  PaintBrushIcon,
  GlobeAltIcon,
  DocumentArrowDownIcon,
  TrashIcon,
  Cog6ToothIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';

const Settings: React.FC = () => {
  const { t, i18n } = useTranslation();
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [isNotificationsModalOpen, setIsNotificationsModalOpen] = useState(false);
  const [isPrivacyModalOpen, setIsPrivacyModalOpen] = useState(false);
  const [isThemeModalOpen, setIsThemeModalOpen] = useState(false);
  const [isLanguageModalOpen, setIsLanguageModalOpen] = useState(false);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isAIModalOpen, setIsAIModalOpen] = useState(false);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState('');
  const [deletePassword, setDeletePassword] = useState('');

  const { user, setUser, theme, setTheme, setAuthenticated, aiSettings, updateAISettings } = useAppStore();

  const handleLanguageChange = (language: string) => {
    i18n.changeLanguage(language);
    setIsLanguageModalOpen(false);
  };

  // Calculate default form values from user state
  const getProfileDefaultValues = () => {
    if (!user) return {};

    // If we have first/last name explicitly, use them
    if (user.first_name || user.last_name) {
      return {
        ...user,
        first_name: user.first_name || '',
        last_name: user.last_name || '',
      };
    }

    // Otherwise try to split the name field
    const nameParts = (user.name || '').split(' ');
    const firstName = nameParts[0] || '';
    const lastName = nameParts.slice(1).join(' ') || '';

    return {
      ...user,
      first_name: firstName,
      last_name: lastName,
    };
  };

  const handleProfileUpdate = async (data: any) => {
    try {
      // Prepare data for API (combine first and last name for backend 'name' field)
      const apiData = {
        ...data,
        name: `${data.first_name} ${data.last_name}`.trim(),
      };

      // Update user profile via API
      const updatedProfile = await authService.updateProfile(apiData);

      // Update local user state
      // We merge: existing user state + form data (to keep fields backend might ignore) + API response
      setUser({ ...user, ...data, ...updatedProfile });

      setIsProfileModalOpen(false);
      setShowSuccessMessage(true);
      setTimeout(() => setShowSuccessMessage(false), 3000);
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('Failed to update profile. Please try again.');
    }
  };

  const handleThemeChange = (newTheme: string) => {
    setTheme(newTheme as 'light' | 'dark' | 'system');
    setIsThemeModalOpen(false);
  };

  const handleExportData = async () => {
    setIsExporting(true);
    try {
      // Fetch all data from API
      const [applications, resumes, coverLetters] = await Promise.all([
        applicationService.getApplications().catch(() => ({ data: [], total: 0 })),
        resumeService.getResumes().catch(() => []),
        coverLetterService.getCoverLetters().catch(() => [])
      ]);

      const exportData = {
        user: user,
        applications: applications.data || applications,
        resumes: resumes,
        coverLetters: coverLetters,
        settings: {
          theme: theme,
        },
        exportDate: new Date().toISOString(),
        version: '1.0.0'
      };

      // Create and download JSON file
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ai-job-apply-data-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      setIsExportModalOpen(false);
      setShowSuccessMessage(true);
      setTimeout(() => setShowSuccessMessage(false), 3000);
    } catch (error) {
      console.error('Error exporting data:', error);
      alert('Failed to export data. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirmation !== 'DELETE') {
      alert('Please type DELETE to confirm account deletion');
      return;
    }

    if (!deletePassword) {
      alert('Please enter your password to confirm account deletion');
      return;
    }

    setIsDeleting(true);
    try {
      // Call API endpoint for account deletion
      await authService.deleteAccount();

      // Clear local data
      setAuthenticated(false);
      setUser(null);
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('token');
      setIsDeleteModalOpen(false);
      setDeleteConfirmation('');
      setDeletePassword('');
      
      // Redirect to login
      window.location.href = '/login';
    } catch (error: any) {
      console.error('Error deleting account:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'Failed to delete account. Please try again.';
      alert(errorMessage);
    } finally {
      setIsDeleting(false);
    }
  };

  const themeOptions = [
    { value: 'light', label: 'Light' },
    { value: 'dark', label: 'Dark' },
    { value: 'system', label: 'System Default' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">{t('settings.title')}</h1>
        <p className="mt-2 text-gray-600">
          {t('settings.description')}
        </p>
      </div>

      {/* Success Message */}
      {showSuccessMessage && (
        <Alert type="success" message={t('settings.successMessage')} />
      )}

      {/* Settings Grid */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Profile Settings */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <UserCircleIcon className="h-6 w-6 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">{t('settings.profile.title')}</h3>
            </div>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              {t('settings.profile.description')}
            </p>
            <Button
              variant="primary"
              onClick={() => setIsProfileModalOpen(true)}
              className="w-full"
            >
              {t('settings.profile.button')}
            </Button>
          </CardBody>
        </Card>

        {/* Notification Settings */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <BellIcon className="h-6 w-6 text-success-600" />
              <h3 className="text-lg font-medium text-gray-900">{t('settings.notifications.title')}</h3>
            </div>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              {t('settings.notifications.description')}
            </p>
            <Button
              variant="success"
              onClick={() => setIsNotificationsModalOpen(true)}
              className="w-full"
            >
              {t('settings.notifications.button')}
            </Button>
          </CardBody>
        </Card>

        {/* Privacy & Security */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <ShieldCheckIcon className="h-6 w-6 text-warning-600" />
              <h3 className="text-lg font-medium text-gray-900">{t('settings.privacy.title')}</h3>
            </div>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              {t('settings.privacy.description')}
            </p>
            <Button
              variant="warning"
              onClick={() => setIsPrivacyModalOpen(true)}
              className="w-full"
            >
              {t('settings.privacy.button')}
            </Button>
          </CardBody>
        </Card>

        {/* Theme & Appearance */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <PaintBrushIcon className="h-6 w-6 text-info-600" />
              <h3 className="text-lg font-medium text-gray-900">{t('settings.theme.title')}</h3>
            </div>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              {t('settings.theme.description')}
            </p>
            <div className="flex items-center space-x-2 mb-3">
              <span className="text-sm text-gray-600">{t('settings.theme.current')}</span>
              <Badge variant="secondary" size="sm">
                {theme.charAt(0).toUpperCase() + theme.slice(1)}
              </Badge>
            </div>
            <Button
              variant="info"
              onClick={() => setIsThemeModalOpen(true)}
              className="w-full"
            >
              {t('settings.theme.button')}
            </Button>
          </CardBody>
        </Card>

        {/* Language & Region */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <GlobeAltIcon className="h-6 w-6 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">{t('settings.language.title')}</h3>
            </div>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              {t('settings.language.description')}
            </p>
            <div className="flex items-center space-x-2 mb-3">
              <span className="text-sm text-gray-600">{t('settings.language.current')}</span>
              <Badge variant="secondary" size="sm">
                {i18n.resolvedLanguage?.startsWith('es') ? 'Español' : 'English'}
              </Badge>
            </div>
            <Button
              variant="secondary"
              onClick={() => setIsLanguageModalOpen(true)}
              className="w-full"
            >
              {t('settings.language.button')}
            </Button>
          </CardBody>
        </Card>

        {/* Data Management */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <DocumentArrowDownIcon className="h-6 w-6 text-success-600" />
              <h3 className="text-lg font-medium text-gray-900">{t('settings.data.title')}</h3>
            </div>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              {t('settings.data.description')}
            </p>
            <div className="space-y-2">
              <Button
                variant="success"
                onClick={() => setIsExportModalOpen(true)}
                className="w-full"
              >
                {t('settings.data.buttonExport')}
              </Button>
              <Button
                variant="danger"
                onClick={() => setIsDeleteModalOpen(true)}
                className="w-full"
              >
                <TrashIcon className="h-4 w-4 mr-2" />
                {t('settings.data.buttonDelete')}
              </Button>
            </div>
          </CardBody>
        </Card>

        {/* AI Intelligence */}
        <Card className="hover:shadow-lg transition-shadow border-primary-100 bg-primary-50/10">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <SparklesIcon className="h-6 w-6 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">{t('settings.ai.title')}</h3>
            </div>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              {t('settings.ai.description')}
            </p>
            <div className="flex items-center space-x-2 mb-3">
              <span className="text-sm text-gray-600">{t('settings.ai.activeProvider')}</span>
              <Badge variant="primary" size="sm">
                {aiSettings.provider_preference === 'openai' ? 'OpenAI' 
                  : aiSettings.provider_preference === 'openrouter' ? 'OpenRouter'
                  : aiSettings.provider_preference === 'gemini' ? 'Gemini'
                  : aiSettings.provider_preference === 'cursor' ? 'Cursor'
                  : 'Local AI'}
              </Badge>
            </div>
            <Button
              variant="primary"
              onClick={() => setIsAIModalOpen(true)}
              className="w-full"
            >
              {t('settings.ai.button')}
            </Button>
          </CardBody>
        </Card>
      </div>

      {/* Profile Modal */}
      <Modal
        isOpen={isProfileModalOpen}
        onClose={() => setIsProfileModalOpen(false)}
        title="Edit Profile"
        size="lg"
      >
        <Form
          onSubmit={handleProfileUpdate}
          defaultValues={getProfileDefaultValues()}
        >
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                name="first_name"
                label="First Name"
                placeholder="Enter your first name"
                required
              />
              <FormField
                name="last_name"
                label="Last Name"
                placeholder="Enter your last name"
                required
              />
            </div>
            <FormField
              name="email"
              label="Email"
              type="email"
              placeholder="Enter your email"
              required
            />
            <FormField
              name="phone"
              label="Phone"
              placeholder="Enter your phone number"
            />
            <FormField
              name="location"
              label="Location"
              placeholder="Enter your location"
            />
            <FormField
              name="bio"
              label="Bio"
              type="textarea"
              placeholder="Tell us about yourself"
            />
          </div>

          <div className="flex justify-end space-x-3 mt-6">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsProfileModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary">
              Save Changes
            </Button>
          </div>
        </Form>
      </Modal>

      {/* Notifications Modal */}
      <Modal
        isOpen={isNotificationsModalOpen}
        onClose={() => setIsNotificationsModalOpen(false)}
        title="Notification Preferences"
        size="lg"
      >
        <EmailSettingsForm onClose={() => setIsNotificationsModalOpen(false)} />
      </Modal>

      {/* Privacy Modal */}
      <Modal
        isOpen={isPrivacyModalOpen}
        onClose={() => setIsPrivacyModalOpen(false)}
        title="Privacy & Security Settings"
        size="lg"
      >
        <div className="space-y-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-gray-900">Profile Visibility</h4>
                <p className="text-sm text-gray-600">Control who can see your profile information</p>
              </div>
              <Select
                name="profile_visibility"
                value="private"
                onChange={() => { }}
                options={[
                  { value: 'public', label: 'Public' },
                  { value: 'private', label: 'Private' },
                  { value: 'connections', label: 'Connections Only' },
                ]}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-gray-900">Data Sharing</h4>
                <p className="text-sm text-gray-600">Allow data to be used for job matching</p>
              </div>
              <input type="checkbox" className="rounded border-gray-300 text-primary-600 focus:ring-primary-500" defaultChecked />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-gray-900">Two-Factor Authentication</h4>
                <p className="text-sm text-gray-600">Add an extra layer of security to your account</p>
              </div>
              <Button variant="secondary" size="sm">
                Enable
              </Button>
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <Button
              variant="secondary"
              onClick={() => setIsPrivacyModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={() => {
                setIsPrivacyModalOpen(false);
                setShowSuccessMessage(true);
                setTimeout(() => setShowSuccessMessage(false), 3000);
              }}
            >
              Save Settings
            </Button>
          </div>
        </div>
      </Modal>

      {/* Theme Modal */}
      <Modal
        isOpen={isThemeModalOpen}
        onClose={() => setIsThemeModalOpen(false)}
        title="Theme & Appearance"
        size="md"
      >
        <div className="space-y-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Choose Theme
              </label>
              <div className="space-y-3">
                {themeOptions.map((option) => (
                  <div
                    key={option.value}
                    className={`flex items-center p-3 border rounded-lg cursor-pointer transition-colors ${theme === option.value
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                      }`}
                    onClick={() => handleThemeChange(option.value)}
                  >
                    <input
                      type="radio"
                      name="theme"
                      value={option.value}
                      checked={theme === option.value}
                      onChange={() => handleThemeChange(option.value)}
                      className="mr-3"
                    />
                    <span className="font-medium text-gray-900">{option.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <Button
              variant="secondary"
              onClick={() => setIsThemeModalOpen(false)}
            >
              {t('common.close')}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Language Modal */}
      <Modal
        isOpen={isLanguageModalOpen}
        onClose={() => setIsLanguageModalOpen(false)}
        title={t('settings.language.title')}
        size="md"
      >
        <div className="space-y-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Choose Language
              </label>
              <div className="space-y-3">
                {[
                  { value: 'en', label: 'English' },
                  { value: 'es', label: 'Español' },
                ].map((option) => (
                  <div
                    key={option.value}
                    className={`flex items-center p-3 border rounded-lg cursor-pointer transition-colors ${i18n.language === option.value
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                      }`}
                    onClick={() => handleLanguageChange(option.value)}
                  >
                    <input
                      type="radio"
                      name="language"
                      value={option.value}
                      checked={i18n.language === option.value}
                      onChange={() => handleLanguageChange(option.value)}
                      className="mr-3"
                    />
                    <span className="font-medium text-gray-900">{option.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <Button
              variant="secondary"
              onClick={() => setIsLanguageModalOpen(false)}
            >
              {t('common.close')}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Export Modal */}
      <Modal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        title="Export Your Data"
        size="md"
      >
        <div className="space-y-6">
          <div className="text-center">
            <DocumentArrowDownIcon className="mx-auto h-12 w-12 text-success-600 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Export Your Data
            </h3>
            <p className="text-gray-600">
              Download a copy of all your data including applications, resumes, and settings.
            </p>
          </div>

          <div className="flex justify-end space-x-3">
            <Button
              variant="secondary"
              onClick={() => setIsExportModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="success"
              onClick={handleExportData}
              disabled={isExporting}
            >
              {isExporting ? (
                <>
                  <Spinner size="sm" className="mr-2" />
                  Exporting...
                </>
              ) : (
                <>
                  <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
                  Export Data
                </>
              )}
            </Button>
          </div>
        </div>
      </Modal>

      {/* AI Intelligence Modal */}
      <Modal
        isOpen={isAIModalOpen}
        onClose={() => setIsAIModalOpen(false)}
        title="AI Intelligence Settings"
        size="lg"
      >
        <div className="space-y-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Preferred AI Provider
              </label>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-3 lg:grid-cols-5">
                {[
                  { id: 'openai', name: 'OpenAI', description: 'GPT-4o, GPT-4' },
                  { id: 'openrouter', name: 'OpenRouter', description: 'Claude, Llama, etc.' },
                  { id: 'gemini', name: 'Gemini', description: 'Gemini 1.5 Flash' },
                  { id: 'cursor', name: 'Cursor', description: 'Cursor AI' },
                  { id: 'local_ai', name: 'Local AI', description: 'Ollama, Localhost' }
                ].map((provider) => (
                  <div
                    key={provider.id}
                    onClick={() => updateAISettings({ provider_preference: provider.id as any })}
                    className={`flex flex-col p-3 border rounded-lg cursor-pointer transition-all ${aiSettings.provider_preference === provider.id
                      ? 'border-primary-500 bg-primary-50 ring-1 ring-primary-500'
                      : 'border-gray-200 hover:border-gray-300 bg-white'
                      }`}
                  >
                    <span className="font-semibold text-gray-900">{provider.name}</span>
                    <span className="text-xs text-gray-500">{provider.description}</span>
                  </div>
                ))}
              </div>
            </div>

            {aiSettings.provider_preference === 'openai' && (
              <div className="space-y-4 pt-4 border-t border-gray-100">
                <Input
                  label="OpenAI API Key"
                  name="openai_api_key"
                  type="password"
                  placeholder="sk-..."
                  value={aiSettings.openai_api_key || ''}
                  onChange={(val: string) => updateAISettings({ openai_api_key: val })}
                />
                <Input
                  label="Model Selection"
                  name="openai_model"
                  placeholder="gpt-4o"
                  value={aiSettings.openai_model || ''}
                  onChange={(val: string) => updateAISettings({ openai_model: val })}
                />
                <Input
                  label="Custom Base URL (Optional)"
                  name="openai_base_url"
                  placeholder="https://api.openai.com/v1"
                  value={aiSettings.openai_base_url || ''}
                  onChange={(val: string) => updateAISettings({ openai_base_url: val })}
                />
              </div>
            )}

            {aiSettings.provider_preference === 'openrouter' && (
              <div className="space-y-4 pt-4 border-t border-gray-100">
                <Input
                  label="OpenRouter API Key"
                  name="openrouter_api_key"
                  type="password"
                  placeholder="sk-or-v1-..."
                  value={aiSettings.openrouter_api_key || ''}
                  onChange={(val: string) => updateAISettings({ openrouter_api_key: val })}
                />
                <Input
                  label="Model Identifier"
                  name="openrouter_model"
                  placeholder="anthropic/claude-3.5-sonnet"
                  value={aiSettings.openrouter_model || ''}
                  onChange={(val: string) => updateAISettings({ openrouter_model: val })}
                />
                <Input
                  label="Custom Base URL"
                  name="openrouter_base_url"
                  placeholder="https://openrouter.ai/api/v1"
                  value={aiSettings.openrouter_base_url || ''}
                  onChange={(val: string) => updateAISettings({ openrouter_base_url: val })}
                />
              </div>
            )}

            {aiSettings.provider_preference === 'gemini' && (
              <div className="space-y-4 pt-4 border-t border-gray-100">
                <Input
                  label="Gemini API Key"
                  name="gemini_api_key"
                  type="password"
                  placeholder="AIza..."
                  value={aiSettings.gemini_api_key || ''}
                  onChange={(val: string) => updateAISettings({ gemini_api_key: val })}
                />
                <Input
                  label="Model Selection"
                  name="gemini_model"
                  placeholder="gemini-1.5-flash"
                  value={aiSettings.gemini_model || ''}
                  onChange={(val: string) => updateAISettings({ gemini_model: val })}
                />
              </div>
            )}

            {aiSettings.provider_preference === 'cursor' && (
              <div className="space-y-4 pt-4 border-t border-gray-100">
                <Input
                  label="Cursor API Key"
                  name="cursor_api_key"
                  type="password"
                  placeholder="key_..."
                  value={aiSettings.cursor_api_key || ''}
                  onChange={(val: string) => updateAISettings({ cursor_api_key: val })}
                />
                <Input
                  label="Model Selection"
                  name="cursor_model"
                  placeholder="gpt-4o"
                  value={aiSettings.cursor_model || ''}
                  onChange={(val: string) => updateAISettings({ cursor_model: val })}
                />
                <Input
                  label="Custom Base URL (Optional)"
                  name="cursor_base_url"
                  placeholder="https://api.cursor.sh/openai/v1"
                  value={aiSettings.cursor_base_url || ''}
                  onChange={(val: string) => updateAISettings({ cursor_base_url: val })}
                />
              </div>
            )}

            {aiSettings.provider_preference === 'local_ai' && (
              <div className="space-y-4 pt-4 border-t border-gray-100">
                <Input
                  label="Local API Endpoint"
                  name="local_base_url"
                  placeholder="http://localhost:11434/v1"
                  value={aiSettings.local_base_url || ''}
                  onChange={(val: string) => updateAISettings({ local_base_url: val })}
                />
                <Input
                  label="Local Model"
                  name="local_model"
                  placeholder="llama3"
                  value={aiSettings.local_model || ''}
                  onChange={(val: string) => updateAISettings({ local_model: val })}
                />
              </div>
            )}
          </div>

          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <Button
              variant="secondary"
              onClick={() => setIsAIModalOpen(false)}
            >
              Close
            </Button>
            <Button
              variant="primary"
              onClick={() => {
                setIsAIModalOpen(false);
                setShowSuccessMessage(true);
                setTimeout(() => setShowSuccessMessage(false), 3000);
              }}
            >
              Apply Settings
            </Button>
          </div>
        </div>
      </Modal>

      {/* Delete Account Modal */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        title="Delete Account"
        size="md"
      >
        <div className="space-y-6">
          <div className="text-center">
            <TrashIcon className="mx-auto h-12 w-12 text-danger-600 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Delete Your Account
            </h3>
            <p className="text-gray-600">
              This action cannot be undone. All your data will be permanently deleted.
            </p>
          </div>

          <div className="p-4 bg-danger-50 border border-danger-200 rounded-lg">
            <p className="text-sm text-danger-800">
              <strong>Warning:</strong> Deleting your account will remove all applications, resumes,
              cover letters, and other data permanently.
            </p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type <strong>DELETE</strong> to confirm:
              </label>
              <Input
                name="deleteConfirmation"
                type="text"
                value={deleteConfirmation}
                onChange={(val: string) => setDeleteConfirmation(val)}
                placeholder="Type DELETE to confirm"
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Enter your password to confirm:
              </label>
              <Input
                name="deletePassword"
                type="password"
                value={deletePassword}
                onChange={(val: string) => setDeletePassword(val)}
                placeholder="Enter your password"
                className="w-full"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-3">
            <Button
              variant="secondary"
              onClick={() => {
                setIsDeleteModalOpen(false);
                setDeleteConfirmation('');
                setDeletePassword('');
              }}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={handleDeleteAccount}
              disabled={isDeleting || deleteConfirmation !== 'DELETE' || !deletePassword}
            >
              {isDeleting ? (
                <>
                  <Spinner size="sm" className="mr-2" />
                  Deleting...
                </>
              ) : (
                <>
                  <TrashIcon className="h-4 w-4 mr-2" />
                  Delete Account
                </>
              )}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Settings;
