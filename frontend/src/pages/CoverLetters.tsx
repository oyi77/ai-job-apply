import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { 
  Card, 
  CardHeader, 
  CardBody, 
  Button, 
  Badge, 
  Modal, 
  Form,
  FormField,
  Select,
  Input,
  Alert,
  Search,
  Pagination,
  Tooltip,
  Progress
} from '../components';
import { useAppStore } from '../stores/appStore';
import { aiService, coverLetterService } from '../services/api';
import type { CoverLetter, Resume, JobApplication } from '../types';
import {
  DocumentTextIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  DocumentArrowDownIcon,
  SparklesIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';

const CoverLetters: React.FC = () => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [isGenerateModalOpen, setIsGenerateModalOpen] = useState(false);
  const [selectedCoverLetter, setSelectedCoverLetter] = useState<CoverLetter | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedResume, setSelectedResume] = useState<Resume | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobApplication | null>(null);
  const [generationResult, setGenerationResult] = useState<string>('');
  const [generationProgress, setGenerationProgress] = useState(0);
  
  const { coverLetters, resumes, applications } = useAppStore();
  const itemsPerPage = 10;

  // Fetch cover letters
  const { data: coverLettersData, isLoading: coverLettersLoading } = useQuery({
    queryKey: ['cover-letters'],
    queryFn: () => coverLetterService.getCoverLetters(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Cover letter generation mutation
  const generationMutation = useMutation({
    mutationFn: async ({
      resumeId,
      jobTitle,
      company,
      jobDescription,
    }: {
      resumeId: string;
      jobTitle: string;
      company: string;
      jobDescription: string;
    }) => {
      return aiService.generateCoverLetter({
        resume_id: resumeId,
        job_title: jobTitle,
        company: company,
        job_description: jobDescription,
        tone: 'professional'
      });
    },
    onSuccess: (result) => {
      setGenerationResult(result.cover_letter || 'Cover letter generated successfully!');
      setGenerationProgress(100);
    },
    onError: (error) => {
      setGenerationResult('Cover letter generation failed. Please try again.');
      setGenerationProgress(0);
    },
  });

  // Filter cover letters based on search
  const filteredCoverLetters = coverLetters.filter(letter =>
    letter.job_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    letter.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
    letter.content.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Pagination
  const totalPages = Math.ceil(filteredCoverLetters.length / itemsPerPage);
  const paginatedCoverLetters = filteredCoverLetters.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handleCreateCoverLetter = (data: any) => {
    // TODO: Implement cover letter creation
    setIsCreateModalOpen(false);
  };

  const handleEditCoverLetter = (data: any) => {
    // TODO: Implement cover letter editing
    setIsEditModalOpen(false);
  };

  const handleGenerateCoverLetter = (data: any) => {
    if (selectedResume && selectedJob) {
      setGenerationProgress(0);
      const interval = setInterval(() => {
        setGenerationProgress(prev => {
          if (prev >= 90) {
            clearInterval(interval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      generationMutation.mutate({
        resumeId: selectedResume.id,
        jobTitle: data.job_title || selectedJob.job_title,
        company: data.company || selectedJob.company,
        jobDescription: data.job_description || '',
      });
    }
  };

  const handleDownload = (coverLetter: CoverLetter) => {
    const content = `Cover Letter for ${coverLetter.job_title} at ${coverLetter.company}\n\n${coverLetter.content}`;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cover-letter-${coverLetter.company}-${coverLetter.job_title}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft':
        return 'default';
      case 'final':
        return 'success';
      case 'sent':
        return 'primary';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'draft':
        return <ClockIcon className="h-4 w-4" />;
      case 'final':
        return <CheckCircleIcon className="h-4 w-4" />;
      case 'sent':
        return <DocumentTextIcon className="h-4 w-4" />;
      default:
        return <ClockIcon className="h-4 w-4" />;
    }
  };

  if (coverLettersLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading cover letters...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Cover Letters</h1>
          <p className="mt-2 text-gray-600">
            Manage and generate personalized cover letters for your job applications
          </p>
        </div>
        <div className="flex space-x-3">
          <Button onClick={() => setIsGenerateModalOpen(true)} variant="primary">
            <SparklesIcon className="h-4 w-4 mr-2" />
            Generate with AI
          </Button>
          <Button onClick={() => setIsCreateModalOpen(true)} variant="secondary">
            <PlusIcon className="h-4 w-4 mr-2" />
            Create New
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardBody className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DocumentTextIcon className="h-8 w-8 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Cover Letters</p>
                <p className="text-2xl font-semibold text-gray-900">{coverLetters.length}</p>
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
                <p className="text-sm font-medium text-gray-500">Final Versions</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {coverLetters.filter(c => c.status === 'final').length}
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
                <p className="text-sm font-medium text-gray-500">Drafts</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {coverLetters.filter(c => c.status === 'draft').length}
                </p>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DocumentArrowDownIcon className="h-8 w-8 text-info-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Sent</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {coverLetters.filter(c => c.status === 'sent').length}
                </p>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardBody className="p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <Search
                placeholder="Search cover letters..."
                value={searchTerm}
                onChange={setSearchTerm}
                className="w-full"
              />
            </div>
            <div className="flex space-x-2">
              <Select
                name="statusFilter"
                value=""
                onChange={() => {}}
                options={[
                  { value: '', label: 'All Statuses' },
                  { value: 'draft', label: 'Draft' },
                  { value: 'final', label: 'Final' },
                  { value: 'sent', label: 'Sent' },
                ]}
                className="w-40"
              />
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Cover Letters List */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Cover Letters</h3>
        </CardHeader>
        <CardBody>
          {paginatedCoverLetters.length === 0 ? (
            <div className="text-center py-12">
              <DocumentTextIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No cover letters found</p>
              <Button 
                onClick={() => setIsCreateModalOpen(true)} 
                variant="primary" 
                className="mt-4"
              >
                Create your first cover letter
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {paginatedCoverLetters.map((coverLetter) => (
                <div
                  key={coverLetter.id}
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="text-lg font-medium text-gray-900">
                          {coverLetter.job_title}
                        </h4>
                        <Badge variant={getStatusColor(coverLetter.status || 'draft') as any}>
                          <div className="flex items-center space-x-1">
                            {getStatusIcon(coverLetter.status || 'draft')}
                            <span>{coverLetter.status || 'draft'}</span>
                          </div>
                        </Badge>
                      </div>
                      <p className="text-gray-600 mb-2">{coverLetter.company}</p>
                      <p className="text-sm text-gray-500 mb-3">
                        {coverLetter.content.substring(0, 150)}...
                      </p>
                      <div className="flex items-center space-x-2 text-xs text-gray-400">
                        <span>Created: {new Date(coverLetter.created_at).toLocaleDateString()}</span>
                        {coverLetter.updated_at && (
                          <span>• Updated: {new Date(coverLetter.updated_at).toLocaleDateString()}</span>
                        )}
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <Tooltip content="View cover letter">
                        <Button
                          onClick={() => {
                            setSelectedCoverLetter(coverLetter);
                            setIsViewModalOpen(true);
                          }}
                          variant="ghost"
                          size="sm"
                        >
                          <EyeIcon className="h-4 w-4" />
                        </Button>
                      </Tooltip>
                      <Tooltip content="Edit cover letter">
                        <Button
                          onClick={() => {
                            setSelectedCoverLetter(coverLetter);
                            setIsEditModalOpen(true);
                          }}
                          variant="ghost"
                          size="sm"
                        >
                          <PencilIcon className="h-4 w-4" />
                        </Button>
                      </Tooltip>
                      <Tooltip content="Download cover letter">
                        <Button
                          onClick={() => handleDownload(coverLetter)}
                          variant="ghost"
                          size="sm"
                        >
                          <DocumentArrowDownIcon className="h-4 w-4" />
                        </Button>
                      </Tooltip>
                      <Tooltip content="Delete cover letter">
                        <Button
                          onClick={() => {
                            // TODO: Implement delete
                          }}
                          variant="ghost"
                          size="sm"
                          className="text-red-600 hover:text-red-700"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </Button>
                      </Tooltip>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-6">
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={setCurrentPage}
              />
            </div>
          )}
        </CardBody>
      </Card>

      {/* Create Cover Letter Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create New Cover Letter"
        size="lg"
      >
        <Form onSubmit={handleCreateCoverLetter}>
          <div className="space-y-4">
            <FormField
              label="Job Title"
              name="job_title"
              type="text"
              required
              placeholder="e.g., Senior Software Engineer"
            />
            <FormField
              label="Company"
              name="company"
              type="text"
              required
              placeholder="e.g., Tech Corp"
            />
            <FormField
              label="Content"
              name="content"
              type="textarea"
              required
              placeholder="Write your cover letter content here..."
            />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status <span className="text-red-500">*</span>
              </label>
              <Select
                name="status"
                value="draft"
                onChange={() => {}}
                options={[
                  { value: 'draft', label: 'Draft' },
                  { value: 'final', label: 'Final' },
                ]}
                placeholder="Select status"
              />
            </div>
          </div>
          <div className="flex justify-end space-x-3 mt-6">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsCreateModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary">
              Create Cover Letter
            </Button>
          </div>
        </Form>
      </Modal>

      {/* Edit Cover Letter Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Edit Cover Letter"
        size="lg"
      >
        {selectedCoverLetter && (
          <Form onSubmit={handleEditCoverLetter} defaultValues={selectedCoverLetter}>
            <div className="space-y-4">
              <FormField
                label="Job Title"
                name="job_title"
                type="text"
                required
              />
              <FormField
                label="Company"
                name="company"
                type="text"
                required
              />
              <FormField
                label="Content"
                name="content"
                type="textarea"
                required
              />
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status <span className="text-red-500">*</span>
                </label>
                <Select
                  name="status"
                  value={selectedCoverLetter.status || 'draft'}
                  onChange={() => {}}
                  options={[
                    { value: 'draft', label: 'Draft' },
                    { value: 'final', label: 'Final' },
                    { value: 'sent', label: 'Sent' },
                  ]}
                  placeholder="Select status"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <Button
                type="button"
                variant="secondary"
                onClick={() => setIsEditModalOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" variant="primary">
                Update Cover Letter
              </Button>
            </div>
          </Form>
        )}
      </Modal>

      {/* View Cover Letter Modal */}
      <Modal
        isOpen={isViewModalOpen}
        onClose={() => setIsViewModalOpen(false)}
        title={`Cover Letter - ${selectedCoverLetter?.job_title} at ${selectedCoverLetter?.company}`}
        size="xl"
      >
        {selectedCoverLetter && (
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {selectedCoverLetter.job_title}
                  </h3>
                  <p className="text-gray-600">{selectedCoverLetter.company}</p>
                </div>
                <Badge variant={getStatusColor(selectedCoverLetter.status || 'draft') as any}>
                  {selectedCoverLetter.status || 'draft'}
                </Badge>
              </div>
              <div className="prose max-w-none">
                <p className="whitespace-pre-wrap text-gray-700">
                  {selectedCoverLetter.content}
                </p>
              </div>
            </div>
            <div className="flex justify-between items-center text-sm text-gray-500">
              <span>Created: {new Date(selectedCoverLetter.created_at).toLocaleDateString()}</span>
              {selectedCoverLetter.updated_at && (
                <span>Updated: {new Date(selectedCoverLetter.updated_at).toLocaleDateString()}</span>
              )}
            </div>
            <div className="flex justify-end space-x-3">
              <Button
                onClick={() => handleDownload(selectedCoverLetter)}
                variant="secondary"
              >
                <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
                Download
              </Button>
              <Button
                onClick={() => {
                  setIsViewModalOpen(false);
                  setSelectedCoverLetter(selectedCoverLetter);
                  setIsEditModalOpen(true);
                }}
                variant="primary"
              >
                <PencilIcon className="h-4 w-4 mr-2" />
                Edit
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* AI Generation Modal */}
      <Modal
        isOpen={isGenerateModalOpen}
        onClose={() => setIsGenerateModalOpen(false)}
        title="Generate Cover Letter with AI"
        size="lg"
      >
        <Form onSubmit={handleGenerateCoverLetter}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Select Resume <span className="text-red-500">*</span>
              </label>
              <Select
                name="resume_id"
                value=""
                onChange={(value) => {
                  const resume = resumes.find(r => r.id === value);
                  setSelectedResume(resume || null);
                }}
                options={resumes.map(resume => ({
                  value: resume.id,
                  label: `${resume.title || resume.filename} (${resume.filename})`
                }))}
                placeholder="Select a resume"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Select Job Application
              </label>
              <Select
                name="job_application_id"
                value=""
                onChange={(value) => {
                  const app = applications.find(a => a.id === value);
                  setSelectedJob(app || null);
                }}
                options={[
                  { value: '', label: 'Custom job details' },
                  ...applications.map(app => ({
                    value: app.id,
                    label: `${app.job_title} at ${app.company}`
                  }))
                ]}
                placeholder="Select a job application or use custom details"
              />
            </div>
            <FormField
              label="Job Title"
              name="job_title"
              type="text"
              required
              placeholder="e.g., Senior Software Engineer"
            />
            <FormField
              label="Company"
              name="company"
              type="text"
              required
              placeholder="e.g., Tech Corp"
            />
            <FormField
              label="Job Description"
              name="job_description"
              type="textarea"
              placeholder="Paste the job description here for better AI generation..."
            />
          </div>

          {generationMutation.isPending && (
            <div className="mt-4">
              <Progress
                value={generationProgress}
                max={100}
                showLabel
                label="Generating cover letter..."
                className="mb-2"
              />
              <p className="text-sm text-gray-600">AI is crafting your personalized cover letter...</p>
            </div>
          )}

          {generationResult && (
            <div className="mt-4">
              <Alert type="success" title="Generation Complete!" message={generationResult} />
              <div className="mt-4">
                <Button
                  onClick={() => {
                    // TODO: Save generated cover letter
                    setIsGenerateModalOpen(false);
                  }}
                  variant="primary"
                  size="sm"
                >
                  Save Cover Letter
                </Button>
              </div>
            </div>
          )}

          <div className="flex justify-end space-x-3 mt-6">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsGenerateModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={generationMutation.isPending || !selectedResume}
            >
              <SparklesIcon className="h-4 w-4 mr-2" />
              Generate Cover Letter
            </Button>
          </div>
        </Form>
      </Modal>
    </div>
  );
};

export default CoverLetters;
