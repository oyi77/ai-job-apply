import React from 'react';
import { Navigate, useLocation, Outlet } from 'react-router-dom';
import Spinner from '../ui/Spinner';
import { useAuth } from '../../contexts/AuthContext';

// ProtectedRoute doesn't need children prop when using Outlet
const ProtectedRoute: React.FC = () => {
  const { isAuthenticated, user, isLoading } = useAuth();
  const location = useLocation();
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Spinner size="lg" />
          <p className="mt-4 text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  if (isAuthenticated && user) {
    return <Outlet />;
  }

  // Not authenticated or no user data, redirect to login
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Fallback (should not reach here)
  return <Outlet />;
};

export default ProtectedRoute;

