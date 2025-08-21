import React, { useState, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Card, 
  CardHeader, 
  CardBody, 
  Button, 
  Badge, 
  Modal, 
  Spinner
} from '../components';

import { resumeService, fileService } from '../services/api';
import type { Resume } from '../types';
import {
  PlusIcon,
  TrashIcon,
  StarIcon,
  DocumentTextIcon,
  EyeIcon,
  CloudArrowUpIcon,
} from '@heroicons/react/24/outline';

const Resumes: React.FC = () => {
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedResume, setSelectedResume] = useState<Resume | null>(null);

  const [isViewModalOpen, setIsViewModalOpen] = useState(false);

  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();


  // Fetch resumes
  const { data: resumes = [], isLoading } = useQuery({
    queryKey: ['resumes'],
    queryFn: resumeService.getResumes,
  });

  // Upload resume mutation
  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      try {
        const uploadResponse = await fileService.uploadFile(file, 'resume');
        
        const resumeData: Partial<Resume> = {
          filename: uploadResponse.filename,
          original_filename: file.name,
          file_path: uploadResponse.url,
          file_size: file.size,
          mime_type: file.type,
          file_type: file.type.split('/')[1],
          skills: [],
          experience_years: 0,
          education: [],
          certifications: [],
          is_default: resumes.length === 0,
        };

        return resumeService.uploadResume(file, resumeData);
      } catch (error) {
        console.error('Error uploading resume:', error);
        throw error;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] });
      console.log('Resume uploaded successfully!');
    },
    onError: (error) => {
      console.error('Upload error:', error);
      console.error('Failed to upload resume. Please try again.');
    },
  });

  // Delete resume mutation
  const deleteMutation = useMutation({
    mutationFn: resumeService.deleteResume,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] });
      console.log('Resume deleted successfully!');
    },
    onError: (error) => {
      console.error('Delete error:', error);
      console.error('Failed to delete resume. Please try again.');
    },
  });

  // Set default resume mutation
  const setDefaultMutation = useMutation({
    mutationFn: resumeService.setDefaultResume,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] });
      console.log('Default resume updated!');
    },
    onError: (error) => {
      console.error('Set default error:', error);
      console.error('Failed to update default resume. Please try again.');
    },
  });

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
      if (!allowedTypes.includes(file.type)) {
        alert('Please select a PDF, DOCX, or TXT file.');
        return;
      }
      
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB.');
        return;
      }
      
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (selectedFile) {
      uploadMutation.mutate(selectedFile);
    }
  };

  const handleDelete = (resumeId: string) => {
    if (window.confirm('Are you sure you want to delete this resume?')) {
      deleteMutation.mutate(resumeId);
    }
  };

  const handleSetDefault = (resumeId: string) => {
    setDefaultMutation.mutate(resumeId);
  };

  const getFileTypeIcon = (fileType: string) => {
    if (fileType.includes('pdf')) return '📄';
    if (fileType.includes('word') || fileType.includes('docx')) return '📝';
    if (fileType.includes('text') || fileType.includes('txt')) return '📄';
    return '📄';
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

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
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Resumes</h1>
          <p className="mt-2 text-gray-600">
            Manage your resumes and professional documents.
          </p>
        </div>
        <Button 
          variant="primary" 
          onClick={() => setIsUploadModalOpen(true)}
          className="flex items-center"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Upload Resume
        </Button>
      </div>

      {/* Resumes List */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-medium text-gray-900">Your Resumes</h3>
        </CardHeader>
        <CardBody>
          {resumes.length === 0 ? (
            <div className="text-center py-8">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No resumes yet</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by uploading your first resume.
              </p>
              <Button 
                variant="primary" 
                onClick={() => setIsUploadModalOpen(true)}
                className="mt-4"
              >
                Upload Resume
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {resumes.map((resume) => (
                <div
                  key={resume.id}
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0">
                        <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center text-2xl">
                          {getFileTypeIcon(resume.file_type || 'pdf')}
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          <h4 className="text-lg font-medium text-gray-900">
                            {resume.title}
                          </h4>
                          {resume.is_default && (
                            <Badge variant="success" className="flex items-center">
                              <StarIcon className="h-3 w-3 mr-1" />
                              Default
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-500 mt-1">
                          {formatFileSize(resume.file_size)} • {resume.file_type}
                        </p>
                        {resume.skills && resume.skills.length > 0 && (
                          <div className="flex flex-wrap gap-2 mt-2">
                            {resume.skills.slice(0, 5).map((skill, index) => (
                              <Badge key={index} variant="secondary" size="sm">
                                {skill}
                              </Badge>
                            ))}
                            {resume.skills.length > 5 && (
                              <Badge variant="secondary" size="sm">
                                +{resume.skills.length - 5} more
                              </Badge>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setSelectedResume(resume);
                          setIsViewModalOpen(true);
                        }}
                      >
                        <EyeIcon className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleSetDefault(resume.id)}
                        disabled={resume.is_default}
                        className={resume.is_default ? 'text-gray-400' : 'text-primary-600 hover:text-primary-700'}
                      >
                        <StarIcon className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(resume.id)}
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

      {/* Upload Resume Modal */}
      <Modal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        title="Upload Resume"
        size="lg"
      >
        <div className="space-y-6">
          {/* File Upload Area */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-400 transition-colors">
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={handleFileSelect}
              className="hidden"
            />
            
            {!selectedFile ? (
              <div>
                <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
                <div className="mt-4">
                  <Button
                    variant="secondary"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    Select File
                  </Button>
                  <p className="mt-2 text-sm text-gray-500">
                    or drag and drop
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    PDF, DOCX, or TXT up to 10MB
                  </p>
                </div>
              </div>
            ) : (
              <div>
                <DocumentTextIcon className="mx-auto h-12 w-12 text-primary-600" />
                <div className="mt-4">
                  <p className="text-sm font-medium text-gray-900">
                    {selectedFile.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(selectedFile.size)}
                  </p>
                  <div className="mt-4">
                    <Button
                      variant="primary"
                      onClick={handleUpload}
                      loading={uploadMutation.isPending}
                    >
                      Upload Resume
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={() => setSelectedFile(null)}
                      className="ml-2"
                    >
                      Change File
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Upload Progress */}
          {uploadMutation.isPending && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white p-6 rounded-lg">
                <Spinner size="lg" />
                <p className="mt-4 text-center">Uploading resume...</p>
              </div>
            </div>
          )}
        </div>
      </Modal>

      {/* View Resume Modal */}
      <Modal
        isOpen={isViewModalOpen}
        onClose={() => setIsViewModalOpen(false)}
        title="Resume Details"
        size="xl"
      >
        {selectedResume && (
          <div className="space-y-6">
            {/* Resume Header */}
            <div className="border-b border-gray-200 pb-4">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-primary-100 rounded-lg flex items-center justify-center text-3xl">
                  {getFileTypeIcon(selectedResume.file_type || 'pdf')}
                </div>
                <div>
                  <h3 className="text-xl font-medium text-gray-900">
                    {selectedResume.title}
                  </h3>
                  <p className="text-gray-600">
                    {formatFileSize(selectedResume.file_size)} • {selectedResume.file_type}
                  </p>
                  {selectedResume.is_default && (
                    <Badge variant="success" className="mt-2">
                      Default Resume
                    </Badge>
                  )}
                </div>
              </div>
            </div>

            {/* Resume Content */}
            <div className="space-y-6">
              {/* Skills */}
              {selectedResume.skills && selectedResume.skills.length > 0 && (
                <div>
                  <h4 className="text-lg font-medium text-gray-900 mb-3">Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedResume.skills.map((skill, index) => (
                      <Badge key={index} variant="primary">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Experience */}
              {selectedResume.experience_years && selectedResume.experience_years > 0 && (
                <div>
                  <h4 className="text-lg font-medium text-gray-900 mb-3">Experience</h4>
                  <p className="text-gray-600">
                    {selectedResume.experience_years} years of professional experience
                  </p>
                </div>
              )}

              {/* Education */}
              {selectedResume.education && selectedResume.education.length > 0 && (
                <div>
                  <h4 className="text-lg font-medium text-gray-900 mb-3">Education</h4>
                  <div className="space-y-2">
                    {selectedResume.education.map((edu, index) => (
                      <div key={index} className="text-gray-600">
                        <p className="font-medium">{edu.degree}</p>
                        <p className="text-sm">{edu.institution} • {edu.year}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Certifications */}
              {selectedResume.certifications && selectedResume.certifications.length > 0 && (
                <div>
                  <h4 className="text-lg font-medium text-gray-900 mb-3">Certifications</h4>
                  <div className="space-y-2">
                    {selectedResume.certifications.map((cert, index) => (
                      <div key={index} className="text-gray-600">
                        <p className="font-medium">{cert.name}</p>
                        <p className="text-sm">{cert.issuer} • {cert.year}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
              <Button
                variant="secondary"
                onClick={() => setIsViewModalOpen(false)}
              >
                Close
              </Button>
              {!selectedResume.is_default && (
                <Button
                  variant="primary"
                  onClick={() => {
                    handleSetDefault(selectedResume.id);
                    setIsViewModalOpen(false);
                  }}
                >
                  Set as Default
                </Button>
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Resumes;
