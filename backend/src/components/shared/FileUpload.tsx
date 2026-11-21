import React, { useState } from 'react';
import { useDropzone, DropzoneOptions } from 'react-dropzone';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, X } from 'lucide-react';
import { formatFileSize } from '../../utils/formatters';

export interface FileUploadProps {
  onFileSelect: (file: File) => void;
  accept?: Record<string, string[]>;
  maxSize?: number; // in bytes
  isLoading?: boolean;
  progress?: number;
  error?: string | null;
  label?: string;
  sublabel?: string;
  className?: string;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  accept = {
    'application/pdf': ['.pdf'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  },
  maxSize = 10 * 1024 * 1024, // 10MB
  isLoading = false,
  progress,
  error: externalError,
  label = 'Upload your resume or document',
  sublabel = 'Supports PDF and DOCX files up to 10MB',
  className = '',
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);

  const dropzoneOptions: DropzoneOptions = {
    accept,
    maxSize,
    multiple: false,
    disabled: isLoading,
    onDrop: (acceptedFiles, fileRejections) => {
      setFileError(null);
      if (fileRejections.length > 0) {
        const rejection = fileRejections[0];
        if (rejection.errors[0]?.code === 'file-too-large') {
          setFileError(`File exceeds maximum size of ${formatFileSize(maxSize)}.`);
        } else {
          setFileError(rejection.errors[0]?.message || 'Invalid file format.');
        }
        return;
      }

      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        setSelectedFile(file);
        onFileSelect(file);
      }
    },
  };

  const { getRootProps, getInputProps, isDragActive, isDragReject } =
    useDropzone(dropzoneOptions);

  const clearFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedFile(null);
    setFileError(null);
  };

  const currentError = externalError || fileError;

  return (
    <div className={`space-y-3 ${className}`}>
      <div
        {...getRootProps()}
        className={`relative flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-2xl cursor-pointer transition-all ${
          isDragActive
            ? 'border-indigo-500 bg-indigo-500/10'
            : isDragReject
            ? 'border-rose-500 bg-rose-500/10'
            : 'border-slate-800 hover:border-slate-700 bg-slate-900/50 hover:bg-slate-900/80'
        } ${isLoading ? 'pointer-events-none opacity-80' : ''}`}
      >
        <input {...getInputProps()} />

        {selectedFile ? (
          <div className="flex flex-col items-center text-center space-y-3">
            <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <FileText className="w-7 h-7" />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-semibold text-white break-all max-w-xs">
                {selectedFile.name}
              </p>
              <p className="text-xs text-slate-400">
                {formatFileSize(selectedFile.size)}
              </p>
            </div>

            {isLoading ? (
              <div className="w-48 space-y-2 mt-2">
                <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-indigo-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress ?? 65}%` }}
                  />
                </div>
                <p className="text-xs text-indigo-300">
                  {progress ? `Uploading... ${progress}%` : 'Processing file...'}
                </p>
              </div>
            ) : (
              <div className="flex items-center gap-2 pt-1">
                <span className="flex items-center gap-1 text-xs text-emerald-400 font-medium">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Ready for upload
                </span>
                <button
                  type="button"
                  onClick={clearFile}
                  className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
                  title="Remove file"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center text-center space-y-3">
            <div className="w-14 h-14 rounded-2xl bg-slate-800/80 border border-slate-700/60 flex items-center justify-center text-slate-400 group-hover:text-indigo-400 transition-colors">
              <UploadCloud className="w-7 h-7 text-indigo-400" />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-slate-200">
                {isDragActive ? 'Drop your file right here' : label}
              </p>
              <p className="text-xs text-slate-400">{sublabel}</p>
            </div>
            <span className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-indigo-600/10 text-indigo-400 border border-indigo-500/20">
              Browse from device
            </span>
          </div>
        )}
      </div>

      {currentError && (
        <div className="flex items-center gap-2 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-400">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{currentError}</span>
        </div>
      )}
    </div>
  );
};
export default FileUpload;
