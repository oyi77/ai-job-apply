import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Card, 
  CardHeader, 
  CardBody, 
  Button, 
  Badge, 
  Select
} from '../components';
import { useAppStore } from '../stores/appStore';
import { applicationService, exportService, analyticsService } from '../services/api';
import { ExportModal } from '../components/ExportModal';
import {
  DocumentArrowDownIcon,
  ArrowTrendingUpIcon,
  BriefcaseIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';
import { StatusChart, TrendsChart, SkillsChart, ResponseTimeChart } from '../components/charts';

const Analytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState('30d');
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  const { applications, resumes } = useAppStore();

  // Fetch analytics data
  const { data: analytics, isLoading: analyticsLoading, error: analyticsError, refetch: refetchAnalytics } = useQuery({
    queryKey: ['analytics-dashboard', timeRange],
    queryFn: () => analyticsService.getDashboard(timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : timeRange === '90d' ? 90 : 365),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const timeRangeOptions = [
    { value: '7d', label: 'Last 7 days' },
    { value: '30d', label: 'Last 30 days' },
    { value: '90d', label: 'Last 90 days' },
    { value: '1y', label: 'Last year' },
  ];

  // Calculate analytics data
  const statusData = analytics?.success_metrics?.breakdown ? [
    { label: 'Applied', value: analytics.success_metrics.total_applications || 0, color: '#3B82F6' },
    { label: 'Interview', value: analytics.success_metrics.breakdown.interview_scheduled || 0, color: '#8B5CF6' },
    { label: 'Offer', value: analytics.success_metrics.breakdown.offer_received || 0, color: '#10B981' },
    { label: 'Rejected', value: analytics.success_metrics.breakdown.rejected || 0, color: '#EF4444' },
    { label: 'Withdrawn', value: analytics.success_metrics.breakdown.withdrawn || 0, color: '#6B7280' },
  ] : [];

  const monthlyData = analytics?.trends?.weekly_trends ? analytics.trends.weekly_trends.map((item: any) => ({
    label: item.week,
    value: item.applications
  })) : [];

  const skillsData = analytics?.skills_gap?.top_required_skills ? analytics.skills_gap.top_required_skills.slice(0, 5).map((skill: any, index: number) => ({
    label: skill.skill,
    value: skill.percentage || 0,
    color: ['#F59E0B', '#3B82F6', '#10B981', '#8B5CF6', '#EF4444'][index % 5]
  })) : [];

  const responseTimeData = analytics?.response_time_metrics ? [
    { label: 'Avg Response', value: analytics.response_time_metrics.avg_response_time_days || 0, color: '#3B82F6' },
    { label: 'Avg Interview', value: analytics.response_time_metrics.avg_interview_time_days || 0, color: '#8B5CF6' },
    { label: 'Fastest', value: analytics.response_time_metrics.fastest_response_days || 0, color: '#10B981' },
    { label: 'Slowest', value: analytics.response_time_metrics.slowest_response_days || 0, color: '#EF4444' }
  ] : [];

  const handleExport = async (format: 'pdf' | 'csv' | 'excel', options?: { includeCharts?: boolean }) => {
    try {
      const blob = await exportService.exportAnalytics(format, options?.includeCharts ?? true);
      
      const extension = format === 'excel' ? 'xlsx' : format;
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics_export.${extension}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error('Export failed:', err);
      throw new Error(err.message || 'Failed to export analytics');
    }
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

  if (analyticsError) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center max-w-lg mx-auto p-6 bg-white rounded-lg shadow-sm border border-gray-200">
          <XCircleIcon className="h-12 w-12 text-danger-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Failed to load analytics</h3>
          <p className="text-gray-600 mb-4">
            We couldn't retrieve your analytics data. Please check your connection and try again.
          </p>
          <Button onClick={() => refetchAnalytics()} variant="primary">
            Retry
          </Button>
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
          <Button onClick={() => setIsExportModalOpen(true)} variant="secondary">
            <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
            Export
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
                <p className="text-2xl font-semibold text-gray-900">{analytics?.success_metrics?.total_applications || 0}</p>
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
                  {analytics?.success_metrics?.success_rate ? `${analytics.success_metrics.success_rate}%` : '0%'}
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
                <p className="text-2xl font-semibold text-gray-900">
                  {analytics?.response_time_metrics?.avg_response_time_days 
                    ? `${analytics.response_time_metrics.avg_response_time_days} days` 
                    : 'N/A'}
                </p>
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
                <p className="text-sm font-medium text-gray-500">Avg Weekly Apps</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {analytics?.trends?.avg_applications_per_week 
                    ? analytics.trends.avg_applications_per_week
                    : '0'}
                </p>
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
            <StatusChart data={statusData} />
          </CardBody>
        </Card>

        {/* Monthly Application Trends */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Monthly Application Trends</h3>
            <p className="text-sm text-gray-600">Application volume over time</p>
          </CardHeader>
          <CardBody>
            <TrendsChart data={monthlyData} />
          </CardBody>
        </Card>

        {/* Skills Distribution */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Skills Distribution</h3>
            <p className="text-sm text-gray-600">Skills mentioned in applications</p>
          </CardHeader>
          <CardBody>
            <SkillsChart data={skillsData} />
          </CardBody>
        </Card>

        {/* Response Time Analysis */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Response Time Analysis</h3>
            <p className="text-sm text-gray-600">How quickly companies respond</p>
          </CardHeader>
          <CardBody>
            <ResponseTimeChart data={responseTimeData} />
          </CardBody>
        </Card>
      </div>

      {/* Detailed Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Company Performance */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Company Performance</h3>
            <p className="text-sm text-gray-600">Top companies by application volume</p>
          </CardHeader>
          <CardBody>
            <div className="space-y-3">
              {analytics?.companies?.companies ? (
                analytics.companies.companies.slice(0, 5).map((company: any, index: number) => (
                  <div key={index} className="flex justify-between items-center">
                    <div>
                      <p className="font-medium text-gray-900">{company.company}</p>
                      <p className="text-sm text-gray-600">{company.total} applications</p>
                    </div>
                    <Badge variant={company.success_rate > 0 ? 'success' : 'default'}>
                      {company.success_rate}% Success
                    </Badge>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center py-4">No company data available</p>
              )}
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
                <span className="text-gray-600">Total Interviews</span>
                <span className="font-medium">{analytics?.interview_metrics?.total_interviews || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Offer Rate</span>
                <span className="font-medium">
                  {analytics?.interview_metrics?.interview_to_offer_rate 
                    ? `${analytics.interview_metrics.interview_to_offer_rate}%` 
                    : '0%'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Rejections (After Interview)</span>
                <span className="font-medium text-danger-600">
                  {analytics?.interview_metrics?.rejections_after_interview || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Pending</span>
                <span className="font-medium text-info-600">
                  {analytics?.interview_metrics?.pending_interviews || 0}
                </span>
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
              <h4 className="font-medium text-gray-900 mb-3">Top Requested Skills</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                {analytics?.skills_gap?.top_required_skills?.slice(0, 5).map((skill: any, index: number) => (
                  <li key={index} className="flex items-center">
                    <CheckCircleIcon className="h-4 w-4 text-success-500 mr-2" />
                    {skill.skill} ({skill.percentage}%)
                  </li>
                ))}
                {!analytics?.skills_gap?.top_required_skills?.length && (
                  <li className="text-gray-500">No sufficient data for skills analysis</li>
                )}
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Recommendations</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                {analytics?.skills_gap?.recommendations?.slice(0, 5).map((rec: string, index: number) => (
                  <li key={index} className="flex items-center">
                    <ArrowTrendingUpIcon className="h-4 w-4 text-primary-500 mr-2" />
                    {rec}
                  </li>
                ))}
                {!analytics?.skills_gap?.recommendations?.length && (
                  <li className="text-gray-500">No specific recommendations available</li>
                )}
              </ul>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Export Modal */}
      <ExportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        onExport={handleExport}
        title="Export Analytics"
        supportedFormats={['pdf', 'csv', 'excel']}
        showDateRange={false}
        defaultFormat="pdf"
      />
    </div>
  );
};

export default Analytics;
