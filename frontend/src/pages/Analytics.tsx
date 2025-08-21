import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Card, 
  CardHeader, 
  CardBody, 
  Button, 
  Badge, 
  Select,
  Chart
} from '../components';
import { useAppStore } from '../stores/appStore';
import { applicationService } from '../services/api';
import {
  DocumentArrowDownIcon,
  ArrowTrendingUpIcon,
  BriefcaseIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';
import { ApplicationStatus } from '../types';

const Analytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState('30d');
  const [chartType, setChartType] = useState('bar');
  const { applications, resumes } = useAppStore();

  // Fetch analytics data
  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['analytics', timeRange],
    queryFn: () => applicationService.getStats(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const timeRangeOptions = [
    { value: '7d', label: 'Last 7 days' },
    { value: '30d', label: 'Last 30 days' },
    { value: '90d', label: 'Last 90 days' },
    { value: '1y', label: 'Last year' },
  ];

  const chartTypeOptions = [
    { value: 'bar', label: 'Bar Chart' },
    { value: 'line', label: 'Line Chart' },
    { value: 'pie', label: 'Pie Chart' },
    { value: 'doughnut', label: 'Doughnut Chart' },
  ];

  // Calculate analytics data
  const statusData = [
    { label: 'Applied', value: applications.filter(a => a.status === ApplicationStatus.APPLIED).length, color: '#3B82F6' },
    { label: 'Under Review', value: applications.filter(a => a.status === 'under_review').length, color: '#F59E0B' },
    { label: 'Interview', value: applications.filter(a => a.status === 'interview_scheduled').length, color: '#8B5CF6' },
    { label: 'Offer', value: applications.filter(a => a.status === 'offer_received').length, color: '#10B981' },
    { label: 'Rejected', value: applications.filter(a => a.status === 'rejected').length, color: '#EF4444' },
  ];

  const monthlyData = [
    { label: 'Jan', value: 12 },
    { label: 'Feb', value: 19 },
    { label: 'Mar', value: 15 },
    { label: 'Apr', value: 22 },
    { label: 'May', value: 28 },
    { label: 'Jun', value: 25 },
  ];

  const skillsData = [
    { label: 'JavaScript', value: 85, color: '#F59E0B' },
    { label: 'React', value: 78, color: '#3B82F6' },
    { label: 'Python', value: 72, color: '#10B981' },
    { label: 'Node.js', value: 68, color: '#8B5CF6' },
    { label: 'SQL', value: 65, color: '#EF4444' },
  ];

  const responseTimeData = [
    { label: 'Same Day', value: 15, color: '#10B981' },
    { label: '1-3 Days', value: 28, color: '#3B82F6' },
    { label: '1 Week', value: 22, color: '#F59E0B' },
    { label: '2+ Weeks', value: 18, color: '#EF4444' },
    { label: 'No Response', value: 17, color: '#6B7280' },
  ];

  const handleExportData = () => {
    const exportData = {
      analytics: analytics,
      applications: applications,
      resumes: resumes,
      timestamp: new Date().toISOString(),
      timeRange: timeRange,
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analytics-${timeRange}-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (analyticsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Track your job application performance and insights
          </p>
        </div>
        <div className="flex space-x-3">
          <Select
            name="timeRange"
            value={timeRange}
            onChange={(value) => setTimeRange(value as string)}
            options={timeRangeOptions}
            className="w-40"
          />
          <Button onClick={handleExportData} variant="secondary">
            <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
            Export Data
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardBody className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BriefcaseIcon className="h-8 w-8 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Applications</p>
                <p className="text-2xl font-semibold text-gray-900">{applications.length}</p>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircleIcon className="h-8 w-8 text-success-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Success Rate</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {applications.length > 0 
                    ? Math.round((applications.filter(a => a.status === 'offer_received').length / applications.length) * 100)
                    : 0}%
                </p>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClockIcon className="h-8 w-8 text-warning-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Avg Response Time</p>
                <p className="text-2xl font-semibold text-gray-900">3.2 days</p>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ArrowTrendingUpIcon className="h-8 w-8 text-info-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Monthly Growth</p>
                <p className="text-2xl font-semibold text-gray-900">+12%</p>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Application Status Distribution */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Application Status Distribution</h3>
            <p className="text-sm text-gray-600">Current status of all applications</p>
          </CardHeader>
          <CardBody>
            <div className="flex space-x-3 mb-4">
              <Select
                name="chartType"
                value={chartType}
                onChange={(value) => setChartType(value as string)}
                options={chartTypeOptions}
                className="w-32"
              />
            </div>
            <Chart data={statusData} type={chartType as 'bar' | 'line' | 'pie' | 'doughnut'} height={250} />
          </CardBody>
        </Card>

        {/* Monthly Application Trends */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Monthly Application Trends</h3>
            <p className="text-sm text-gray-600">Application volume over time</p>
          </CardHeader>
          <CardBody>
            <Chart data={monthlyData} type="line" height={250} />
          </CardBody>
        </Card>

        {/* Skills Distribution */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Skills Distribution</h3>
            <p className="text-sm text-gray-600">Skills mentioned in applications</p>
          </CardHeader>
          <CardBody>
            <Chart data={skillsData} type="doughnut" height={250} />
          </CardBody>
        </Card>

        {/* Response Time Analysis */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Response Time Analysis</h3>
            <p className="text-sm text-gray-600">How quickly companies respond</p>
          </CardHeader>
          <CardBody>
            <Chart data={responseTimeData} type="bar" height={250} />
          </CardBody>
        </Card>
      </div>

      {/* Detailed Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Company Performance */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Company Performance</h3>
            <p className="text-sm text-gray-600">Success rates by company</p>
          </CardHeader>
          <CardBody>
            <div className="space-y-3">
              {applications.slice(0, 5).map((app, index) => (
                <div key={index} className="flex justify-between items-center">
                  <div>
                    <p className="font-medium text-gray-900">{app.company}</p>
                    <p className="text-sm text-gray-600">{app.job_title}</p>
                  </div>
                  <Badge variant={app.status === 'offer_received' ? 'success' : 'default'}>
                    {app.status.replace('_', ' ')}
                  </Badge>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Interview Performance */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Interview Performance</h3>
            <p className="text-sm text-gray-600">Interview outcomes and feedback</p>
          </CardHeader>
          <CardBody>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Technical Rounds</span>
                <span className="font-medium">85% Pass Rate</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Behavioral Rounds</span>
                <span className="font-medium">92% Pass Rate</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Final Rounds</span>
                <span className="font-medium">78% Pass Rate</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Overall Success</span>
                <span className="font-medium text-success-600">82%</span>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Insights and Recommendations */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">AI Insights & Recommendations</h3>
          <p className="text-sm text-gray-600">Data-driven suggestions for improvement</p>
        </CardHeader>
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Strengths</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center">
                  <CheckCircleIcon className="h-4 w-4 text-success-500 mr-2" />
                  Strong technical skills in React and JavaScript
                </li>
                <li className="flex items-center">
                  <CheckCircleIcon className="h-4 w-4 text-success-500 mr-2" />
                  Good response rate from tech companies
                </li>
                <li className="flex items-center">
                  <CheckCircleIcon className="h-4 w-4 text-success-500 mr-2" />
                  Consistent application volume
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Areas for Improvement</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center">
                  <XCircleIcon className="h-4 w-4 text-danger-500 mr-2" />
                  Consider adding more Python/ML skills
                </li>
                <li className="flex items-center">
                  <XCircleIcon className="h-4 w-4 text-danger-500 mr-2" />
                  Improve follow-up timing (currently 5+ days)
                </li>
                <li className="flex items-center">
                  <XCircleIcon className="h-4 w-4 text-danger-500 mr-2" />
                  Target more remote-first companies
                </li>
              </ul>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  );
};

export default Analytics;
