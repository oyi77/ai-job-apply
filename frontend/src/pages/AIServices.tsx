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
import { aiService, resumeService } from '../services/api';
import type { Resume, JobApplication } from '../types';
import {
  SparklesIcon,
  DocumentTextIcon,
  EnvelopeIcon,
  MagnifyingGlassIcon,
  ChartBarIcon,
  LightBulbIcon,
  CheckCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';

const AIServices: React.FC = () => {
  const [isResumeOptimizationOpen, setIsResumeOptimizationOpen] = useState(false);
  const [isCoverLetterOpen, setIsCoverLetterOpen] = useState(false);
  const [isJobMatchingOpen, setIsJobMatchingOpen] = useState(false);
  const [selectedResume, setSelectedResume] = useState<Resume | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobApplication | null>(null);
  const [optimizationResult, setOptimizationResult] = useState<string>('');
  const [coverLetterResult, setCoverLetterResult] = useState<string>('');
  const [jobMatchResult, setJobMatchResult] = useState<any>(null);
  const [isSkillsExtractionOpen, setIsSkillsExtractionOpen] = useState(false);
  const [isInterviewPrepOpen, setIsInterviewPrepOpen] = useState(false);
  const [isCareerInsightsOpen, setIsCareerInsightsOpen] = useState(false);
  const [skillsResult, setSkillsResult] = useState<{ skills: string[]; confidence: number } | null>(null);
  const [interviewPrepResult, setInterviewPrepResult] = useState<any>(null);
  const [careerInsightsResult, setCareerInsightsResult] = useState<any>(null);
  const [selectedApplicationForInterview, setSelectedApplicationForInterview] = useState<JobApplication | null>(null);
  const [isLoadingInterviewPrep, setIsLoadingInterviewPrep] = useState(false);

  const { resumes, applications } = useAppStore();

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
    onError: (error) => {
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
    onError: (error) => {
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
    onError: (error) => {
      setJobMatchResult({ error: 'Job matching analysis failed. Please try again.' });
    },
  });

  // Skills extraction mutation
  const skillsExtractionMutation = useMutation({
    mutationFn: async (text: string) => {
      return aiService.extractSkills(text);
    },
    onSuccess: (result) => {
      setSkillsResult(result);
    },
    onError: () => {
      setSkillsResult({ skills: [], confidence: 0 });
    },
  });

  // Career insights mutation
  const careerInsightsMutation = useMutation({
    mutationFn: async () => {
      // Gather data for insights
      const applicationHistory = applications.map(app => ({
        title: app.job_title,
        company: app.company,
        status: app.status,
        date: app.applied_date
      }));

      // Get skills from the most recent or default resume
      let skills: string[] = [];
      const defaultResume = resumes.find(r => r.is_default) || resumes[0];
      if (defaultResume) {
        skills = defaultResume.skills || [];
      }

      return aiService.generateCareerInsights({
        application_history: applicationHistory,
        skills: skills,
        experience_level: defaultResume?.experience_years ? `${defaultResume.experience_years} years` : undefined
      });
    },
    onSuccess: (result) => {
      setCareerInsightsResult(result);
    },
    onError: (error) => {
      setCareerInsightsResult({ error: 'Failed to generate career insights. Please try again.' });
    },
  });

  const handleResumeOptimization = (data: any) => {
    if (selectedResume) {
      optimizationMutation.mutate({
        resumeId: selectedResume.id,
        jobDescription: data.job_description,
      });
    }
  };

  const handleCoverLetterGeneration = (data: any) => {
    if (selectedResume) {
      coverLetterMutation.mutate({
        resumeId: selectedResume.id,
        jobTitle: data.job_title,
        company: data.company,
        jobDescription: data.job_description,
      });
    }
  };

  const handleJobMatching = (data: any) => {
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
              onClick={() => setIsSkillsExtractionOpen(true)}
              className="w-full"
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
              onClick={() => setIsInterviewPrepOpen(true)}
              className="w-full"
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
              onClick={() => setIsCareerInsightsOpen(true)}
              className="w-full"
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
                options={resumes.map(r => ({ value: r.id, label: r.name || r.title || r.filename || 'Unnamed Resume' }))}
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
                options={resumes.map(r => ({ value: r.id, label: r.title || r.filename || 'Untitled Resume' }))}
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
                options={resumes.map(r => ({ value: r.id, label: r.title || r.filename || 'Untitled Resume' }))}
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
                        {jobMatchResult.skills_analysis.map((skill: any, index: number) => (
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

      {/* Skills Extraction Modal */}
      <Modal
        isOpen={isSkillsExtractionOpen}
        onClose={() => {
          setIsSkillsExtractionOpen(false);
          setSkillsResult(null);
        }}
        title="Extract Skills from Resume"
        size="lg"
      >
        <div className="space-y-4">
          <Select
            name="resume"
            label="Select Resume"
            value=""
            onChange={(value) => {
              const resume = resumes.find(r => r.id === value);
              if (resume && resume.content) {
                skillsExtractionMutation.mutate(resume.content);
              }
            }}
            options={[
              { value: '', label: 'Select a resume' },
              ...resumes.map(r => ({ value: r.id, label: r.title || r.original_filename || 'Untitled Resume' }))
            ]}
          />
          {skillsResult && (
            <div className="mt-4">
              <Alert
                type="success"
                title={`Extracted ${skillsResult.skills.length} skills`}
                message={`Confidence: ${(skillsResult.confidence * 100).toFixed(1)}%`}
              />
              <div className="mt-4 flex flex-wrap gap-2">
                {skillsResult.skills.map((skill, index) => (
                  <Badge key={index} variant="primary" size="sm">
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      </Modal>

      {/* Interview Prep Modal */}
      <Modal
        isOpen={isInterviewPrepOpen}
        onClose={() => {
          setIsInterviewPrepOpen(false);
          setInterviewPrepResult('');
        }}
        title="Interview Preparation"
        size="lg"
      >
        <div className="space-y-4">
          <Select
            name="job_application"
            label="Select Job Application"
            value=""
            options={[
              { value: '', label: 'Select a job application' },
              ...applications.map(app => ({
                value: app.id,
                label: `${app.job_title} at ${app.company}`
              }))
            ]}
            onChange={async (value) => {
              const app = applications.find(a => a.id === value);
              if (app) {
                setSelectedApplicationForInterview(app);
                setIsLoadingInterviewPrep(true);
                setInterviewPrepResult(null);

                try {
                  // Get resume content if resume_id is available
                  let resumeContent = '';
                  if (app.resume_id) {
                    try {
                      const resume = await resumeService.getResume(app.resume_id);
                      resumeContent = resume.content || '';
                    } catch (error) {
                      console.warn('Could not fetch resume content:', error);
                      // Try to get from store
                      const storeResume = resumes.find(r => r.id === app.resume_id);
                      resumeContent = storeResume?.content || '';
                    }
                  } else {
                    // Use default resume if no resume_id
                    const defaultResume = resumes.find(r => r.is_default) || resumes[0];
                    if (defaultResume) {
                      try {
                        const resume = await resumeService.getResume(defaultResume.id);
                        resumeContent = resume.content || '';
                      } catch (error) {
                        resumeContent = defaultResume.content || '';
                      }
                    }
                  }

                  // Create job description from application data
                  const jobDescription = app.notes ||
                    `Position: ${app.job_title}\nCompany: ${app.company}\nLocation: ${app.location}`;

                  // Call interview prep API
                  const result = await aiService.prepareInterview(
                    jobDescription,
                    resumeContent,
                    app.company,
                    app.job_title
                  );

                  setInterviewPrepResult(result);
                } catch (error: any) {
                  console.error('Error preparing interview:', error);
                  setInterviewPrepResult({
                    error: error?.response?.data?.detail || error?.message || 'Failed to prepare interview. Please try again.'
                  });
                } finally {
                  setIsLoadingInterviewPrep(false);
                }
              } else {
                setSelectedApplicationForInterview(null);
                setInterviewPrepResult(null);
              }
            }}
          />
          {isLoadingInterviewPrep && (
            <div className="mt-4 flex items-center justify-center py-8">
              <Spinner size="lg" />
              <span className="ml-3 text-gray-600">Preparing interview questions...</span>
            </div>
          )}

          {interviewPrepResult && !isLoadingInterviewPrep && (
            <div className="mt-4 space-y-6">
              {interviewPrepResult.error ? (
                <Alert type="error" message={interviewPrepResult.error} />
              ) : (
                <>
                  {/* Questions */}
                  {interviewPrepResult.questions && interviewPrepResult.questions.length > 0 && (
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-3">Interview Questions</h4>
                      <div className="space-y-4">
                        {interviewPrepResult.questions.map((q: any, index: number) => (
                          <div key={index} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex items-start justify-between mb-2">
                              <p className="font-medium text-gray-900">{q.question}</p>
                              <Badge variant="secondary" size="sm">{q.type || 'general'}</Badge>
                            </div>
                            {q.suggested_answer && (
                              <p className="text-sm text-gray-600 mt-2">{q.suggested_answer}</p>
                            )}
                            {q.tips && q.tips.length > 0 && (
                              <div className="mt-2">
                                <p className="text-xs font-medium text-gray-500 mb-1">Tips:</p>
                                <ul className="list-disc list-inside text-xs text-gray-600">
                                  {q.tips.map((tip: string, tipIndex: number) => (
                                    <li key={tipIndex}>{tip}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Technical Questions */}
                  {interviewPrepResult.technical_questions && interviewPrepResult.technical_questions.length > 0 && (
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-3">Technical Questions</h4>
                      <div className="space-y-4">
                        {interviewPrepResult.technical_questions.map((q: any, index: number) => (
                          <div key={index} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex items-start justify-between mb-2">
                              <p className="font-medium text-gray-900">{q.question}</p>
                              <div className="flex gap-2">
                                <Badge variant="primary" size="sm">{q.category || 'technical'}</Badge>
                                <Badge variant="secondary" size="sm">{q.difficulty || 'medium'}</Badge>
                              </div>
                            </div>
                            {q.suggested_approach && (
                              <p className="text-sm text-gray-600 mt-2">{q.suggested_approach}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Preparation Tips */}
                  {interviewPrepResult.preparation_tips && interviewPrepResult.preparation_tips.length > 0 && (
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-3">Preparation Tips</h4>
                      <ul className="list-disc list-inside space-y-2 text-gray-700">
                        {interviewPrepResult.preparation_tips.map((tip: string, index: number) => (
                          <li key={index}>{tip}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Key Topics */}
                  {interviewPrepResult.key_topics && interviewPrepResult.key_topics.length > 0 && (
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-3">Key Topics to Review</h4>
                      <div className="flex flex-wrap gap-2">
                        {interviewPrepResult.key_topics.map((topic: string, index: number) => (
                          <Badge key={index} variant="primary">{topic}</Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Questions to Ask */}
                  {interviewPrepResult.questions_to_ask && interviewPrepResult.questions_to_ask.length > 0 && (
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-3">Questions to Ask the Interviewer</h4>
                      <ul className="list-disc list-inside space-y-2 text-gray-700">
                        {interviewPrepResult.questions_to_ask.map((question: string, index: number) => (
                          <li key={index}>{question}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Company Research */}
                  {interviewPrepResult.company_research && (
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-3">Company Research</h4>
                      <p className="text-gray-700">{interviewPrepResult.company_research}</p>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </div>
      </Modal>

      {/* Career Insights Modal */}
      <Modal
        isOpen={isCareerInsightsOpen}
        onClose={() => {
          setIsCareerInsightsOpen(false);
          setCareerInsightsResult(null);
        }}
        title="Career Insights"
        size="xl"
      >
        <div className="space-y-6">
          <div className="bg-primary-50 p-4 rounded-lg border border-primary-100">
            <h4 className="font-medium text-primary-900 mb-2">How it works</h4>
            <p className="text-sm text-primary-700">
              Our AI analyzes your job application history and resume skills to provide personalized career advice,
              market trends, and strategic recommendations for your growth.
            </p>
          </div>

          <Button
            variant="primary"
            onClick={() => careerInsightsMutation.mutate()}
            loading={careerInsightsMutation.isPending}
            className="w-full"
          >
            <ChartBarIcon className="h-4 w-4 mr-2" />
            Generate Career Insights
          </Button>

          {careerInsightsResult && (
            <div className="mt-6 space-y-6">
              {careerInsightsResult.error ? (
                <Alert type="error" message={careerInsightsResult.error} />
              ) : (
                <>
                  {/* Market Analysis */}
                  <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm">
                    <h4 className="text-lg font-medium text-gray-900 mb-3 flex items-center">
                      <ChartBarIcon className="h-5 w-5 mr-2 text-primary-600" />
                      Market Analysis
                    </h4>
                    <p className="text-gray-700">{careerInsightsResult.market_analysis}</p>
                  </div>

                  {/* Salary Insights */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-success-50 border border-success-100 rounded-lg">
                      <div className="text-sm text-success-700 font-medium">Estimated Salary</div>
                      <div className="text-lg font-bold text-success-900 mt-1">
                        {careerInsightsResult.salary_insights.estimated_range}
                      </div>
                    </div>
                    <div className="p-4 bg-blue-50 border border-blue-100 rounded-lg">
                      <div className="text-sm text-blue-700 font-medium">Market Trend</div>
                      <div className="text-lg font-bold text-blue-900 mt-1">
                        {careerInsightsResult.salary_insights.market_trend}
                      </div>
                    </div>
                    <div className="p-4 bg-purple-50 border border-purple-100 rounded-lg">
                      <div className="text-sm text-purple-700 font-medium">Location Factor</div>
                      <div className="text-lg font-bold text-purple-900 mt-1">
                        {careerInsightsResult.salary_insights.location_factor}
                      </div>
                    </div>
                  </div>

                  {/* Recommendations Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Recommended Roles */}
                    <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                      <h4 className="font-medium text-gray-900 mb-3">Recommended Roles</h4>
                      <ul className="space-y-2">
                        {careerInsightsResult.recommended_roles.map((role: string, idx: number) => (
                          <li key={idx} className="flex items-start space-x-2">
                            <CheckCircleIcon className="h-5 w-5 text-success-500 flex-shrink-0" />
                            <span className="text-gray-700">{role}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Skill Gaps */}
                    <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                      <h4 className="font-medium text-gray-900 mb-3">Skills to Acquire</h4>
                      <ul className="space-y-2">
                        {careerInsightsResult.skill_gaps.map((skill: string, idx: number) => (
                          <li key={idx} className="flex items-start space-x-2">
                            <LightBulbIcon className="h-5 w-5 text-warning-500 flex-shrink-0" />
                            <span className="text-gray-700">{skill}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Strategic Advice */}
                  <div className="p-4 bg-primary-50 border border-primary-100 rounded-lg">
                    <h4 className="font-medium text-primary-900 mb-3">Strategic Advice</h4>
                    <ul className="space-y-3">
                      {careerInsightsResult.strategic_advice.map((advice: string, idx: number) => (
                        <li key={idx} className="flex items-start space-x-2">
                          <SparklesIcon className="h-5 w-5 text-primary-600 flex-shrink-0 mt-0.5" />
                          <span className="text-primary-800">{advice}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
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
