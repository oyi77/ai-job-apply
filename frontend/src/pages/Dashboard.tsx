import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import { useAppStore } from '../stores/appStore';
import { applicationService } from '../services/api';
import {
  BriefcaseIcon,
  DocumentTextIcon,
  EnvelopeIcon,
  ChartBarIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';

const Dashboard: React.FC = () => {
  const { applications, resumes, coverLetters } = useAppStore();

  // Fetch application statistics
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['application-stats'],
    queryFn: applicationService.getStats,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const recentApplications = applications.slice(0, 5);
  const totalApplications = applications.length;
  const totalResumes = resumes.length;
  const totalCoverLetters = coverLetters.length;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'applied':
        return 'primary';
      case 'under_review':
        return 'warning';
      case 'interview_scheduled':
        return 'primary';
      case 'offer_received':
        return 'success';
      case 'rejected':
        return 'danger';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'applied':
        return <BriefcaseIcon className="h-4 w-4" />;
      case 'under_review':
        return <ClockIcon className="h-4 w-4" />;
      case 'interview_scheduled':
        return <ClockIcon className="h-4 w-4" />;
      case 'offer_received':
        return <CheckCircleIcon className="h-4 w-4" />;
      case 'rejected':
        return <XCircleIcon className="h-4 w-4" />;
      default:
        return <BriefcaseIcon className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome back! Here's an overview of your job application progress.
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardBody className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BriefcaseIcon className="h-8 w-8 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Applications</p>
                <p className="text-2xl font-semibold text-gray-900">{totalApplications}</p>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DocumentTextIcon className="h-8 w-8 text-success-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Resumes</p>
                <p className="text-2xl font-semibold text-gray-900">{totalResumes}</p>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <EnvelopeIcon className="h-8 w-8 text-warning-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Cover Letters</p>
                <p className="text-2xl font-semibold text-gray-900">{totalCoverLetters}</p>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-8 w-8 text-info-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Success Rate</p>
                <p className="text-2xl font-semibold text-gray-900">
                                     {statsLoading ? '...' : `${(stats as any)?.success_rate || 0}%`}
                </p>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Recent applications */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-medium text-gray-900">Recent Applications</h3>
        </CardHeader>
        <CardBody>
          {recentApplications.length === 0 ? (
            <div className="text-center py-8">
              <BriefcaseIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No applications yet</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by creating your first job application.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
                             {recentApplications.map((application: any) => (
                <div
                  key={application.id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                >
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      {getStatusIcon(application.status)}
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">
                        {application.job_title}
                      </h4>
                      <p className="text-sm text-gray-500">{application.company}</p>
                      <p className="text-xs text-gray-400">
                        Applied on {new Date(application.applied_date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant={getStatusColor(application.status)}>
                      {application.status.replace('_', ' ')}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardBody>
      </Card>

      {/* Quick actions */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
        </CardHeader>
        <CardBody>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <button className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-primary-300 transition-colors">
              <BriefcaseIcon className="h-8 w-8 text-primary-600 mb-2" />
              <span className="text-sm font-medium text-gray-900">New Application</span>
            </button>
            <button className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-success-300 transition-colors">
              <DocumentTextIcon className="h-8 w-8 text-success-600 mb-2" />
              <span className="text-sm font-medium text-gray-900">Upload Resume</span>
            </button>
            <button className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-warning-300 transition-colors">
              <EnvelopeIcon className="h-8 w-8 text-warning-600 mb-2" />
              <span className="text-sm font-medium text-gray-900">Generate Cover Letter</span>
            </button>
            <button className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-info-300 transition-colors">
              <MagnifyingGlassIcon className="h-8 w-8 text-info-600 mb-2" />
              <span className="text-sm font-medium text-gray-900">Search Jobs</span>
            </button>
          </div>
        </CardBody>
      </Card>
    </div>
  );
};

export default Dashboard;
