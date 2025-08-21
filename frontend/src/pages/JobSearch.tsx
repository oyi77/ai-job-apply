import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
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
  Input
} from '../components';
import { useAppStore } from '../stores/appStore';
import { jobSearchService, applicationService } from '../services/api';
import type { Job, JobType, ExperienceLevel, ApplicationStatus } from '../types';
import {
  MagnifyingGlassIcon,
  MapPinIcon,
  BuildingOfficeIcon,
  CurrencyDollarIcon,
  ClockIcon,
  BookmarkIcon,
  PlusIcon,
  FunnelIcon,
  ArrowsUpDownIcon,
} from '@heroicons/react/24/outline';

const JobSearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [location, setLocation] = useState('');
  const [selectedJobType, setSelectedJobType] = useState<JobType | ''>('');
  const [selectedExperience, setSelectedExperience] = useState<ExperienceLevel | ''>('');
  const [isSearching, setIsSearching] = useState(false);
  const [isJobDetailOpen, setIsJobDetailOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [isCreateApplicationOpen, setIsCreateApplicationOpen] = useState(false);
  const [sortBy, setSortBy] = useState<'relevance' | 'date' | 'salary'>('relevance');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  
  const queryClient = useQueryClient();
  const { addApplication } = useAppStore();

  // Search jobs
  // Search jobs
  const { data: searchResults = { data: [] }, isLoading, refetch } = useQuery({
    queryKey: ['job-search', searchQuery, location, selectedJobType, selectedExperience],
    queryFn: () => jobSearchService.searchJobs({
      query: searchQuery,
      location,
      job_type: selectedJobType || undefined,
      experience_level: selectedExperience || undefined,
      sort_by: sortBy,
      sort_order: sortOrder,
    }),
    enabled: false, // Only search when explicitly triggered
  });

  // Create application mutation
  const createApplicationMutation = useMutation({
    mutationFn: applicationService.createApplication,
    onSuccess: (newApplication) => {
      addApplication(newApplication);
      setIsCreateApplicationOpen(false);
      queryClient.invalidateQueries({ queryKey: ['applications'] });
    },
  });

  const handleSearch = async () => {
    if (searchQuery.trim()) {
      setIsSearching(true);
      await refetch();
      setIsSearching(false);
    }
  };

  const handleJobClick = (job: Job) => {
    setSelectedJob(job);
    setIsJobDetailOpen(true);
  };

  const handleCreateApplication = (data: { 
    notes?: string; 
    contact_person?: string; 
    contact_email?: string; 
    contact_phone?: string; 
  }) => {
    if (selectedJob) {
      createApplicationMutation.mutate({
        ...data,
        job_id: selectedJob.id || 'unknown',
        job_title: selectedJob.title || 'Unknown Job',
        company: selectedJob.company || 'Unknown Company',
        location: selectedJob.location || 'Unknown Location',
        applied_date: new Date().toISOString(),
        status: 'submitted' as ApplicationStatus,
      });
    }
  };

  const handleSaveJob = (job: Job) => {
    // TODO: Implement job saving functionality
    console.log('Saving job:', job);
  };

  const jobTypeOptions = [
    { value: '', label: 'All Job Types' },
    { value: 'full_time', label: 'Full Time' },
    { value: 'part_time', label: 'Part Time' },
    { value: 'contract', label: 'Contract' },
    { value: 'internship', label: 'Internship' },
    { value: 'freelance', label: 'Freelance' },
  ];

  const experienceOptions = [
    { value: '', label: 'All Experience Levels' },
    { value: 'entry', label: 'Entry Level' },
    { value: 'junior', label: 'Junior' },
    { value: 'mid', label: 'Mid Level' },
    { value: 'senior', label: 'Senior' },
    { value: 'lead', label: 'Lead' },
    { value: 'executive', label: 'Executive' },
  ];

  const sortOptions = [
    { value: 'relevance', label: 'Relevance' },
    { value: 'date', label: 'Date Posted' },
    { value: 'salary', label: 'Salary' },
  ];



  const formatDate = (dateString: string) => {
    if (!dateString) return 'Recently';
    
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return 'Recently';
      
      const now = new Date();
      const diffTime = Math.abs(now.getTime() - date.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays === 1) return 'Today';
      if (diffDays === 2) return 'Yesterday';
      if (diffDays <= 7) return `${diffDays - 1} days ago`;
      return date.toLocaleDateString();
    } catch {
      return 'Recently';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Job Search</h1>
        <p className="mt-2 text-gray-600">
          Search and discover job opportunities across multiple platforms.
        </p>
      </div>

      {/* Search Form */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-medium text-gray-900">Search Jobs</h3>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            {/* Search Inputs */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Job Title or Keywords
                </label>
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <Input
                    name="search"
                    value={searchQuery}
                    onChange={setSearchQuery}
                    placeholder="e.g., Software Engineer, React Developer"
                    className="pl-10"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Location
                </label>
                <div className="relative">
                  <MapPinIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <Input
                    name="location"
                    value={location}
                    onChange={setLocation}
                    placeholder="e.g., San Francisco, CA or Remote"
                    className="pl-10"
                  />
                </div>
              </div>
            </div>

            {/* Filters */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Select
                name="job_type"
                label="Job Type"
                value={selectedJobType}
                onChange={(value) => setSelectedJobType(value as JobType | '')}
                options={jobTypeOptions}
                placeholder="Select job type"
              />
              <Select
                name="experience_level"
                label="Experience Level"
                value={selectedExperience}
                onChange={(value) => setSelectedExperience(value as ExperienceLevel | '')}
                options={experienceOptions}
                placeholder="Select experience level"
              />
              <div className="flex items-end space-x-2">
                <Select
                  name="sort_by"
                  label="Sort By"
                  value={sortBy}
                  onChange={(value) => setSortBy(value as 'relevance' | 'date' | 'salary')}
                  options={sortOptions.map(opt => ({ value: opt.value, label: opt.label }))}
                  placeholder="Sort by"
                />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                  className="px-2"
                >
                  <ArrowsUpDownIcon className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Search Button */}
            <div className="flex justify-center">
              <Button
                variant="primary"
                onClick={handleSearch}
                loading={isSearching || isLoading}
                className="px-8"
              >
                <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
                Search Jobs
              </Button>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Search Results */}
      {searchResults && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium text-gray-900">
                Search Results ({searchResults.data?.length || 0} jobs found)
              </h3>
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <FunnelIcon className="h-4 w-4" />
                <span>Filtered and sorted</span>
              </div>
            </div>
          </CardHeader>
          <CardBody>
            {searchResults?.data && Array.isArray(searchResults.data) && searchResults.data.length > 0 ? (
              <div className="space-y-4">
                {searchResults.data.map((job) => job && (
                  <div
                    key={job.id || `job-${Math.random()}`}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors cursor-pointer"
                    onClick={() => handleJobClick(job)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h4 className="text-lg font-medium text-gray-900">
                            {job.title}
                          </h4>
                          {job.job_type && (
                            <Badge variant="primary" size="sm">
                              {job.job_type.replace('_', ' ')}
                            </Badge>
                          )}
                          {job.location?.toLowerCase().includes('remote') && (
                            <Badge variant="success" size="sm">
                              Remote
                            </Badge>
                          )}
                        </div>
                        
                        <div className="flex items-center space-x-4 text-sm text-gray-600 mb-2">
                          <div className="flex items-center space-x-1">
                            <BuildingOfficeIcon className="h-4 w-4" />
                            <span>{job.company}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <MapPinIcon className="h-4 w-4" />
                            <span>{job.location}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <ClockIcon className="h-4 w-4" />
                            <span>{job.posted_date ? formatDate(job.posted_date) : 'Recently'}</span>
                          </div>
                        </div>

                        {job.salary && (
                          <div className="flex items-center space-x-1 text-sm text-gray-600 mb-2">
                            <CurrencyDollarIcon className="h-4 w-4" />
                            <span>{job.salary}</span>
                          </div>
                        )}

                        {job.description && (
                          <p className="text-gray-600 text-sm line-clamp-2">
                            {job.description}
                          </p>
                        )}

                        {job.skills && job.skills.length > 0 && (
                          <div className="flex flex-wrap gap-2 mt-3">
                            {job.skills.slice(0, 5).map((skill, index) => (
                              <Badge key={index} variant="default" size="sm">
                                {skill}
                              </Badge>
                            ))}
                            {job.skills.length > 5 && (
                              <Badge variant="default" size="sm">
                                +{job.skills.length - 5} more
                              </Badge>
                            )}
                          </div>
                        )}
                      </div>

                      <div className="flex items-center space-x-2 ml-4">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleSaveJob(job)}
                          className="text-gray-400 hover:text-gray-600"
                        >
                          <BookmarkIcon className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={() => {
                            setSelectedJob(job);
                            setIsCreateApplicationOpen(true);
                          }}
                        >
                          <PlusIcon className="h-4 w-4 mr-1" />
                          Apply
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <MagnifyingGlassIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No jobs found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Try adjusting your search criteria or location.
                </p>
              </div>
            )}
          </CardBody>
        </Card>
      )}

      {/* Job Detail Modal */}
      <Modal
        isOpen={isJobDetailOpen}
        onClose={() => setIsJobDetailOpen(false)}
        title="Job Details"
        size="xl"
      >
        {selectedJob && (
          <div className="space-y-6">
            {/* Job Header */}
            <div className="border-b border-gray-200 pb-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-xl font-medium text-gray-900">
                    {selectedJob?.title || 'Job Title'}
                  </h3>
                  <p className="text-lg text-gray-600 mt-1">{selectedJob?.company || 'Company'}</p>
                  <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                    <div className="flex items-center space-x-1">
                      <MapPinIcon className="h-4 w-4" />
                      <span>{selectedJob?.location || 'Location'}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <ClockIcon className="h-4 w-4" />
                      <span>Posted {selectedJob?.posted_date ? formatDate(selectedJob.posted_date) : 'Recently'}</span>
                    </div>
                  </div>
                </div>
                <div className="flex flex-col items-end space-y-2">
                  {selectedJob?.job_type && (
                    <Badge variant="primary">
                      {selectedJob.job_type.replace('_', ' ')}
                    </Badge>
                  )}
                  {selectedJob?.location?.toLowerCase().includes('remote') && (
                    <Badge variant="success">Remote</Badge>
                  )}
                </div>
              </div>
            </div>

            {/* Job Details */}
            <div className="space-y-6">
              {/* Salary */}
              {selectedJob?.salary && (
                <div>
                  <h4 className="text-lg font-medium text-gray-900 mb-2">Salary</h4>
                  <div className="flex items-center space-x-2 text-lg text-gray-600">
                    <CurrencyDollarIcon className="h-5 w-5" />
                    <span>{selectedJob.salary}</span>
                  </div>
                </div>
              )}

              {/* Description */}
              {selectedJob?.description && (
                <div>
                  <h4 className="text-lg font-medium text-gray-900 mb-2">Job Description</h4>
                  <div className="text-gray-600 whitespace-pre-wrap">
                    {selectedJob.description}
                  </div>
                </div>
              )}

              {/* Requirements */}
              {selectedJob?.requirements && selectedJob.requirements.length > 0 && (
                <div>
                  <h4 className="text-lg font-medium text-gray-900 mb-2">Requirements</h4>
                  <ul className="space-y-2 text-gray-600">
                    {selectedJob.requirements.map((req, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 flex-shrink-0" />
                        <span>{req}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Skills */}
              {selectedJob?.skills && selectedJob.skills.length > 0 && (
                <div>
                  <h4 className="text-lg font-medium text-gray-900 mb-2">Required Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedJob.skills.map((skill, index) => (
                      <Badge key={index} variant="primary">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Benefits */}
              {selectedJob?.benefits && selectedJob.benefits.length > 0 && (
                <div>
                  <h4 className="text-lg font-medium text-gray-900 mb-2">Benefits</h4>
                  <ul className="space-y-2 text-gray-600">
                    {selectedJob.benefits.map((benefit, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <div className="w-2 h-2 bg-success-600 rounded-full mt-2 flex-shrink-0" />
                        <span>{benefit}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
              <Button
                variant="secondary"
                onClick={() => setIsJobDetailOpen(false)}
              >
                Close
              </Button>
              <Button
                variant="primary"
                onClick={() => {
                  setIsJobDetailOpen(false);
                  setIsCreateApplicationOpen(true);
                }}
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Apply Now
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Create Application Modal */}
      <Modal
        isOpen={isCreateApplicationOpen}
        onClose={() => setIsCreateApplicationOpen(false)}
        title="Create Application"
        size="lg"
      >
        {selectedJob && (
          <Form onSubmit={handleCreateApplication}>
            <div className="space-y-4">
              <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Job Details</h4>
                <p className="text-sm text-gray-600">
                  <strong>{selectedJob?.title || 'Job Title'}</strong> at <strong>{selectedJob?.company || 'Company'}</strong>
                </p>
                <p className="text-sm text-gray-500 mt-1">{selectedJob?.location || 'Location'}</p>
              </div>
              
              <FormField
                name="notes"
                label="Application Notes"
                type="textarea"
                placeholder="Add any notes about this application..."
              />
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <Button 
                type="button" 
                variant="ghost" 
                onClick={() => setIsCreateApplicationOpen(false)}
              >
                Cancel
              </Button>
              <Button 
                type="submit" 
                variant="primary"
                loading={createApplicationMutation.isPending}
              >
                Create Application
              </Button>
            </div>
          </Form>
        )}
      </Modal>
    </div>
  );
};

export default JobSearch;
