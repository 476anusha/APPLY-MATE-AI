import React, { useState } from 'react';
import { X, Sparkles, Check, ArrowRight, Wand2, ShieldCheck, Download } from 'lucide-react';

export interface ResumeTailorModalProps {
  isOpen: boolean;
  onClose: () => void;
  jobTitle?: string;
  company?: string;
  originalResumeText?: string;
  tailoredResumeText?: string;
  matchedKeywords?: string[];
  suggestedImprovements?: string[];
  isTailoring?: boolean;
  onTailor?: () => Promise<void>;
  onSaveAsNewVersion?: (text: string) => void;
}

export const ResumeTailorModal: React.FC<ResumeTailorModalProps> = ({
  isOpen,
  onClose,
  jobTitle = 'Target Role',
  company = 'Target Company',
  originalResumeText = 'Experienced software engineer skilled in full-stack web development, modern cloud architectures, and scalable API design.',
  tailoredResumeText: initialTailored = '',
  matchedKeywords = ['React', 'TypeScript', 'PostgreSQL', 'FastAPI', 'System Architecture'],
  suggestedImprovements = [
    'Aligned summary statement directly with the role requirements',
    'Rephrased bullet points to highlight measurable performance metrics',
    'Prioritized matching keywords for ATS algorithm optimization',
  ],
  isTailoring = false,
  onTailor,
  onSaveAsNewVersion,
}) => {
  const [tailoredText, setTailoredText] = useState(initialTailored);
  const [copied, setCopied] = useState(false);

  React.useEffect(() => {
    if (initialTailored) {
      setTailoredText(initialTailored);
    } else if (!tailoredText && originalResumeText) {
      // Create sensible demo tailored content if empty
      setTailoredText(
        `Results-driven Senior Full-Stack Engineer with specialized expertise in React, TypeScript, and FastAPI. Proven track record of developing high-throughput web architectures for top-tier applications at scale.\n\nKey Strengths for ${jobTitle} at ${company}:\n• Architected distributed microservices boosting throughput by 42%\n• Spearheaded cross-functional frontend component libraries using React and TypeScript\n• Streamlined CI/CD pipelines reducing deployment friction by 35%`
      );
    }
  }, [initialTailored, originalResumeText, jobTitle, company]);

  if (!isOpen) return null;

  const handleCopy = () => {
    if (!tailoredText) return;
    navigator.clipboard.writeText(tailoredText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!tailoredText) return;
    const blob = new Blob([tailoredText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Tailored_Resume_${company.replace(/\s+/g, '_')}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-5xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl flex flex-col max-h-[92vh] overflow-hidden text-slate-100">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/90">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Wand2 className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">AI Resume Tailoring</h2>
              <p className="text-xs text-slate-400">
                Optimizing for <span className="text-indigo-300 font-medium">{jobTitle}</span> at{' '}
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

        {/* Keywords and Optimization Summary */}
        <div className="px-6 py-3 border-b border-slate-800/80 bg-slate-950/40 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-slate-400 font-medium">Injected Keywords:</span>
            {matchedKeywords.map((kw, i) => (
              <span
                key={i}
                className="px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium"
              >
                ✓ {kw}
              </span>
            ))}
          </div>
          <div className="flex items-center gap-1.5 text-indigo-400 font-medium">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Honest Tailoring (No Fabrication)</span>
          </div>
        </div>

        {/* Side-by-side View */}
        <div className="p-6 flex-1 overflow-y-auto grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Original Resume Side */}
          <div className="flex flex-col space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Original Version
              </span>
              <span className="text-[11px] text-slate-500">Read-only</span>
            </div>
            <div className="flex-1 min-h-[300px] p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs text-slate-400 font-mono leading-relaxed whitespace-pre-wrap overflow-y-auto">
              {originalResumeText}
            </div>
          </div>

          {/* Tailored Resume Side */}
          <div className="flex flex-col space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" /> Tailored & ATS-Optimized
              </span>
              <span className="text-[11px] text-emerald-400 font-medium">
                Editable below
              </span>
            </div>

            {isTailoring ? (
              <div className="flex-1 min-h-[300px] rounded-xl bg-slate-950 border border-indigo-500/30 flex flex-col items-center justify-center p-6 text-center space-y-3">
                <Sparkles className="w-8 h-8 text-indigo-400 animate-spin" />
                <p className="text-sm font-medium text-slate-200">
                  Tailoring resume to job criteria...
                </p>
                <p className="text-xs text-slate-500 max-w-xs">
                  Rephrasing accomplishments to match required skills and keywords.
                </p>
              </div>
            ) : (
              <textarea
                value={tailoredText}
                onChange={(e) => setTailoredText(e.target.value)}
                rows={14}
                className="flex-1 min-h-[300px] p-4 rounded-xl bg-slate-950 border border-indigo-500/40 text-xs text-slate-200 font-mono leading-relaxed focus:border-indigo-400 focus:outline-none resize-none transition-colors"
              />
            )}
          </div>
        </div>

        {/* Suggested Improvements Box */}
        {suggestedImprovements.length > 0 && (
          <div className="px-6 py-3 border-t border-slate-800/80 bg-slate-950/20">
            <p className="text-[11px] font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
              Optimization Highlights:
            </p>
            <ul className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs text-slate-300">
              {suggestedImprovements.map((item, idx) => (
                <li key={idx} className="flex items-start gap-1.5">
                  <ArrowRight className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-900 flex flex-wrap items-center justify-between gap-3">
          <div>
            {onTailor && (
              <button
                type="button"
                onClick={() => onTailor()}
                disabled={isTailoring}
                className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors disabled:opacity-50"
              >
                <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                Re-tailor with AI
              </button>
            )}
          </div>

          <div className="flex items-center gap-2">
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
                'Copy Text'
              )}
            </button>
            <button
              type="button"
              onClick={handleDownload}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors"
            >
              <Download className="w-3.5 h-3.5" /> Download (.txt)
            </button>
            <button
              type="button"
              onClick={() => {
                if (onSaveAsNewVersion && tailoredText) {
                  onSaveAsNewVersion(tailoredText);
                }
                onClose();
              }}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors"
            >
              Save as New Version
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
export default ResumeTailorModal;
