import React, { useRef, useState } from 'react';
import { useForm, FormProvider } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { resumeSchema, ResumeFormData } from '../../schemas';
import { Button, Spinner } from '../ui';
import FormField from './FormField';
import { CloudArrowUpIcon, DocumentTextIcon } from '@heroicons/react/24/outline';

interface ResumeUploadFormProps {
  onSubmit: (data: ResumeFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

const ResumeUploadForm: React.FC<ResumeUploadFormProps> = ({
  onSubmit,
  onCancel,
  isLoading = false,
}) => {
  const methods = useForm<ResumeFormData>({
    resolver: zodResolver(resumeSchema),
    defaultValues: {
      title: '',
    },
  });

  const {
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
    trigger,
  } = methods;

  const fileInputRef = useRef<HTMLInputElement>(null);
  const selectedFile = watch('file');
  const [dragActive, setDragActive] = useState(false);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      validateAndSetFile(file);
    }
  };

  const validateAndSetFile = (file: File) => {
    // Validate file type
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain',
    ];
    if (!allowedTypes.includes(file.type)) {
      alert('Please select a PDF, DOCX, or TXT file.');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB.');
      return;
    }

    setValue('file', file, { shouldValidate: true });
    
    // Auto-fill title if empty
    const currentTitle = methods.getValues('title');
    if (!currentTitle) {
      // Remove extension and underscores/hyphens
      const name = file.name.replace(/\.[^/.]+$/, "").replace(/[-_]/g, " ");
      // Capitalize first letters
      const formattedName = name.replace(/\b\w/g, c => c.toUpperCase());
      setValue('title', formattedName, { shouldValidate: true });
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          name="title"
          label="Resume Title"
          placeholder="e.g. Full Stack Developer 2024"
          required
        />

        {/* File Upload Area */}
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-700">
            Resume File <span className="text-danger-500">*</span>
          </label>
          <div
            className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
              dragActive
                ? 'border-primary-500 bg-primary-50'
                : errors.file
                ? 'border-danger-300 hover:border-danger-400'
                : 'border-gray-300 hover:border-primary-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
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
                    type="button"
                    variant="secondary"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    Select File
                  </Button>
                  <p className="mt-2 text-sm text-gray-500">or drag and drop</p>
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
                    {(selectedFile as File).name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {formatFileSize((selectedFile as File).size)}
                  </p>
                  <div className="mt-4">
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={() => setValue('file', null as any, { shouldValidate: true })}
                      className="ml-2"
                    >
                      Change File
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>
          {errors.file && (
            <p className="text-sm text-danger-600">{errors.file.message as string}</p>
          )}
        </div>

        {/* Upload Progress Overlay */}
        {isLoading && (
          <div className="absolute inset-0 bg-white/50 flex items-center justify-center z-10">
            <Spinner size="lg" />
          </div>
        )}

        <div className="flex justify-end space-x-3">
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" loading={isLoading}>
            Upload Resume
          </Button>
        </div>
      </form>
    </FormProvider>
  );
};

export default ResumeUploadForm;
