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
  const { data: stats, isLoading: statsLoading, error: statsError } = useQuery({
    queryKey: ['application-stats'],
    queryFn: applicationService.getStats,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
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
    <div className="space-y-8 animate-fade-in">
      {/* Page header */}
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
        <div className="animate-slide-up">
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Dashboard</h1>
          <p className="mt-2 text-gray-600 font-medium">
            Welcome back! Here's your job search intelligence overview.
          </p>
        </div>
        <div className="flex items-center space-x-2 animate-slide-up" style={{ animationDelay: '100ms' }}>
          <Badge variant="info" className="px-3 py-1 text-xs">
            System Active
          </Badge>
          <span className="text-xs text-gray-400 font-medium">Last updated: Just now</span>
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="animate-slide-up" style={{ animationDelay: '150ms' }}>
          <Card className="hover:shadow-2xl hover:-translate-y-1 transition-all duration-500">
            <CardBody className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 p-3 bg-primary-50 rounded-2xl">
                  <BriefcaseIcon className="h-7 w-7 text-primary-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Total Applications</p>
                  <p className="text-3xl font-bold text-gray-900">{totalApplications}</p>
                </div>
              </div>
            </CardBody>
          </Card>
        </div>

        <div className="animate-slide-up" style={{ animationDelay: '200ms' }}>
          <Card className="hover:shadow-2xl hover:-translate-y-1 transition-all duration-500">
            <CardBody className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 p-3 bg-success-50 rounded-2xl">
                  <DocumentTextIcon className="h-7 w-7 text-success-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Resumes</p>
                  <p className="text-3xl font-bold text-gray-900">{totalResumes}</p>
                </div>
              </div>
            </CardBody>
          </Card>
        </div>

        <div className="animate-slide-up" style={{ animationDelay: '250ms' }}>
          <Card className="hover:shadow-2xl hover:-translate-y-1 transition-all duration-500">
            <CardBody className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 p-3 bg-warning-50 rounded-2xl">
                  <EnvelopeIcon className="h-7 w-7 text-warning-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Cover Letters</p>
                  <p className="text-3xl font-bold text-gray-900">{totalCoverLetters}</p>
                </div>
              </div>
            </CardBody>
          </Card>
        </div>

        <div className="animate-slide-up" style={{ animationDelay: '300ms' }}>
          <Card className="hover:shadow-2xl hover:-translate-y-1 transition-all duration-500">
            <CardBody className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 p-3 bg-info-50 rounded-2xl">
                  <ChartBarIcon className="h-7 w-7 text-info-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Success Rate</p>
                  <p className="text-3xl font-bold text-gray-900">
                    {statsLoading ? '...' : statsError ? 'N/A' : `${(stats as any)?.success_rate || 0}%`}
                  </p>
                </div>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent applications */}
        <div className="lg:col-span-2 animate-slide-up" style={{ animationDelay: '350ms' }}>
          <Card className="h-full">
            <CardHeader className="flex items-center justify-between border-gray-50">
              <h3 className="text-xl font-bold text-gray-900">Recent Applications</h3>
              <button className="text-sm font-semibold text-primary-600 hover:text-primary-700 transition-colors">View all</button>
            </CardHeader>
            <CardBody>
              {recentApplications.length === 0 ? (
                <div className="text-center py-16">
                  <div className="inline-flex items-center justify-center p-4 bg-gray-50 rounded-full mb-4">
                    <BriefcaseIcon className="h-10 w-12 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-bold text-gray-900">No applications yet</h3>
                  <p className="mt-1 text-gray-500">
                    Get started by creating your first job application.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {recentApplications.map((application: any, index: number) => (
                    <div
                      key={application.id}
                      className="group flex items-center justify-between p-5 border border-gray-100 rounded-2xl hover:border-primary-100 hover:bg-primary-50/10 transition-all duration-300"
                    >
                      <div className="flex items-center space-x-5">
                        <div className="flex-shrink-0 p-3 bg-white rounded-xl shadow-sm group-hover:shadow-md transition-all">
                          {getStatusIcon(application.status)}
                        </div>
                        <div>
                          <h4 className="text-base font-bold text-gray-900 group-hover:text-primary-700 transition-colors">
                            {application.job_title}
                          </h4>
                          <div className="flex items-center mt-1 space-x-2 text-sm text-gray-500">
                            <span className="font-medium">{application.company}</span>
                            <span>&bull;</span>
                            <span>{new Date(application.applied_date).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <Badge variant={getStatusColor(application.status)} size="md">
                          {application.status.replace('_', ' ')}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardBody>
          </Card>
        </div>

        {/* Quick actions */}
        <div className="animate-slide-up" style={{ animationDelay: '400ms' }}>
          <Card className="h-full">
            <CardHeader className="border-gray-50">
              <h3 className="text-xl font-bold text-gray-900">Quick Actions</h3>
            </CardHeader>
            <CardBody>
              <div className="grid grid-cols-2 gap-4">
                <button className="flex flex-col items-center justify-center p-6 bg-primary-50/50 border border-primary-100 rounded-2xl hover:bg-primary-50 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 group">
                  <div className="p-3 bg-primary-600 rounded-xl mb-3 shadow-primary-600/20 group-hover:scale-110 transition-transform">
                    <BriefcaseIcon className="h-6 w-6 text-white" />
                  </div>
                  <span className="text-xs font-bold text-gray-900 text-center">New Application</span>
                </button>
                <button className="flex flex-col items-center justify-center p-6 bg-success-50/50 border border-success-100 rounded-2xl hover:bg-success-50 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 group">
                  <div className="p-3 bg-success-600 rounded-xl mb-3 shadow-success-600/20 group-hover:scale-110 transition-transform">
                    <DocumentTextIcon className="h-6 w-6 text-white" />
                  </div>
                  <span className="text-xs font-bold text-gray-900 text-center">Upload Resume</span>
                </button>
                <button className="flex flex-col items-center justify-center p-6 bg-warning-50/50 border border-warning-100 rounded-2xl hover:bg-warning-50 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 group">
                  <div className="p-3 bg-warning-600 rounded-xl mb-3 shadow-warning-600/20 group-hover:scale-110 transition-transform">
                    <EnvelopeIcon className="h-6 w-6 text-white" />
                  </div>
                  <span className="text-xs font-bold text-gray-900 text-center">Generate Cover Letter</span>
                </button>
                <button className="flex flex-col items-center justify-center p-6 bg-info-50/50 border border-info-100 rounded-2xl hover:bg-info-50 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 group">
                  <div className="p-3 bg-info-600 rounded-xl mb-3 shadow-info-600/20 group-hover:scale-110 transition-transform">
                    <MagnifyingGlassIcon className="h-6 w-6 text-white" />
                  </div>
                  <span className="text-xs font-bold text-gray-900 text-center">Search Jobs</span>
                </button>
              </div>

              <div className="mt-8 p-6 glass rounded-2xl border-primary-50 bg-gradient-to-br from-primary-50 to-white">
                <h4 className="text-sm font-bold text-primary-900">Pro Tip</h4>
                <p className="mt-2 text-xs text-primary-700 leading-relaxed font-medium">
                  Use the AI Optimization tool to tailor your resume for specific job descriptions and increase your response rate by up to 60%.
                </p>
                <button className="mt-4 text-xs font-bold text-primary-600 underline">Get Started &rarr;</button>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
