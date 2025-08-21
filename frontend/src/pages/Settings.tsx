import React, { useState } from 'react';
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
  Alert
} from '../components';
import { useAppStore } from '../stores/appStore';
import {
  UserCircleIcon,
  BellIcon,
  ShieldCheckIcon,
  PaintBrushIcon,
  GlobeAltIcon,
  DocumentArrowDownIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';

const Settings: React.FC = () => {
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [isNotificationsModalOpen, setIsNotificationsModalOpen] = useState(false);
  const [isPrivacyModalOpen, setIsPrivacyModalOpen] = useState(false);
  const [isThemeModalOpen, setIsThemeModalOpen] = useState(false);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  
  const { user, setUser, theme, setTheme, setAuthenticated } = useAppStore();

  const handleProfileUpdate = (data: { 
    name?: string; 
    email?: string; 
    phone?: string; 
    location?: string; 
    bio?: string; 
  }) => {
    // TODO: Implement profile update
    if (user) {
      setUser({ ...user, ...data });
    }
    setIsProfileModalOpen(false);
    setShowSuccessMessage(true);
    setTimeout(() => setShowSuccessMessage(false), 3000);
  };

  const handleThemeChange = (newTheme: string) => {
    setTheme(newTheme as 'light' | 'dark' | 'system');
    setIsThemeModalOpen(false);
  };

  const handleExportData = () => {
    // TODO: Implement data export
    const exportData = {
      user: user,
      timestamp: new Date().toISOString(),
    };
    
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
  };

  const handleDeleteAccount = () => {
    // TODO: Implement account deletion
    setAuthenticated(false);
    setUser(null);
    localStorage.removeItem('token');
    setIsDeleteModalOpen(false);
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
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-gray-600">
          Manage your account preferences and application settings.
        </p>
      </div>

      {/* Success Message */}
      {showSuccessMessage && (
        <Alert type="success" message="Settings updated successfully!" />
      )}

      {/* Settings Grid */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Profile Settings */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <UserCircleIcon className="h-6 w-6 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Profile</h3>
            </div>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              Update your personal information and contact details.
            </p>
            <Button
              variant="primary"
              onClick={() => setIsProfileModalOpen(true)}
              className="w-full"
            >
              Edit Profile
            </Button>
          </CardBody>
        </Card>

        {/* Notification Settings */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <BellIcon className="h-6 w-6 text-success-600" />
              <h3 className="text-lg font-medium text-gray-900">Notifications</h3>
            </div>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              Configure how and when you receive notifications.
            </p>
            <Button
              variant="success"
              onClick={() => setIsNotificationsModalOpen(true)}
              className="w-full"
            >
              Configure
            </Button>
          </CardBody>
        </Card>

        {/* Privacy & Security */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <ShieldCheckIcon className="h-6 w-6 text-warning-600" />
              <h3 className="text-lg font-medium text-gray-900">Privacy & Security</h3>
            </div>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              Manage your privacy settings and security preferences.
            </p>
            <Button
              variant="warning"
              onClick={() => setIsPrivacyModalOpen(true)}
              className="w-full"
            >
              Manage
            </Button>
          </CardBody>
        </Card>

        {/* Theme & Appearance */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <PaintBrushIcon className="h-6 w-6 text-info-600" />
              <h3 className="text-lg font-medium text-gray-900">Theme & Appearance</h3>
            </div>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              Customize the look and feel of your application.
            </p>
            <div className="flex items-center space-x-2 mb-3">
              <span className="text-sm text-gray-600">Current:</span>
              <Badge variant="secondary" size="sm">
                {theme.charAt(0).toUpperCase() + theme.slice(1)}
              </Badge>
            </div>
            <Button
              variant="info"
              onClick={() => setIsThemeModalOpen(true)}
              className="w-full"
            >
              Customize
            </Button>
          </CardBody>
        </Card>

        {/* Language & Region */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <GlobeAltIcon className="h-6 w-6 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Language & Region</h3>
            </div>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              Set your preferred language and regional settings.
            </p>
            <div className="flex items-center space-x-2 mb-3">
              <span className="text-sm text-gray-600">Current:</span>
              <Badge variant="secondary" size="sm">English</Badge>
            </div>
            <Button
              variant="secondary"
              onClick={() => {}} // TODO: Implement language selection
              className="w-full"
              disabled
            >
              Change Language
            </Button>
          </CardBody>
        </Card>

        {/* Data Management */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <DocumentArrowDownIcon className="h-6 w-6 text-success-600" />
              <h3 className="text-lg font-medium text-gray-900">Data Management</h3>
            </div>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              Export your data or manage your account information.
            </p>
            <div className="space-y-2">
              <Button
                variant="success"
                onClick={() => setIsExportModalOpen(true)}
                className="w-full"
              >
                Export Data
              </Button>
              <Button
                variant="danger"
                onClick={() => setIsDeleteModalOpen(true)}
                className="w-full"
              >
                <TrashIcon className="h-4 w-4 mr-2" />
                Delete Account
              </Button>
            </div>
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
        <Form onSubmit={handleProfileUpdate}>
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
        <div className="space-y-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-gray-900">Application Updates</h4>
                <p className="text-sm text-gray-600">Get notified when your application status changes</p>
              </div>
              <input type="checkbox" className="rounded border-gray-300 text-primary-600 focus:ring-primary-500" defaultChecked />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-gray-900">New Job Matches</h4>
                <p className="text-sm text-gray-600">Receive alerts for jobs that match your profile</p>
              </div>
              <input type="checkbox" className="rounded border-gray-300 text-primary-600 focus:ring-primary-500" defaultChecked />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-gray-900">AI Service Updates</h4>
                <p className="text-sm text-gray-600">Notifications about AI service availability</p>
              </div>
              <input type="checkbox" className="rounded border-gray-300 text-primary-600 focus:ring-primary-500" defaultChecked />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-gray-900">Weekly Reports</h4>
                <p className="text-sm text-gray-600">Get weekly summaries of your job search activity</p>
              </div>
              <input type="checkbox" className="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
            </div>
          </div>
          
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <Button
              variant="secondary"
              onClick={() => setIsNotificationsModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={() => {
                setIsNotificationsModalOpen(false);
                setShowSuccessMessage(true);
                setTimeout(() => setShowSuccessMessage(false), 3000);
              }}
            >
              Save Preferences
            </Button>
          </div>
        </div>
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
                onChange={() => {}}
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
                    className={`flex items-center p-3 border rounded-lg cursor-pointer transition-colors ${
                      theme === option.value
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
              Close
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
            >
              <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
              Export Data
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
          
          <div className="flex justify-end space-x-3">
            <Button
              variant="secondary"
              onClick={() => setIsDeleteModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={handleDeleteAccount}
            >
              <TrashIcon className="h-4 w-4 mr-2" />
              Delete Account
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Settings;
