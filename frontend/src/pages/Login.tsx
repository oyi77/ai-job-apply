import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Card, CardBody } from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import { useAppStore } from '../stores/appStore';
import { authService } from '../services/api';
import { useNotifications } from '../components/ui/Notification';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { setUser, setAuthenticated } = useAppStore();
  const { showSuccess, showError } = useNotifications();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (!formData.email || !formData.password) {
        setError('Please enter both email and password');
        return;
      }

      // Call authentication API
      await authService.login({
        email: formData.email,
        password: formData.password,
      });

      // Get user profile
      const userProfile = await authService.getProfile();

      // Update store with user data
      const user = {
        id: userProfile.id,
        email: userProfile.email,
        name: userProfile.name || userProfile.email,
        preferences: {
          theme: 'system' as const,
          notifications: {
            email: true,
            push: true,
            follow_up_reminders: true,
            interview_reminders: true,
            application_updates: true,
          },
          privacy: {
            profile_visibility: 'private' as const,
            data_sharing: false,
            analytics_tracking: true,
          },
          ai: {
            provider_preference: 'openai' as const,
          },
        },
        created_at: userProfile.created_at,
        updated_at: userProfile.updated_at,
      };

      setUser(user);
      setAuthenticated(true);

      showSuccess('Login successful!', 'Welcome back');

      // Redirect to dashboard
      navigate('/', { replace: true });
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Login failed. Please try again.';
      setError(errorMessage);
      showError('Login failed', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 bg-primary-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xl">AI</span>
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            AI Job Application Assistant
          </p>
        </div>

        <Card>
          <CardBody className="p-6">
            <form className="space-y-6" onSubmit={handleSubmit}>
              {error && (
                <div className="bg-danger-50 border border-danger-200 text-danger-700 px-4 py-3 rounded-md">
                  {error}
                </div>
              )}

              <Input
                name="email"
                label="Email address"
                type="email"
                placeholder="Enter your email"
                value={formData.email}
                onChange={(value: string) => handleInputChange('email', value)}
                required
              />

              <Input
                name="password"
                label="Password"
                type="password"
                placeholder="Enter your password"
                value={formData.password}
                onChange={(value: string) => handleInputChange('password', value)}
                required
              />

              <div>
                <Button
                  type="submit"
                  variant="primary"
                  loading={loading}
                  className="w-full"
                >
                  Sign in
                </Button>
              </div>

              <div className="text-center">
                <p className="text-sm text-gray-600">
                  Don't have an account?{' '}
                  <Link to="/register" className="font-medium text-primary-600 hover:text-primary-500">
                    Sign up
                  </Link>
                </p>
              </div>
            </form>
          </CardBody>
        </Card>
      </div>
    </div>
  );
};

export default Login;
