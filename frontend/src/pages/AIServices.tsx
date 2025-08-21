import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { 
  Card, 
  CardHeader, 
  CardBody, 
  Button, 
  Badge, 
  Modal, 
  Spinner,
  Alert,
  Form,
  FormField,
  Select
} from '../components';
import { useAppStore } from '../stores/appStore';
import { aiService } from '../services/api';
import type { Resume } from '../types';
import {
  SparklesIcon,
  DocumentTextIcon,
  EnvelopeIcon,
  MagnifyingGlassIcon,
  ChartBarIcon,
  LightBulbIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

const AIServices: React.FC = () => {
  const [isResumeOptimizationOpen, setIsResumeOptimizationOpen] = useState(false);
  const [isCoverLetterOpen, setIsCoverLetterOpen] = useState(false);
  const [isJobMatchingOpen, setIsJobMatchingOpen] = useState(false);
  const [selectedResume, setSelectedResume] = useState<Resume | null>(null);

  const [optimizationResult, setOptimizationResult] = useState<string>('');
  const [coverLetterResult, setCoverLetterResult] = useState<string>('');
  const [jobMatchResult, setJobMatchResult] = useState<{ 
    error?: string; 
    match_score?: number; 
    skills_gap?: string[];
    skills_analysis?: Array<{ name: string; matched: boolean }>;
    recommendations?: string[];
  } | null>(null);
  
  const { resumes } = useAppStore();

  // Fetch AI service status
  const { data: aiStatus, isLoading: statusLoading } = useQuery({
    queryKey: ['ai-status'],
    queryFn: () => aiService.getStatus(),
  });

  // Resume optimization mutation
  const optimizationMutation = useMutation({
    mutationFn: async ({ resumeId, jobDescription }: { resumeId: string; jobDescription: string }) => {
      return aiService.optimizeResume({
        resume_id: resumeId,
        job_description: jobDescription,
        optimization_type: 'all'
      });
    },
    onSuccess: (result) => {
      setOptimizationResult(result.optimized_content || 'Optimization completed successfully!');
    },
    onError: () => {
      setOptimizationResult('Optimization failed. Please try again.');
    },
  });

  // Cover letter generation mutation
  const coverLetterMutation = useMutation({
    mutationFn: async ({ 
      resumeId, 
      jobTitle, 
      company, 
      jobDescription 
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
      setCoverLetterResult(result.cover_letter || 'Cover letter generated successfully!');
    },
    onError: () => {
      setCoverLetterResult('Cover letter generation failed. Please try again.');
    },
  });

  // Job matching mutation
  const jobMatchingMutation = useMutation({
    mutationFn: async ({ resumeId, jobDescription }: { resumeId: string; jobDescription: string }) => {
      return aiService.analyzeJobMatch(resumeId, jobDescription);
    },
    onSuccess: (result) => {
      setJobMatchResult(result);
    },
    onError: () => {
      setJobMatchResult({ error: 'Job matching analysis failed. Please try again.' });
    },
  });

  const handleResumeOptimization = (data: { job_description: string }) => {
    if (selectedResume) {
      optimizationMutation.mutate({
        resumeId: selectedResume.id,
        jobDescription: data.job_description,
      });
    }
  };

  const handleCoverLetterGeneration = (data: { job_title: string; company: string; job_description: string }) => {
    if (selectedResume) {
      coverLetterMutation.mutate({
        resumeId: selectedResume.id,
        jobTitle: data.job_title,
        company: data.company,
        jobDescription: data.job_description,
      });
    }
  };

  const handleJobMatching = (data: { job_description: string }) => {
    if (selectedResume) {
      jobMatchingMutation.mutate({
        resumeId: selectedResume.id,
        jobDescription: data.job_description,
      });
    }
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'danger';
  };

  const getMatchScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent Match';
    if (score >= 60) return 'Good Match';
    if (score >= 40) return 'Fair Match';
    return 'Poor Match';
  };

  if (statusLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">AI Services</h1>
        <p className="mt-2 text-gray-600">
          Leverage AI to optimize your job search and application process.
        </p>
      </div>

      {/* AI Status */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <SparklesIcon className="h-6 w-6 text-primary-600" />
            <h3 className="text-lg font-medium text-gray-900">AI Service Status</h3>
          </div>
        </CardHeader>
        <CardBody>
          <div className="flex items-center space-x-4">
            <Badge variant={aiStatus?.available ? 'success' : 'danger'}>
              {aiStatus?.available ? 'Available' : 'Unavailable'}
            </Badge>
            <span className="text-sm text-gray-600">
              {aiStatus?.available ? 'AI services are ready to use' : 'AI services are currently unavailable'}
            </span>
          </div>
          {aiStatus?.model && (
            <p className="text-sm text-gray-500 mt-2">
              Using: {aiStatus.model}
            </p>
          )}
        </CardBody>
      </Card>

      {/* AI Services Grid */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Resume Optimization */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <DocumentTextIcon className="h-6 w-6 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Resume Optimization</h3>
            </div>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              Get AI-powered suggestions to improve your resume for specific job postings.
            </p>
            <Button
              variant="primary"
              onClick={() => setIsResumeOptimizationOpen(true)}
              className="w-full"
            >
              <SparklesIcon className="h-4 w-4 mr-2" />
              Optimize Resume
            </Button>
          </CardBody>
        </Card>

        {/* Cover Letter Generation */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <EnvelopeIcon className="h-6 w-6 text-success-600" />
              <h3 className="text-lg font-medium text-gray-900">Cover Letter Generation</h3>
            </div>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              Generate personalized cover letters tailored to specific job applications.
            </p>
            <Button
              variant="success"
              onClick={() => setIsCoverLetterOpen(true)}
              className="w-full"
            >
              <SparklesIcon className="h-4 w-4 mr-2" />
              Generate Cover Letter
            </Button>
          </CardBody>
        </Card>

        {/* Job Matching Analysis */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <MagnifyingGlassIcon className="h-6 w-6 text-warning-600" />
              <h3 className="text-lg font-medium text-gray-900">Job Matching</h3>
            </div>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              Analyze how well your resume matches specific job requirements.
            </p>
            <Button
              variant="warning"
              onClick={() => setIsJobMatchingOpen(true)}
              className="w-full"
            >
              <ChartBarIcon className="h-4 w-4 mr-2" />
              Analyze Match
            </Button>
          </CardBody>
        </Card>

        {/* Skills Extraction */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <LightBulbIcon className="h-6 w-6 text-info-600" />
              <h3 className="text-lg font-medium text-gray-900">Skills Extraction</h3>
            </div>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              Automatically extract and categorize skills from your resume content.
            </p>
            <Button
              variant="info"
              onClick={() => {}} // TODO: Implement skills extraction
              className="w-full"
              disabled
            >
              <SparklesIcon className="h-4 w-4 mr-2" />
              Extract Skills
            </Button>
          </CardBody>
        </Card>

        {/* Interview Preparation */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <CheckCircleIcon className="h-6 w-6 text-success-600" />
              <h3 className="text-lg font-medium text-gray-900">Interview Prep</h3>
            </div>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              Get AI-generated interview questions and preparation tips.
            </p>
            <Button
              variant="secondary"
              onClick={() => {}} // TODO: Implement interview prep
              className="w-full"
              disabled
            >
              <SparklesIcon className="h-4 w-4 mr-2" />
              Prepare for Interview
            </Button>
          </CardBody>
        </Card>

        {/* Career Insights */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <ChartBarIcon className="h-6 w-6 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Career Insights</h3>
            </div>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">
              Receive personalized career advice and growth recommendations.
            </p>
            <Button
              variant="secondary"
              onClick={() => {}} // TODO: Implement career insights
              className="w-full"
              disabled
            >
              <SparklesIcon className="h-4 w-4 mr-2" />
              Get Insights
            </Button>
          </CardBody>
        </Card>
      </div>

      {/* Resume Optimization Modal */}
      <Modal
        isOpen={isResumeOptimizationOpen}
        onClose={() => setIsResumeOptimizationOpen(false)}
        title="Resume Optimization"
        size="xl"
      >
        <div className="space-y-6">
          <Form onSubmit={handleResumeOptimization}>
            <div className="space-y-4">
              <Select
                name="resume"
                label="Select Resume"
                value={selectedResume?.id || ''}
                onChange={(value) => {
                  const resume = resumes.find(r => r.id === value);
                  setSelectedResume(resume || null);
                }}
                options={resumes.map(r => ({ value: r.id, label: r.title || r.filename }))}
                placeholder="Choose a resume to optimize"
                required
              />
              <FormField
                name="job_description"
                label="Job Description"
                type="textarea"
                placeholder="Paste the job description here to get targeted optimization suggestions..."
                required
              />
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <Button 
                type="button" 
                variant="secondary" 
                onClick={() => setIsResumeOptimizationOpen(false)}
              >
                Cancel
              </Button>
              <Button 
                type="submit" 
                variant="primary"
                loading={optimizationMutation.isPending}
              >
                <SparklesIcon className="h-4 w-4 mr-2" />
                Optimize Resume
              </Button>
            </div>
          </Form>

          {optimizationResult && (
            <div className="mt-6 p-4 bg-primary-50 border border-primary-200 rounded-lg">
              <h4 className="font-medium text-primary-900 mb-2">Optimization Result:</h4>
              <div className="text-primary-800 whitespace-pre-wrap">{optimizationResult}</div>
            </div>
          )}
        </div>
      </Modal>

      {/* Cover Letter Generation Modal */}
      <Modal
        isOpen={isCoverLetterOpen}
        onClose={() => setIsCoverLetterOpen(false)}
        title="Generate Cover Letter"
        size="xl"
      >
        <div className="space-y-6">
          <Form onSubmit={handleCoverLetterGeneration}>
            <div className="space-y-4">
              <Select
                name="resume"
                label="Select Resume"
                value={selectedResume?.id || ''}
                onChange={(value) => {
                  const resume = resumes.find(r => r.id === value);
                  setSelectedResume(resume || null);
                }}
                options={resumes.map(r => ({ value: r.id, label: r.title || r.filename }))}
                placeholder="Choose a resume to base the cover letter on"
                required
              />
              <FormField
                name="job_title"
                label="Job Title"
                placeholder="e.g., Senior Software Engineer"
                required
              />
              <FormField
                name="company"
                label="Company"
                placeholder="e.g., Google"
                required
              />
              <FormField
                name="job_description"
                label="Job Description"
                type="textarea"
                placeholder="Paste the job description to personalize the cover letter..."
                required
              />
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <Button 
                type="button" 
                variant="secondary" 
                onClick={() => setIsCoverLetterOpen(false)}
              >
                Cancel
              </Button>
              <Button 
                type="submit" 
                variant="success"
                loading={coverLetterMutation.isPending}
              >
                <SparklesIcon className="h-4 w-4 mr-2" />
                Generate Cover Letter
              </Button>
            </div>
          </Form>

          {coverLetterResult && (
            <div className="mt-6 p-4 bg-success-50 border border-success-200 rounded-lg">
              <h4 className="font-medium text-success-900 mb-2">Generated Cover Letter:</h4>
              <div className="text-success-800 whitespace-pre-wrap">{coverLetterResult}</div>
            </div>
          )}
        </div>
      </Modal>

      {/* Job Matching Analysis Modal */}
      <Modal
        isOpen={isJobMatchingOpen}
        onClose={() => setIsJobMatchingOpen(false)}
        title="Job Matching Analysis"
        size="xl"
      >
        <div className="space-y-6">
          <Form onSubmit={handleJobMatching}>
            <div className="space-y-4">
              <Select
                name="resume"
                label="Select Resume"
                value={selectedResume?.id || ''}
                onChange={(value) => {
                  const resume = resumes.find(r => r.id === value);
                  setSelectedResume(resume || null);
                }}
                options={resumes.map(r => ({ value: r.id, label: r.title || r.filename }))}
                placeholder="Choose a resume to analyze"
                required
              />
              <FormField
                name="job_description"
                label="Job Description"
                type="textarea"
                placeholder="Paste the job description to analyze the match..."
                required
              />
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <Button 
                type="button" 
                variant="secondary" 
                onClick={() => setIsJobMatchingOpen(false)}
              >
                Cancel
              </Button>
              <Button 
                type="submit" 
                variant="warning"
                loading={jobMatchingMutation.isPending}
              >
                <ChartBarIcon className="h-4 w-4 mr-2" />
                Analyze Match
              </Button>
            </div>
          </Form>

          {jobMatchResult && (
            <div className="mt-6 space-y-4">
              {jobMatchResult.error ? (
                <Alert type="error" message={jobMatchResult.error} />
              ) : (
                <>
                  {/* Match Score */}
                  <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium text-gray-900">Overall Match Score</h4>
                      <Badge variant={getMatchScoreColor(jobMatchResult.match_score || 0)} size="lg">
                        {jobMatchResult.match_score || 0}%
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {getMatchScoreLabel(jobMatchResult.match_score || 0)}
                    </p>
                  </div>

                  {/* Skills Analysis */}
                  {jobMatchResult.skills_analysis && (
                    <div className="p-4 bg-primary-50 border border-primary-200 rounded-lg">
                      <h4 className="font-medium text-primary-900 mb-3">Skills Analysis</h4>
                      <div className="space-y-2">
                        {jobMatchResult.skills_analysis.map((skill: { name: string; matched: boolean }, index: number) => (
                          <div key={index} className="flex items-center justify-between">
                            <span className="text-primary-800">{skill.name}</span>
                            <Badge variant={skill.matched ? 'success' : 'danger'} size="sm">
                              {skill.matched ? 'Match' : 'Missing'}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Recommendations */}
                  {jobMatchResult.recommendations && (
                    <div className="p-4 bg-warning-50 border border-warning-200 rounded-lg">
                      <h4 className="font-medium text-warning-900 mb-3">Recommendations</h4>
                      <ul className="space-y-2 text-warning-800">
                        {jobMatchResult.recommendations.map((rec: string, index: number) => (
                          <li key={index} className="flex items-start space-x-2">
                            <LightBulbIcon className="h-4 w-4 mt-0.5 flex-shrink-0" />
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default AIServices;
