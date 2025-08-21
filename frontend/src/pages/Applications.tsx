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
import { applicationService } from '../services/api';
import type { JobApplication } from '../types';
import { ApplicationStatus } from '../types';
import {
  PlusIcon,
  EyeIcon,
  TrashIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';

const Applications: React.FC = () => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedApplication, setSelectedApplication] = useState<JobApplication | null>(null);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState<ApplicationStatus | ''>('');
  
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

  const handleCreateApplication = (data: { 
    job_title: string; 
    company: string; 
    location?: string; 
    description?: string; 
    salary_range?: string; 
    contact_person?: string; 
    contact_email?: string; 
    contact_phone?: string; 
    notes?: string; 
  }) => {
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
            <div className="text-sm text-gray-500">
              {filteredApplications.length} of {applications.length} applications
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Applications List */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-medium text-gray-900">Your Applications</h3>
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
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <h4 className="text-lg font-medium text-gray-900">
                          {application.job_title}
                        </h4>
                        <Badge variant={getStatusColor(application.status)}>
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
                <Badge variant={getStatusColor(selectedApplication.status)} className="mt-1">
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
    </div>
  );
};

export default Applications;
