import React, { useState } from 'react';
import { X, Sparkles, Copy, Check, Download, FileText } from 'lucide-react';
import { TONE_OPTIONS } from '../../utils/constants';

export interface CoverLetterModalProps {
  isOpen: boolean;
  onClose: () => void;
  jobTitle?: string;
  company?: string;
  initialContent?: string;
  onGenerate?: (tone: string) => Promise<string | void>;
  onSave?: (content: string, tone: string) => void;
  isGenerating?: boolean;
}

export const CoverLetterModal: React.FC<CoverLetterModalProps> = ({
  isOpen,
  onClose,
  jobTitle = 'Position',
  company = 'Company',
  initialContent = '',
  onGenerate,
  onSave,
  isGenerating = false,
}) => {
  const [content, setContent] = useState(initialContent);
  const [selectedTone, setSelectedTone] = useState('professional');
  const [copied, setCopied] = useState(false);

  React.useEffect(() => {
    if (initialContent) {
      setContent(initialContent);
    }
  }, [initialContent]);

  if (!isOpen) return null;

  const handleCopy = () => {
    if (!content) return;
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!content) return;
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Cover_Letter_${company.replace(/\s+/g, '_')}_${jobTitle.replace(/\s+/g, '_')}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleGenerateClick = async () => {
    if (onGenerate) {
      const generated = await onGenerate(selectedTone);
      if (typeof generated === 'string') {
        setContent(generated);
      }
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-3xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden text-slate-100">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/80">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Cover Letter Generator</h2>
              <p className="text-xs text-slate-400">
                Tailored for <span className="text-slate-200 font-medium">{jobTitle}</span> at{' '}
                <span className="text-slate-200 font-medium">{company}</span>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tone Selector & Options */}
        <div className="px-6 py-4 border-b border-slate-800/80 bg-slate-950/40">
          <label className="block text-xs font-semibold text-slate-300 mb-2">
            Select Writing Tone
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {TONE_OPTIONS.map((tone) => (
              <button
                key={tone.value}
                type="button"
                onClick={() => setSelectedTone(tone.value)}
                className={`px-3 py-2 text-xs font-medium rounded-xl border text-left transition-all ${
                  selectedTone === tone.value
                    ? 'bg-purple-600/20 border-purple-500 text-purple-300 shadow-sm'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
                }`}
              >
                <div className="font-semibold">{tone.label}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Content Area */}
        <div className="p-6 flex-1 overflow-y-auto">
          {isGenerating ? (
            <div className="h-64 flex flex-col items-center justify-center space-y-4 text-center">
              <div className="relative">
                <div className="w-12 h-12 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 animate-pulse">
                  <Sparkles className="w-6 h-6 animate-spin text-purple-400" />
                </div>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-slate-200">
                  AI is crafting your tailored cover letter...
                </p>
                <p className="text-xs text-slate-400">
                  Highlighting relevant experience and matching role keywords
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Edit your cover letter directly:</span>
                <span>{content ? content.trim().split(/\s+/).length : 0} words</span>
              </div>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                rows={14}
                placeholder="Click 'Generate with AI' below or paste your cover letter here..."
                className="w-full rounded-xl bg-slate-950 border border-slate-800 p-4 text-sm text-slate-200 font-sans leading-relaxed focus:border-purple-500 focus:outline-none resize-none transition-colors"
              />
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-900 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleGenerateClick}
              disabled={isGenerating}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white shadow-md shadow-purple-950/40 transition-all disabled:opacity-50"
            >
              <Sparkles className="w-3.5 h-3.5" />
              {content ? 'Regenerate with AI' : 'Generate with AI'}
            </button>
          </div>

          <div className="flex items-center gap-2">
            {content && (
              <>
                <button
                  type="button"
                  onClick={handleCopy}
                  className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors"
                >
                  {copied ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" /> Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" /> Copy
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={handleDownload}
                  className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors"
                >
                  <Download className="w-3.5 h-3.5" /> Download
                </button>
              </>
            )}
            <button
              type="button"
              onClick={() => {
                if (onSave && content) onSave(content, selectedTone);
                onClose();
              }}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors"
            >
              Save & Use
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
export default CoverLetterModal;
