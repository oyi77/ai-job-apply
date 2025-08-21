import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardBody } from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import { useAppStore } from '../stores/appStore';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { setUser, setAuthenticated } = useAppStore();
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
      // For demo purposes, simulate login
      // In production, this would call your authentication API
      if (formData.email && formData.password) {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Create mock user
        const mockUser = {
          id: '1',
          email: formData.email,
          name: 'Demo User',
          avatar: undefined,
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
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };

        // Store mock token
        localStorage.setItem('auth_token', 'mock-jwt-token');
        
        // Update store
        setUser(mockUser);
        setAuthenticated(true);
        
        // Redirect to dashboard
        navigate('/');
      } else {
        setError('Please enter both email and password');
      }
    } catch {
      setError('Login failed. Please try again.');
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
                  Demo credentials: Use any email and password
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
