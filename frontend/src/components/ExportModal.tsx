import React, { useState } from 'react';
import Modal from './ui/Modal';
import Button from './ui/Button';
import Select from './ui/Select';
import Alert from './ui/Alert';
import Spinner from './ui/Spinner';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';

export interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onExport: (format: 'pdf' | 'csv' | 'excel', options?: any) => Promise<void>;
  title?: string;
  supportedFormats?: string[];
  showDateRange?: boolean;
  defaultFormat?: 'pdf' | 'csv' | 'excel';
}

export const ExportModal: React.FC<ExportModalProps> = ({
  isOpen,
  onClose,
  onExport,
  title = 'Export Data',
  supportedFormats = ['pdf', 'csv', 'excel'],
  showDateRange = false,
  defaultFormat = 'csv',
}) => {
  const [format, setFormat] = useState<'pdf' | 'csv' | 'excel'>(defaultFormat);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExport = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setIsExporting(true);
    setError(null);

    try {
      const options = showDateRange ? { dateFrom, dateTo } : undefined;
      await onExport(format, options);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Export failed. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const formatOptions = [
    { value: 'pdf', label: 'PDF', disabled: !supportedFormats.includes('pdf') },
    { value: 'csv', label: 'CSV', disabled: !supportedFormats.includes('csv') },
    { value: 'excel', label: 'Excel', disabled: !supportedFormats.includes('excel') },
  ].filter(opt => !opt.disabled);

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title}>
      <div className="space-y-4">
        {error && (
          <Alert type="error" title="Export Error" message={error} />
        )}

        <form onSubmit={handleExport} className="space-y-4">
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Export Format</label>
            <Select
              name="format"
              value={format}
              onChange={(value) => setFormat(value as 'pdf' | 'csv' | 'excel')}
              options={formatOptions}
            />
          </div>

          {showDateRange && (
            <>
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Date From</label>
                <input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Date To</label>
                <input
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </>
          )}

          <div className="flex justify-end space-x-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
              disabled={isExporting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={isExporting}
              className="flex items-center"
            >
              {isExporting ? (
                <>
                  <Spinner size="sm" className="mr-2" />
                  Exporting...
                </>
              ) : (
                <>
                  <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                  Export
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
};
