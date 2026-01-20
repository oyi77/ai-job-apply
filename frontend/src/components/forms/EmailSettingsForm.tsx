import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Alert,
  Spinner,
  Select,
} from '../components';
import { notificationService, NotificationSettings, EmailTemplate } from '../services/api';
import { EnvelopeIcon, PaperAirplaneIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

interface EmailSettingsFormProps {
  onClose?: () => void;
}

const EmailSettingsForm: React.FC<EmailSettingsFormProps> = ({ onClose }) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [testEmailSent, setTestEmailSent] = useState(false);
  const [testEmail, setTestEmail] = useState('');

  const [settings, setSettings] = useState<NotificationSettings>({
    email_enabled: true,
    follow_up_reminders: true,
    interview_reminders: true,
    application_status_updates: true,
    marketing_emails: false,
  });

  // Load settings and templates on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [settingsData, templatesData] = await Promise.all([
          notificationService.getSettings().catch(() => settings),
          notificationService.getTemplates().catch(() => []),
        ]);
        setSettings(settingsData);
        setTemplates(templatesData);
      } catch (err) {
        console.error('Error loading notification settings:', err);
        setError('Failed to load notification settings');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const handleSettingChange = (key: keyof NotificationSettings, value: boolean) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      await notificationService.updateSettings(settings);
      setSuccess('Notification settings saved successfully');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      console.error('Error saving notification settings:', err);
      setError(err?.response?.data?.detail || err?.message || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleSendTestEmail = async () => {
    if (!testEmail) {
      setError('Please enter a test email address');
      return;
    }

    try {
      setError(null);
      await notificationService.sendTestEmail(testEmail);
      setTestEmailSent(true);
      setTimeout(() => setTestEmailSent(false), 3000);
    } catch (err: any) {
      console.error('Error sending test email:', err);
      setError(err?.response?.data?.detail || err?.message || 'Failed to send test email');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Success/Error Messages */}
      {success && (
        <Alert type="success" message={success} onClose={() => setSuccess(null)} />
      )}
      {error && (
        <Alert type="error" message={error} onClose={() => setError(null)} />
      )}

      {/* Email Notifications Toggle */}
      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
        <div className="flex items-center space-x-3">
          <EnvelopeIcon className="h-6 w-6 text-primary-600" />
          <div>
            <h3 className="font-medium text-gray-900">Email Notifications</h3>
            <p className="text-sm text-gray-600">Enable or disable all email notifications</p>
          </div>
        </div>
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={settings.email_enabled}
            onChange={(e) => handleSettingChange('email_enabled', e.target.checked)}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
        </label>
      </div>

      {/* Notification Preferences */}
      {settings.email_enabled && (
        <>
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">Notification Preferences</h4>

            {/* Application Status Updates */}
            <div className="flex items-center justify-between p-4 bg-white rounded-lg border border-gray-200 hover:border-gray-300 transition-colors">
              <div>
                <h5 className="font-medium text-gray-900">Application Status Updates</h5>
                <p className="text-sm text-gray-600">Get notified when your application status changes</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.application_status_updates}
                  onChange={(e) => handleSettingChange('application_status_updates', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-success-600"></div>
              </label>
            </div>

            {/* Follow-up Reminders */}
            <div className="flex items-center justify-between p-4 bg-white rounded-lg border border-gray-200 hover:border-gray-300 transition-colors">
              <div>
                <h5 className="font-medium text-gray-900">Follow-up Reminders</h5>
                <p className="text-sm text-gray-600">Receive reminders to follow up on applications</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.follow_up_reminders}
                  onChange={(e) => handleSettingChange('follow_up_reminders', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-success-600"></div>
              </label>
            </div>

            {/* Interview Reminders */}
            <div className="flex items-center justify-between p-4 bg-white rounded-lg border border-gray-200 hover:border-gray-300 transition-colors">
              <div>
                <h5 className="font-medium text-gray-900">Interview Reminders</h5>
                <p className="text-sm text-gray-600">Get notified about upcoming interviews</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.interview_reminders}
                  onChange={(e) => handleSettingChange('interview_reminders', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-success-600"></div>
              </label>
            </div>

            {/* Marketing Emails */}
            <div className="flex items-center justify-between p-4 bg-white rounded-lg border border-gray-200 hover:border-gray-300 transition-colors">
              <div>
                <h5 className="font-medium text-gray-900">Product Updates & Tips</h5>
                <p className="text-sm text-gray-600">Receive tips to improve your job search</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.marketing_emails}
                  onChange={(e) => handleSettingChange('marketing_emails', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
          </div>

          {/* Test Email Section */}
          <div className="p-4 bg-primary-50 rounded-lg border border-primary-200">
            <div className="flex items-center space-x-2 mb-3">
              <PaperAirplaneIcon className="h-5 w-5 text-primary-600" />
              <h4 className="font-medium text-primary-900">Send Test Email</h4>
            </div>
            <p className="text-sm text-primary-700 mb-4">
              Verify your email notifications are working by sending a test email.
            </p>
            <div className="flex space-x-3">
              <Input
                type="email"
                placeholder="Enter test email address"
                value={testEmail}
                onChange={(val: string) => setTestEmail(val)}
                className="flex-1"
              />
              <Button
                variant="primary"
                onClick={handleSendTestEmail}
                disabled={!testEmail}
              >
                Send Test
              </Button>
            </div>
            {testEmailSent && (
              <div className="mt-3 flex items-center text-success-600">
                <CheckCircleIcon className="h-4 w-4 mr-1" />
                <span className="text-sm">Test email sent successfully!</span>
              </div>
            )}
          </div>

          {/* Available Templates */}
          {templates.length > 0 && (
            <div className="space-y-3">
              <h4 className="font-medium text-gray-900">Available Email Templates</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {templates.map((template) => (
                  <div
                    key={template.id}
                    className="p-3 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <h5 className="font-medium text-gray-900 capitalize">
                      {template.name.replace(/_/g, ' ')}
                    </h5>
                    <p className="text-xs text-gray-600 mt-1">{template.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Action Buttons */}
      <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
        {onClose && (
          <Button variant="secondary" onClick={onClose}>
            {t('common.cancel')}
          </Button>
        )}
        <Button
          variant="primary"
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? (
            <>
              <Spinner size="sm" className="mr-2" />
              Saving...
            </>
          ) : (
            'Save Preferences'
          )}
        </Button>
      </div>
    </div>
  );
};

export default EmailSettingsForm;
