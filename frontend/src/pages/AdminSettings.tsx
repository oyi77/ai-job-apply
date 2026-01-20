import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Settings, 
  Brain, 
  Key, 
  RefreshCw, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Save,
  Trash2,
  Plus,
  TestTube,
  Zap,
  Clock,
  DollarSign,
  Activity
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Card, 
  CardHeader, 
  CardBody, 
  CardFooter 
} from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Alert } from '../components/ui/Alert';
import { Badge } from '../components/ui/Badge';
import { Spinner } from '../components/ui/Spinner';
import { apiService } from '../services/api';

interface AIProvider {
  id: string;
  provider_name: string;
  is_enabled: boolean;
  priority: number;
  api_base_url?: string;
  default_model?: string;
  temperature: number;
  max_tokens: number;
  supports_resume_optimization: boolean;
  supports_cover_letter: boolean;
  supports_interview_prep: boolean;
  supports_career_insights: boolean;
  requests_today: number;
  max_requests_daily?: number;
  cost_today: number;
  max_cost_daily?: number;
  last_used_at?: string;
  is_healthy: boolean;
}

interface GlobalAISettings {
  active_provider: string;
  default_temperature: number;
  default_max_tokens: number;
  auto_retry_on_failure: boolean;
  max_retries: number;
  fallback_to_mock: boolean;
  rate_limit_requests_per_minute: number;
  cache_enabled: boolean;
  cache_ttl_seconds: number;
}

