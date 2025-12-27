import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Card, 
  CardHeader, 
  CardBody, 
  Button, 
  Badge, 
  Modal, 
  Spinner,
  Alert,
  Select,
  Form,
  FormField
} from '../components';
import { useAppStore } from '../stores/appStore';
import { applicationService, exportService } from '../services/api';
import type { JobApplication } from '../types';
import { ApplicationStatus } from '../types';
import { ExportModal } from '../components/ExportModal';
import {
  PlusIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  FunnelIcon,
  ArrowDownTrayIcon,
  CheckIcon,
} from '@heroicons/react/24/outline';

const Applications: React.FC = () => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedApplication, setSelectedApplication] = useState<JobApplication | null>(null);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState<ApplicationStatus | ''>('');
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  
  const queryClient = useQueryClient();
  const { applications, setApplications, addApplication, updateApplication, deleteApplication } = useAppStore();

  // Fetch applications
  const { data: fetchedApplications, isLoading, error } = useQuery({
    queryKey: ['applications'],
    queryFn: () => applicationService.getApplications(),
  });

  // Update applications when data is fetched
  useEffect(() => {
    if (fetchedApplications?.data) {
      setApplications(fetchedApplications.data);
    }
  }, [fetchedApplications]);

  // Create application mutation
  const createMutation = useMutation({
    mutationFn: applicationService.createApplication,
    onSuccess: (newApplication) => {
      addApplication(newApplication);
      setIsCreateModalOpen(false);
      queryClient.invalidateQueries({ queryKey: ['applications'] });
    },
  });

  // Update application mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<JobApplication> }) =>
      applicationService.updateApplication(id, data),
    onSuccess: (updatedApplication) => {
      updateApplication(updatedApplication.id, updatedApplication);
      queryClient.invalidateQueries({ queryKey: ['applications'] });
    },
  });

  // Delete application mutation
  const deleteMutation = useMutation({
    mutationFn: applicationService.deleteApplication,
    onSuccess: (_, deletedId) => {
      deleteApplication(deletedId);
      queryClient.invalidateQueries({ queryKey: ['applications'] });
    },
  });

  // Bulk update mutation
  const bulkUpdateMutation = useMutation({
    mutationFn: ({ ids, data }: { ids: string[]; data: Partial<JobApplication> }) =>
      applicationService.bulkUpdate(ids, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      setSelectedIds([]);
    },
  });

  // Bulk delete mutation
  const bulkDeleteMutation = useMutation({
    mutationFn: applicationService.bulkDelete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      setSelectedIds([]);
    },
  });

  const handleCreateApplication = (data: any) => {
    createMutation.mutate({
      ...data,
      applied_date: new Date().toISOString(),
      status: 'draft' as ApplicationStatus,
    });
  };

  const handleStatusChange = (applicationId: string, newStatus: ApplicationStatus) => {
    updateMutation.mutate({
      id: applicationId,
      data: { status: newStatus },
    });
  };

  const handleDelete = (applicationId: string) => {
    if (window.confirm('Are you sure you want to delete this application?')) {
      deleteMutation.mutate(applicationId);
    }
  };

  const handleSelectAll = () => {
    if (selectedIds.length === filteredApplications.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(filteredApplications.map(app => app.id));
    }
  };

  const handleToggleSelect = (id: string) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const handleBulkStatusChange = (status: ApplicationStatus) => {
    if (selectedIds.length === 0) return;
    bulkUpdateMutation.mutate({ ids: selectedIds, data: { status } });
  };

  const handleBulkDelete = () => {
    if (selectedIds.length === 0) return;
    if (window.confirm(`Are you sure you want to delete ${selectedIds.length} applications?`)) {
      bulkDeleteMutation.mutate(selectedIds);
    }
  };

  const handleExport = async (format: 'pdf' | 'csv' | 'excel', options?: { dateFrom?: string; dateTo?: string }) => {
    try {
      const blob = await exportService.exportApplications(
        selectedIds.length > 0 ? selectedIds : undefined,
        format,
        options?.dateFrom,
        options?.dateTo
      );
      
      const extension = format === 'excel' ? 'xlsx' : format;
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `applications_export.${extension}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error('Export failed:', err);
      throw new Error(err.message || 'Failed to export applications');
    }
  };

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'draft', label: 'Draft' },
    { value: 'applied', label: 'Applied' },
    { value: 'under_review', label: 'Under Review' },
    { value: 'interview_scheduled', label: 'Interview Scheduled' },
    { value: 'interview_completed', label: 'Interview Completed' },
    { value: 'offer_received', label: 'Offer Received' },
    { value: 'offer_accepted', label: 'Offer Accepted' },
    { value: 'offer_declined', label: 'Offer Declined' },
    { value: 'rejected', label: 'Rejected' },
    { value: 'withdrawn', label: 'Withdrawn' },
  ];

  const getStatusColor = (status: ApplicationStatus) => {
    const colorMap: Record<ApplicationStatus, string> = {
      [ApplicationStatus.DRAFT]: 'default',
      [ApplicationStatus.APPLIED]: 'primary',
      [ApplicationStatus.UNDER_REVIEW]: 'warning',
      [ApplicationStatus.INTERVIEW_SCHEDULED]: 'primary',
      [ApplicationStatus.INTERVIEW_COMPLETED]: 'primary',
      [ApplicationStatus.OFFER_RECEIVED]: 'success',
      [ApplicationStatus.OFFER_ACCEPTED]: 'success',
      [ApplicationStatus.OFFER_DECLINED]: 'warning',
      [ApplicationStatus.REJECTED]: 'danger',
      [ApplicationStatus.WITHDRAWN]: 'default',
    };
    return colorMap[status] || 'default';
  };

  const filteredApplications = applications.filter(app => 
    !statusFilter || app.status === statusFilter
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <Alert 
          type="error" 
          title="Error Loading Applications"
          message="Failed to load applications. Please try again later."
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Applications</h1>
          <p className="mt-2 text-gray-600">
            Manage your job applications and track their progress.
          </p>
        </div>
        <Button 
          variant="primary" 
          onClick={() => setIsCreateModalOpen(true)}
          className="flex items-center"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          New Application
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardBody className="p-4">
          <div className="flex items-center space-x-4">
            <FunnelIcon className="h-5 w-5 text-gray-400" />
            <div className="flex-1 max-w-xs">
              <Select
                name="status-filter"
                value={statusFilter}
                onChange={(value) => setStatusFilter(value as ApplicationStatus | '')}
                options={statusOptions}
                placeholder="Filter by status"
              />
            </div>
            <div className="flex items-center space-x-2">
              <Button 
                variant="secondary" 
                size="sm" 
                onClick={() => setIsExportModalOpen(true)}
                className="flex items-center"
              >
                <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                Export
              </Button>
            </div>
            <div className="text-sm text-gray-500">
              {filteredApplications.length} of {applications.length} applications
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Bulk Actions Toolbar */}
      {selectedIds.length > 0 && (
        <div className="bg-primary-50 border border-primary-100 rounded-lg p-3 flex items-center justify-between animate-fade-in">
          <div className="flex items-center space-x-4">
            <span className="text-primary-800 font-medium">
              {selectedIds.length} items selected
            </span>
            <div className="h-4 w-px bg-primary-200"></div>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-primary-700">Update Status:</span>
              <div className="w-48">
                <Select
                  name="bulk-status"
                  value=""
                  onChange={(value) => handleBulkStatusChange(value as ApplicationStatus)}
                  options={statusOptions.slice(1)}
                  placeholder="Select status..."
                />
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button 
              variant="secondary" 
              size="sm" 
              onClick={() => handleExport('csv')}
              className="text-primary-700"
            >
              Export Selected
            </Button>
            <Button 
              variant="danger" 
              size="sm" 
              onClick={handleBulkDelete}
              className="flex items-center"
            >
              <TrashIcon className="h-4 w-4 mr-1" />
              Delete Selected
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setSelectedIds([])}
            >
              Cancel
            </Button>
          </div>
        </div>
      )}

      {/* Applications List */}
      <Card>
        <CardHeader className="flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              checked={selectedIds.length === filteredApplications.length && filteredApplications.length > 0}
              onChange={handleSelectAll}
            />
            <h3 className="text-lg font-medium text-gray-900">Your Applications</h3>
          </div>
        </CardHeader>
        <CardBody>
          {filteredApplications.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-gray-400 mb-4">
                <PlusIcon className="mx-auto h-12 w-12" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No applications found</h3>
              <p className="text-gray-500 mb-4">
                {statusFilter ? 'No applications match the selected filter.' : 'Get started by creating your first job application.'}
              </p>
              {!statusFilter && (
                <Button variant="primary" onClick={() => setIsCreateModalOpen(true)}>
                  Create Application
                </Button>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {filteredApplications.map((application) => (
                <div
                  key={application.id}
                  className={`border rounded-lg p-4 transition-colors ${
                    selectedIds.includes(application.id) 
                      ? 'border-primary-300 bg-primary-50' 
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center space-x-4">
                    <input
                      type="checkbox"
                      className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      checked={selectedIds.includes(application.id)}
                      onChange={() => handleToggleSelect(application.id)}
                    />
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <h4 className="text-lg font-medium text-gray-900">
                              {application.job_title}
                            </h4>
                            <Badge variant={getStatusColor(application.status) as any}>
                              {application.status.replace('_', ' ')}
                            </Badge>
                          </div>
                          <p className="text-gray-600 mt-1">{application.company}</p>
                          <p className="text-sm text-gray-500 mt-1">
                            Applied: {new Date(application.applied_date).toLocaleDateString()}
                          </p>
                          {application.notes && (
                            <p className="text-sm text-gray-600 mt-2 truncate">
                              {application.notes}
                            </p>
                          )}
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedApplication(application);
                              setIsViewModalOpen(true);
                            }}
                          >
                            <EyeIcon className="h-4 w-4" />
                          </Button>
                          <Select
                            name={`status-${application.id}`}
                            value={application.status}
                            onChange={(value) => handleStatusChange(application.id, value as ApplicationStatus)}
                            options={statusOptions.slice(1)} // Remove "All Statuses" option
                          />
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(application.id)}
                            className="text-danger-600 hover:text-danger-700"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardBody>
      </Card>

      {/* Create Application Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create New Application"
        size="lg"
      >
        <Form onSubmit={handleCreateApplication}>
          <div className="space-y-4">
            <FormField
              name="job_title"
              label="Job Title"
              required
              placeholder="e.g. Senior Software Engineer"
            />
            <FormField
              name="company"
              label="Company"
              required
              placeholder="e.g. Google"
            />
            <FormField
              name="location"
              label="Location"
              placeholder="e.g. San Francisco, CA"
            />
            <FormField
              name="job_id"
              label="Job ID/URL"
              placeholder="Job posting ID or URL"
            />
            <FormField
              name="notes"
              label="Notes"
              type="textarea"
              placeholder="Additional notes about this application..."
            />
          </div>
          
          <div className="flex justify-end space-x-3 mt-6">
            <Button 
              type="button" 
              variant="secondary" 
              onClick={() => setIsCreateModalOpen(false)}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              variant="primary"
              loading={createMutation.isPending}
            >
              Create Application
            </Button>
          </div>
        </Form>
      </Modal>

      {/* View Application Modal */}
      <Modal
        isOpen={isViewModalOpen}
        onClose={() => setIsViewModalOpen(false)}
        title="Application Details"
        size="lg"
      >
        {selectedApplication && (
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-medium text-gray-900">
                {selectedApplication.job_title}
              </h3>
              <p className="text-gray-600">{selectedApplication.company}</p>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Status</label>
                <Badge variant={getStatusColor(selectedApplication.status) as any} className="mt-1">
                  {selectedApplication.status.replace('_', ' ')}
                </Badge>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Applied Date</label>
                <p className="mt-1 text-sm text-gray-900">
                  {new Date(selectedApplication.applied_date).toLocaleDateString()}
                </p>
              </div>
              {selectedApplication.location && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Location</label>
                  <p className="mt-1 text-sm text-gray-900">{selectedApplication.location}</p>
                </div>
              )}
              {selectedApplication.job_id && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Job ID</label>
                  <p className="mt-1 text-sm text-gray-900">{selectedApplication.job_id}</p>
                </div>
              )}
            </div>
            
            {selectedApplication.notes && (
              <div>
                <label className="block text-sm font-medium text-gray-700">Notes</label>
                <p className="mt-1 text-sm text-gray-900">{selectedApplication.notes}</p>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Export Modal */}
      <ExportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        onExport={handleExport}
        title="Export Applications"
        supportedFormats={['pdf', 'csv', 'excel']}
        showDateRange={true}
        defaultFormat="csv"
      />
    </div>
  );
};

export default Applications;
