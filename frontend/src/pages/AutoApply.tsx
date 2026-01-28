import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Badge,
  Input,
  Select,
  Alert,
  Toggle
} from '../components';
import { autoApplyService } from '../services/api';
import {
  PlayIcon,
  PauseIcon,
  Cog6ToothIcon,
  ChartBarIcon,
  ListBulletIcon
} from '@heroicons/react/24/outline';

const AutoApply: React.FC = () => {
  const [keywords, setKeywords] = useState('');
  const [locations, setLocations] = useState('');
  const [minSalary, setMinSalary] = useState<number | ''>('');
  const [dailyLimit, setDailyLimit] = useState(5);
  const [isConfigChanged, setIsConfigChanged] = useState(false);

  const queryClient = useQueryClient();

  // Fetch config
  const { data: config, isLoading: configLoading } = useQuery({
    queryKey: ['auto-apply-config'],
    queryFn: autoApplyService.getConfig
  });

  // Sync config data to local state
  useEffect(() => {
    if (config) {
      setKeywords(config.keywords.join(', '));
      setLocations(config.locations.join(', '));
      setMinSalary(config.min_salary || '');
      setDailyLimit(config.daily_limit);
    }
  }, [config]);

  // Fetch activity log
  const { data: activityLog = [], isLoading: logLoading } = useQuery({
    queryKey: ['auto-apply-activity'],
    queryFn: autoApplyService.getActivity,
    refetchInterval: 30000 // Refresh every 30s
  });

  // Update config mutation
  const updateConfigMutation = useMutation({
    mutationFn: autoApplyService.updateConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auto-apply-config'] });
      setIsConfigChanged(false);
    }
  });

  // Toggle auto-apply mutation
  const toggleMutation = useMutation({
    mutationFn: (isActive: boolean) => 
      isActive ? autoApplyService.start() : autoApplyService.stop(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auto-apply-config'] });
    }
  });

  const handleSaveConfig = () => {
    updateConfigMutation.mutate({
      keywords: keywords.split(',').map(k => k.trim()).filter(k => k),
      locations: locations.split(',').map(l => l.trim()).filter(l => l),
      min_salary: minSalary === '' ? undefined : Number(minSalary),
      daily_limit: dailyLimit
    });
  };

  const handleToggle = () => {
    if (config) {
      toggleMutation.mutate(!config.is_active);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Auto Apply</h1>
          <p className="mt-2 text-gray-600">
            Automate your job search with AI-powered applications.
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <span className={`text-sm font-medium ${config?.is_active ? 'text-green-600' : 'text-gray-500'}`}>
            {config?.is_active ? 'Active' : 'Inactive'}
          </span>
          <Toggle
            checked={config?.is_active || false}
            onChange={handleToggle}
            label="Auto Apply Status"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <div className="flex items-center space-x-2">
                <Cog6ToothIcon className="h-5 w-5 text-gray-500" />
                <h3 className="text-lg font-medium text-gray-900">Configuration</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Keywords (comma separated)
                  </label>
                  <Input
                    name="keywords"
                    value={keywords}
                    onChange={(val: any) => {
                      setKeywords(val);
                      setIsConfigChanged(true);
                    }}
                    placeholder="e.g. Python, React, Remote"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Locations (comma separated)
                  </label>
                  <Input
                    name="locations"
                    value={locations}
                    onChange={(val: any) => {
                      setLocations(val);
                      setIsConfigChanged(true);
                    }}
                    placeholder="e.g. San Francisco, Remote"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Minimum Salary
                  </label>
                  <Input
                    name="minSalary"
                    type="number"
                    value={minSalary === '' ? '' : String(minSalary)}
                    onChange={(val: any) => {
                      setMinSalary(val === '' ? '' : Number(val));
                      setIsConfigChanged(true);
                    }}
                    placeholder="e.g. 100000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Daily Limit: {dailyLimit}
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="50"
                    value={dailyLimit}
                    onChange={(e) => {
                      setDailyLimit(Number(e.target.value));
                      setIsConfigChanged(true);
                    }}
                    className="w-full"
                  />
                </div>
                <Button
                  variant="primary"
                  className="w-full"
                  disabled={!isConfigChanged}
                  onClick={handleSaveConfig}
                >
                  Save Configuration
                </Button>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Activity Log */}
        <div className="lg:col-span-2">
          <Card className="h-full">
            <CardHeader>
              <div className="flex items-center space-x-2">
                <ListBulletIcon className="h-5 w-5 text-gray-500" />
                <h3 className="text-lg font-medium text-gray-900">Activity Log</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Job
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Company
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {activityLog.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">
                          No activity yet
                        </td>
                      </tr>
                    ) : (
                      activityLog.map((log: any) => (
                        <tr key={log.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(log.timestamp).toLocaleString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {log.job_title}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {log.company}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <Badge variant={log.status === 'success' ? 'success' : 'danger'}>
                              {log.status}
                            </Badge>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AutoApply;
