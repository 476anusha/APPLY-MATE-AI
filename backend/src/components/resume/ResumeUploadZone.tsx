import React, { useState } from 'react';
import { FileUpload } from '../shared/FileUpload';
import { Sparkles, FileText } from 'lucide-react';

export interface ResumeUploadZoneProps {
  onUpload: (file: File, title: string) => Promise<void>;
  isLoading?: boolean;
  className?: string;
}

export const ResumeUploadZone: React.FC<ResumeUploadZoneProps> = ({
  onUpload,
  isLoading = false,
  className = '',
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile);
    setError(null);
    if (!title) {
      // Auto-populate title without extension
      const cleanName = selectedFile.name.replace(/\.[^/.]+$/, '');
      setTitle(cleanName);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please choose or drop a resume file first.');
      return;
    }
    const finalTitle = title.trim() || file.name.replace(/\.[^/.]+$/, '');
    try {
      await onUpload(file, finalTitle);
      setFile(null);
      setTitle('');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to upload resume.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className={`space-y-4 ${className}`}>
      <div className="space-y-1.5">
        <label className="block text-xs font-semibold text-slate-300">
          Resume Version Title
        </label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g. Senior Frontend Engineer - General (2026)"
          className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
        />
      </div>

      <FileUpload
        onFileSelect={handleFileSelect}
        isLoading={isLoading}
        error={error}
        label="Drop your resume here or click to browse"
        sublabel="Supports PDF and DOCX format up to 10MB"
      />

      {file && (
        <div className="flex items-center justify-between pt-2">
          <div className="text-xs text-slate-400 flex items-center gap-1.5">
            <FileText className="w-4 h-4 text-indigo-400" />
            <span className="font-medium text-slate-200">{file.name}</span> selected
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-950/40 transition-all disabled:opacity-50"
          >
            {isLoading ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                Parsing & Uploading...
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5" />
                Upload & Parse Resume
              </>
            )}
          </button>
        </div>
      )}
    </form>
  );
};
export default ResumeUploadZone;
