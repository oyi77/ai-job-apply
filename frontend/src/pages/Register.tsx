import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Card, CardBody } from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import { authService } from '../services/api';
import { useAppStore } from '../stores/appStore';
import { useNotifications } from '../components/ui/Notification';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const { setUser, setAuthenticated } = useAppStore();
  const { showSuccess, showError } = useNotifications();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = 'Password must contain uppercase, lowercase, and a number';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      const tokens = await authService.register({
        email: formData.email,
        password: formData.password,
        name: formData.name || undefined,
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
        },
        created_at: userProfile.created_at,
        updated_at: userProfile.updated_at,
      };

      setUser(user);
      setAuthenticated(true);

      showSuccess('Registration successful!', 'Welcome to AI Job Application Assistant');
      
      // Redirect to dashboard
      navigate('/');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Registration failed. Please try again.';
      showError('Registration failed', errorMessage);
      setErrors({ submit: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 bg-primary-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xl">AI</span>
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            AI Job Application Assistant
          </p>
        </div>
        
        <Card>
          <CardBody className="p-6">
            <form className="space-y-6" onSubmit={handleSubmit}>
              {errors.submit && (
                <div className="bg-danger-50 border border-danger-200 text-danger-700 px-4 py-3 rounded-md">
                  {errors.submit}
                </div>
              )}
              
              <Input
                name="name"
                label="Full Name (Optional)"
                type="text"
                placeholder="Enter your name"
                value={formData.name}
                onChange={(value: string) => handleInputChange('name', value)}
                error={errors.name}
              />
              
              <Input
                name="email"
                label="Email address"
                type="email"
                placeholder="Enter your email"
                value={formData.email}
                onChange={(value: string) => handleInputChange('email', value)}
                required
                error={errors.email}
              />
              
              <Input
                name="password"
                label="Password"
                type="password"
                placeholder="Enter your password"
                value={formData.password}
                onChange={(value: string) => handleInputChange('password', value)}
                required
                error={errors.password}
                helpText="Must be at least 8 characters with uppercase, lowercase, and a number"
              />
              
              <Input
                name="confirmPassword"
                label="Confirm Password"
                type="password"
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onChange={(value: string) => handleInputChange('confirmPassword', value)}
                required
                error={errors.confirmPassword}
              />
              
              <div>
                <Button
                  type="submit"
                  variant="primary"
                  loading={loading}
                  className="w-full"
                >
                  Create Account
                </Button>
              </div>
              
              <div className="text-center">
                <p className="text-sm text-gray-600">
                  Already have an account?{' '}
                  <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">
                    Sign in
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

export default Register;