export function AdminSettings() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [editingProvider, setEditingProvider] = useState<string | null>(null);
  const [showAddProvider, setShowAddProvider] = useState(false);
  const [testResult, setTestResult] = useState<{ status: string; message: string } | null>(null);

  // Fetch providers
  const { data: providers, isLoading: loadingProviders } = useQuery({
    queryKey: ['ai-providers'],
    queryFn: () => apiService.jobSearchService.getJobSources().catch(() => []),
  });

  // Fetch AI config directly
  const { data: aiConfig, isLoading: loadingAIConfig } = useQuery({
    queryKey: ['ai-config'],
    queryFn: async () => {
      try {
        const response = await fetch('/api/v1/ai-config/providers');
        if (!response.ok) throw new Error('Failed to fetch AI config');
        return await response.json() as AIProvider[];
      } catch {
        // Fallback to mock data if endpoint not available
        return [
          {
            id: 'gemini-1',
            provider_name: 'gemini',
            is_enabled: true,
            priority: 0,
            api_base_url: 'https://generativelanguage.googleapis.com',
            default_model: 'gemini-1.5-flash',
            temperature: 0.7,
            max_tokens: 2048,
            supports_resume_optimization: true,
            supports_cover_letter: true,
            supports_interview_prep: true,
            supports_career_insights: true,
            requests_today: 0,
            cost_today: 0,
            is_healthy: true,
          }
        ] as AIProvider[];
      }
    },
  });

  // Fetch global settings
  const { data: globalSettings, isLoading: loadingSettings } = useQuery({
    queryKey: ['ai-global-settings'],
    queryFn: async () => {
      try {
        const response = await fetch('/api/v1/ai-config/settings');
        if (!response.ok) throw new Error('Failed to fetch settings');
        return await response.json() as GlobalAISettings;
      } catch {
        // Fallback to default settings
        return {
          active_provider: 'gemini',
          default_temperature: 0.7,
          default_max_tokens: 2048,
          auto_retry_on_failure: true,
          max_retries: 3,
          fallback_to_mock: true,
          rate_limit_requests_per_minute: 60,
          cache_enabled: true,
          cache_ttl_seconds: 3600,
        } as GlobalAISettings;
      }
    },
  });

  // Update provider mutation
  const updateProviderMutation = useMutation({
    mutationFn: async ({ name, updates }: { name: string; updates: Partial<AIProvider> }) => {
      const response = await fetch(`/api/v1/ai-config/providers/${name}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      if (!response.ok) throw new Error('Failed to update provider');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-config'] });
    },
  });

  // Test provider mutation
  const testProviderMutation = useMutation({
    mutationFn: async (providerName: string) => {
      const response = await fetch(`/api/v1/ai-config/providers/${providerName}/test`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to test provider');
      return response.json();
    },
    onSuccess: (data) => {
      setTestResult(data);
    },
  });

  const isLoading = loadingProviders || loadingAIConfig || loadingSettings;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            AI Configuration
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage AI providers, API keys, and global settings
          </p>
        </div>
        <Button onClick={() => setShowAddProvider(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Provider
        </Button>
      </div>

      {/* Test Result Alert */}
      {testResult && (
        <Alert
          type={testResult.status === 'success' ? 'success' : testResult.status === 'error' ? 'error' : 'warning'}
          title={testResult.status === 'success' ? 'Test Passed' : testResult.status === 'error' ? 'Test Failed' : 'Warning'}
          onClose={() => setTestResult(null)}
        >
          {testResult.message}
        </Alert>
      )}

      {/* AI Providers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {aiConfig?.map((provider) => (
          <ProviderCard
            key={provider.id}
            provider={provider}
            onUpdate={(updates) => updateProviderMutation.mutate({ name: provider.provider_name, updates })}
            onTest={() => testProviderMutation.mutate(provider.provider_name)}
            isUpdating={updateProviderMutation.isPending}
          />
        ))}
      </div>

      {/* Global Settings */}
      {globalSettings && (
        <GlobalSettingsCard
          settings={globalSettings}
          onUpdate={(updates) => {
            fetch('/api/v1/ai-config/settings', {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(updates),
            }).then(() => {
              queryClient.invalidateQueries({ queryKey: ['ai-global-settings'] });
            });
          }}
        />
      )}

      {/* Add Provider Modal */}
      {showAddProvider && (
        <AddProviderModal
          onClose={() => setShowAddProvider(false)}
          onAdd={(provider) => {
            fetch('/api/v1/ai-config/providers', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(provider),
            }).then(() => {
              setShowAddProvider(false);
              queryClient.invalidateQueries({ queryKey: ['ai-config'] });
            });
          }}
        />
      )}
    </div>
  );
}

function ProviderCard({ 
  provider, 
  onUpdate, 
  onTest,
  isUpdating 
}: { 
  provider: AIProvider;
  onUpdate: (updates: Partial<AIProvider>) => void;
  onTest: () => void;
  isUpdating: boolean;
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    api_key: '',
    temperature: provider.temperature,
    max_tokens: provider.max_tokens,
    default_model: provider.default_model || '',
  });

  const handleSave = () => {
    onUpdate({
      ...formData,
      api_key: formData.api_key || undefined,
    });
    setIsEditing(false);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg ${provider.is_enabled ? 'bg-primary-100 text-primary-600' : 'bg-gray-100 text-gray-600'}`}>
              <Brain className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-semibold text-lg capitalize">{provider.provider_name}</h3>
              <p className="text-sm text-gray-500">{provider.default_model}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {provider.is_healthy ? (
              <CheckCircle className="w-5 h-5 text-green-500" />
            ) : (
              <XCircle className="w-5 h-5 text-red-500" />
            )}
            <Badge variant={provider.is_enabled ? 'success' : 'default'}>
              {provider.is_enabled ? 'Active' : 'Disabled'}
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardBody className="space-y-4">
        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="flex items-center justify-center text-gray-500 mb-1">
              <Activity className="w-4 h-4" />
            </div>
            <p className="text-2xl font-bold">{provider.requests_today}</p>
            <p className="text-xs text-gray-500">Requests Today</p>
          </div>
          <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="flex items-center justify-center text-gray-500 mb-1">
              <DollarSign className="w-4 h-4" />
            </div>
            <p className="text-2xl font-bold">${provider.cost_today.toFixed(2)}</p>
            <p className="text-xs text-gray-500">Cost Today</p>
          </div>
          <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="flex items-center justify-center text-gray-500 mb-1">
              <Clock className="w-4 h-4" />
            </div>
            <p className="text-2xl font-bold">{provider.temperature}</p>
            <p className="text-xs text-gray-500">Temperature</p>
          </div>
        </div>

        {/* Features */}
        <div className="flex flex-wrap gap-2">
          {provider.supports_resume_optimization && (
            <Badge variant="info" size="sm">Resume Optimization</Badge>
          )}
          {provider.supports_cover_letter && (
            <Badge variant="info" size="sm">Cover Letter</Badge>
          )}
          {provider.supports_interview_prep && (
            <Badge variant="info" size="sm">Interview Prep</Badge>
          )}
          {provider.supports_career_insights && (
            <Badge variant="info" size="sm">Career Insights</Badge>
          )}
        </div>

        {/* Edit Form */}
        {isEditing && (
          <div className="space-y-4 pt-4 border-t">
            <Input
              label="API Key"
              type="password"
              value={formData.api_key}
              onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
              placeholder="Enter new API key to update"
            />
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Temperature"
                type="number"
                step="0.1"
                min="0"
                max="2"
                value={formData.temperature}
                onChange={(e) => setFormData({ ...formData, temperature: parseFloat(e.target.value) })}
              />
              <Input
                label="Max Tokens"
                type="number"
                min="1"
                max="8192"
                value={formData.max_tokens}
                onChange={(e) => setFormData({ ...formData, max_tokens: parseInt(e.target.value) })}
              />
            </div>
            <Input
              label="Default Model"
              value={formData.default_model}
              onChange={(e) => setFormData({ ...formData, default_model: e.target.value })}
              placeholder="e.g., gemini-1.5-flash"
            />
          </div>
        )}
      </CardBody>

      <CardFooter className="flex justify-between">
        <div className="flex space-x-2">
          {isEditing ? (
            <>
              <Button size="sm" variant="ghost" onClick={() => setIsEditing(false)}>
                Cancel
              </Button>
              <Button size="sm" onClick={handleSave} disabled={isUpdating}>
                <Save className="w-4 h-4 mr-1" />
                Save
              </Button>
            </>
          ) : (
            <Button size="sm" variant="ghost" onClick={() => setIsEditing(true)}>
              <Settings className="w-4 h-4 mr-1" />
              Configure
            </Button>
          )}
        </div>
        <div className="flex space-x-2">
          <Button size="sm" variant="ghost" onClick={onTest} disabled={testProviderMutation.isPending}>
            <TestTube className="w-4 h-4 mr-1" />
            Test
          </Button>
          <Button 
            size="sm" 
            variant={provider.is_enabled ? 'secondary' : 'primary'}
            onClick={() => onUpdate({ is_enabled: !provider.is_enabled })}
          >
            {provider.is_enabled ? 'Disable' : 'Enable'}
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}

function GlobalSettingsCard({ 
  settings, 
  onUpdate 
}: { 
  settings: GlobalAISettings;
  onUpdate: (updates: Partial<GlobalAISettings>) => void;
}) {
  const [formData, setFormData] = useState(settings);

  const handleSave = () => {
    onUpdate(formData);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-primary-100 text-primary-600 rounded-lg">
            <Zap className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold text-lg">Global AI Settings</h3>
            <p className="text-sm text-gray-500">Default behavior for all AI features</p>
          </div>
        </div>
      </CardHeader>

      <CardBody>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Input
            label="Active Provider"
            value={formData.active_provider}
            onChange={(e) => setFormData({ ...formData, active_provider: e.target.value })}
            placeholder="e.g., gemini"
          />
          <Input
            label="Default Temperature"
            type="number"
            step="0.1"
            min="0"
            max="2"
            value={formData.default_temperature}
            onChange={(e) => setFormData({ ...formData, default_temperature: parseFloat(e.target.value) })}
          />
          <Input
            label="Max Retries"
            type="number"
            min="0"
            max="10"
            value={formData.max_retries}
            onChange={(e) => setFormData({ ...formData, max_retries: parseInt(e.target.value) })}
          />
          <Input
            label="Rate Limit (req/min)"
            type="number"
            min="1"
            value={formData.rate_limit_requests_per_minute}
            onChange={(e) => setFormData({ ...formData, rate_limit_requests_per_minute: parseInt(e.target.value) })}
          />
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={formData.auto_retry_on_failure}
              onChange={(e) => setFormData({ ...formData, auto_retry_on_failure: e.target.checked })}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm">Auto Retry</span>
          </label>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={formData.fallback_to_mock}
              onChange={(e) => setFormData({ ...formData, fallback_to_mock: e.target.checked })}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm">Fallback to Mock</span>
          </label>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={formData.cache_enabled}
              onChange={(e) => setFormData({ ...formData, cache_enabled: e.target.checked })}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm">Enable Cache</span>
          </label>
          <Input
            label="Cache TTL (seconds)"
            type="number"
            min="0"
            value={formData.cache_ttl_seconds}
            onChange={(e) => setFormData({ ...formData, cache_ttl_seconds: parseInt(e.target.value) })}
          />
        </div>
      </CardBody>

      <CardFooter>
        <Button onClick={handleSave}>
          <Save className="w-4 h-4 mr-2" />
          Save Global Settings
        </Button>
      </CardFooter>
    </Card>
  );
}

function AddProviderModal({ 
  onClose, 
  onAdd 
}: { 
  onClose: () => void;
  onAdd: (provider: any) => void;
}) {
  const [formData, setFormData] = useState({
    provider_name: '',
    api_key: '',
    api_base_url: '',
    default_model: '',
    temperature: 0.7,
    max_tokens: 2048,
    is_enabled: true,
    priority: 0,
    supports_resume_optimization: true,
    supports_cover_letter: true,
    supports_interview_prep: true,
    supports_career_insights: true,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onAdd(formData);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b">
          <h2 className="text-xl font-bold">Add AI Provider</h2>
          <p className="text-gray-500 mt-1">Configure a new AI service provider</p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Provider Name"
              required
              value={formData.provider_name}
              onChange={(e) => setFormData({ ...formData, provider_name: e.target.value })}
              placeholder="e.g., openai, anthropic, gemini"
            />
            <Input
              label="Default Model"
              value={formData.default_model}
              onChange={(e) => setFormData({ ...formData, default_model: e.target.value })}
              placeholder="e.g., gpt-4, claude-3"
            />
          </div>

          <Input
            label="API Key"
            type="password"
            required
            value={formData.api_key}
            onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
            placeholder="Enter API key"
          />

          <Input
            label="API Base URL"
            value={formData.api_base_url}
            onChange={(e) => setFormData({ ...formData, api_base_url: e.target.value })}
            placeholder="e.g., https://api.openai.com/v1"
          />

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Temperature"
              type="number"
              step="0.1"
              min="0"
              max="2"
              value={formData.temperature}
              onChange={(e) => setFormData({ ...formData, temperature: parseFloat(e.target.value) })}
            />
            <Input
              label="Max Tokens"
              type="number"
              min="1"
              max="8192"
              value={formData.max_tokens}
              onChange={(e) => setFormData({ ...formData, max_tokens: parseInt(e.target.value) })}
            />
          </div>

          <div className="space-y-3">
            <label className="block text-sm font-medium">Features</label>
            <div className="grid grid-cols-2 gap-3">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={formData.supports_resume_optimization}
                  onChange={(e) => setFormData({ ...formData, supports_resume_optimization: e.target.checked })}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm">Resume Optimization</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={formData.supports_cover_letter}
                  onChange={(e) => setFormData({ ...formData, supports_cover_letter: e.target.checked })}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm">Cover Letter</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={formData.supports_interview_prep}
                  onChange={(e) => setFormData({ ...formData, supports_interview_prep: e.target.checked })}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm">Interview Prep</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={formData.supports_career_insights}
                  onChange={(e) => setFormData({ ...formData, supports_career_insights: e.target.checked })}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm">Career Insights</span>
              </label>
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t">
            <Button type="button" variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit">
              <Plus className="w-4 h-4 mr-2" />
              Add Provider
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AdminSettings;
