import React, { useEffect } from 'react';
import { Navigate, useLocation, Outlet } from 'react-router-dom';
import { useAppStore } from '../../stores/appStore';
import { authService } from '../../services/api';
import Spinner from '../ui/Spinner';

// ProtectedRoute doesn't need children prop when using Outlet
const ProtectedRoute: React.FC = () => {
  const { isAuthenticated, user, setUser, setAuthenticated } = useAppStore();
  const location = useLocation();
  const [loading, setLoading] = React.useState(true);
  const hasCheckedAuth = React.useRef(false);

  useEffect(() => {
    const checkAuth = async () => {
      // If we already have a user and are authenticated, skip the check
      if (isAuthenticated && user) {
        setLoading(false);
        return;
      }

      // Only check once per mount
      if (hasCheckedAuth.current) {
        setLoading(false);
        return;
      }
      hasCheckedAuth.current = true;

      try {
        // Check if we have a token in localStorage
        if (authService.isAuthenticated()) {
          // Try to get user profile to verify token is valid
          try {
            const userProfile = await authService.getProfile();
            const userData = {
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
            setUser(userData);
            setAuthenticated(true);
          } catch (error) {
            console.error('Failed to get user profile:', error);
            // Token invalid, clear auth
            await authService.logout();
            setUser(null);
            setAuthenticated(false);
          }
        } else {
          // No token, not authenticated
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
  }, [setUser, setAuthenticated]); // Removed isAuthenticated and user from deps to prevent loops

  // If we have auth state from store, use it immediately (skip loading)
  // This prevents blank page after login
  if (isAuthenticated && user) {
    return <Outlet />;
  }

  // Show loading only if we're actually checking auth
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

  // Not authenticated or no user data, redirect to login
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Fallback (should not reach here)
  return <Outlet />;
};

export default ProtectedRoute;

