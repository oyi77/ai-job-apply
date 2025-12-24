import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAppStore } from '../../stores/appStore';
import { authService } from '../../services/api';
import Spinner from '../ui/Spinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, setUser, setAuthenticated } = useAppStore();
  const location = useLocation();
  const [loading, setLoading] = React.useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check if we have a token
        if (authService.isAuthenticated()) {
          // Try to get user profile to verify token is valid
          try {
            const userProfile = await authService.getProfile();
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
          } catch (error) {
            // Token invalid, clear auth
            await authService.logout();
            setUser(null);
            setAuthenticated(false);
          }
        } else {
          setAuthenticated(false);
        }
      } catch (error) {
        console.error('Auth check error:', error);
        setAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [setUser, setAuthenticated]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Spinner size="lg" />
          <p className="mt-4 text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect to login with return URL
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;

