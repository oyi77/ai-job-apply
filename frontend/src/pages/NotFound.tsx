import React from 'react';
import { Link } from 'react-router-dom';
import Button from '../components/ui/Button';

const NotFound: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full text-center">
        <div className="mx-auto h-24 w-24 bg-gray-200 rounded-full flex items-center justify-center mb-6">
          <span className="text-4xl font-bold text-gray-400">404</span>
        </div>
        
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Page not found</h1>
        <p className="text-gray-600 mb-8">
          Sorry, we couldn't find the page you're looking for. It might have been moved, deleted, or you entered the wrong URL.
        </p>
        
        <div className="space-y-4">
          <Link to="/">
            <Button variant="primary" className="w-full">
              Go back to Dashboard
            </Button>
          </Link>
          
          <Link to="/applications">
            <Button variant="secondary" className="w-full">
              View Applications
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
