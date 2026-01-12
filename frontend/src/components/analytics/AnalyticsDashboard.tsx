import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Button from '@/components/ui/Button';
import { Download, TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';

interface AnalyticsDashboardProps {
    userId: string;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ userId }) => {
    const [dashboardData, setDashboardData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [dateRange, setDateRange] = useState({ start: null, end: null });
    const [insights, setInsights] = useState<any>(null);

    useEffect(() => {
        fetchDashboardData();
        fetchInsights();
    }, [userId, dateRange]);

    const fetchDashboardData = async () => {
        try {
            const response = await fetch('/api/v1/analytics/dashboard?days=30', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
                }
            });
            const result = await response.json();
            setDashboardData(result.data);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            setLoading(false);
        }
    };

    const fetchInsights = async () => {
        try {
            const response = await fetch('/api/v1/analytics/insights/ai-recommendations', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
                }
            });
            const result = await response.json();
            setInsights(result.data);
        } catch (error) {
            console.error('Error fetching insights:', error);
        }
    };

    const handleExport = async (format: string) => {
        try {
            const response = await fetch(`/api/v1/analytics/export?format=${format}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
                }
            });
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `analytics_report.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Error exporting data:', error);
        }
    };

    if (loading) {
        return <div className="flex items-center justify-center h-64">Loading analytics...</div>;
    }

    if (!dashboardData) {
        return <div className="text-center text-gray-500">No data available</div>;
    }

    const { success_metrics, response_time_metrics, interview_metrics, trends, skills_gap, companies } = dashboardData;

    // Prepare chart data
    const statusData = Object.entries(success_metrics.breakdown || {}).map(([name, value]) => ({
        name: name.replace(/_/g, ' ').toUpperCase(),
        value: value as number
    }));

    const trendData = trends.weekly_trends || [];

    return (
        <div className="space-y-6 p-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
                <div className="flex gap-2">
                    <Button onClick={() => handleExport('csv')} variant="secondary">
                        <Download className="mr-2 h-4 w-4" />
                        Export CSV
                    </Button>
                    <Button onClick={() => handleExport('excel')} variant="secondary">
                        <Download className="mr-2 h-4 w-4" />
                        Export Excel
                    </Button>
                    <Button onClick={() => handleExport('pdf')} variant="secondary">
                        <Download className="mr-2 h-4 w-4" />
                        Export PDF
                    </Button>
                </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                    <CardHeader title="Total Applications" />
                    <CardBody>
                        <div className="text-2xl font-bold">{success_metrics.total_applications}</div>
                    </CardBody>
                </Card>

                <Card>
                    <CardHeader title="Success Rate">
                        {success_metrics.success_rate > 15 ? (
                            <TrendingUp className="h-4 w-4 text-green-600" />
                        ) : (
                            <TrendingDown className="h-4 w-4 text-red-600" />
                        )}
                    </CardHeader>
                    <CardBody>
                        <div className="text-2xl font-bold">{success_metrics.success_rate}%</div>
                    </CardBody>
                </Card>

                <Card>
                    <CardHeader title="Interview Rate" />
                    <CardBody>
                        <div className="text-2xl font-bold">{success_metrics.interview_rate}%</div>
                    </CardBody>
                </Card>

                <Card>
                    <CardHeader title="Avg Response Time" />
                    <CardBody>
                        <div className="text-2xl font-bold">{response_time_metrics.avg_response_time_days} days</div>
                    </CardBody>
                </Card>
            </div>

            {/* AI Insights */}
            {insights && insights.insights && insights.insights.length > 0 && (
                <Card>
                    <CardHeader title="AI-Powered Insights" />
                    <CardBody>
                        <div className="space-y-3">
                            {insights.insights.map((insight: any, index: number) => (
                                <div
                                    key={index}
                                    className={`p-3 rounded-lg border ${insight.type === 'warning' ? 'bg-yellow-50 border-yellow-200' :
                                        insight.type === 'success' ? 'bg-green-50 border-green-200' :
                                            'bg-blue-50 border-blue-200'
                                        }`}
                                >
                                    <div className="flex items-start gap-2">
                                        <AlertCircle className="h-5 w-5 mt-0.5" />
                                        <div>
                                            <p className="font-medium">{insight.message}</p>
                                            {insights.recommendations && insights.recommendations.length > 0 && (
                                                <p className="text-sm text-gray-600 mt-1">
                                                    Recommendation: {insights.recommendations[0].suggestion}
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardBody>
                </Card>
            )}

            {/* Charts Row 1 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Status Distribution */}
                <Card>
                    <CardHeader title="Application Status Distribution" />
                    <CardBody>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={statusData}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={({ name, percent }: any) => `${name}: ${(percent * 100).toFixed(0)}%`}
                                    outerRadius={80}
                                    fill="#8884d8"
                                    dataKey="value"
                                >
                                    {statusData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                            </PieChart>
                        </ResponsiveContainer>
                    </CardBody>
                </Card>

                {/* Trend Analysis */}
                <Card>
                    <CardHeader title="Application Trends (Weekly)" />
                    <CardBody>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={trendData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="week" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Line type="monotone" dataKey="applications" stroke="#8884d8" name="Applications" />
                                <Line type="monotone" dataKey="interviews" stroke="#82ca9d" name="Interviews" />
                                <Line type="monotone" dataKey="offers" stroke="#ffc658" name="Offers" />
                            </LineChart>
                        </ResponsiveContainer>
                    </CardBody>
                </Card>
            </div>

            {/* Skills Gap */}
            <Card>
                <CardHeader title="Top Required Skills" />
                <CardBody>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={skills_gap.top_required_skills || []}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="skill" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="count" fill="#8884d8" name="Frequency" />
                        </BarChart>
                    </ResponsiveContainer>
                </CardBody>
            </Card>

            {/* Company Analysis Table */}
            <Card>
                <CardHeader title="Company Analysis" />
                <CardBody>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b">
                                    <th className="text-left p-2">Company</th>
                                    <th className="text-right p-2">Applications</th>
                                    <th className="text-right p-2">Interviews</th>
                                    <th className="text-right p-2">Offers</th>
                                    <th className="text-right p-2">Success Rate</th>
                                </tr>
                            </thead>
                            <tbody>
                                {companies.companies.slice(0, 10).map((company: any, index: number) => (
                                    <tr key={index} className="border-b hover:bg-gray-50">
                                        <td className="p-2">{company.company}</td>
                                        <td className="text-right p-2">{company.total}</td>
                                        <td className="text-right p-2">{company.interviews}</td>
                                        <td className="text-right p-2">{company.offers}</td>
                                        <td className="text-right p-2">{company.success_rate}%</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </CardBody>
            </Card>
        </div>
    );
};

export default AnalyticsDashboard;
