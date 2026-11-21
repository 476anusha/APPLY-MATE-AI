import React from 'react';
import { Resume } from '../../types';
import { formatDate, formatFileSize } from '../../utils/formatters';
import {
  FileText,
  Star,
  Sparkles,
  Trash2,
  ExternalLink,
  ShieldCheck,
  MoreVertical,
  Check,
} from 'lucide-react';

export interface ResumeCardProps {
  resume: Resume;
  onAnalyze: (resume: Resume) => void;
  onSetDefault: (resume: Resume) => void;
  onDelete: (resume: Resume) => void;
  onView: (resume: Resume) => void;
  isAnalyzing?: boolean;
}

function scoreColorClass(score: number) {
  if (score >= 80) return { bg: 'bg-emerald-500/15', text: 'text-emerald-400', border: 'border-emerald-500/30' };
  if (score >= 60) return { bg: 'bg-amber-500/15', text: 'text-amber-400', border: 'border-amber-500/30' };
  return { bg: 'bg-rose-500/15', text: 'text-rose-400', border: 'border-rose-500/30' };
}

export const ResumeCard: React.FC<ResumeCardProps> = ({
  resume,
  onAnalyze,
  onSetDefault,
  onDelete,
  onView,
  isAnalyzing = false,
}) => {
  const [menuOpen, setMenuOpen] = React.useState(false);
  const displayScore = resume.overall_score;
  const scoreInfo = displayScore !== undefined ? scoreColorClass(displayScore) : null;
  const isDefault = resume.is_default || resume.is_primary;

  return (
    <div className="relative group rounded-2xl border border-slate-800 bg-slate-900/70 hover:border-slate-700 hover:bg-slate-900 transition-all p-5 flex flex-col justify-between space-y-4 shadow-sm hover:shadow-xl">
      {/* Top row */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3.5">
          <div className="w-11 h-11 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shrink-0">
            <FileText className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-sm font-bold text-white group-hover:text-indigo-300 transition-colors">
                {resume.title || resume.file_name}
              </h3>
              {isDefault && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/15 text-amber-400 border border-amber-500/30">
                  <Star className="w-2.5 h-2.5 fill-amber-400" /> Default
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 truncate max-w-[200px] sm:max-w-[240px]">
              {resume.file_name}
            </p>
          </div>
        </div>

        {/* Action Dropdown */}
        <div className="relative">
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            aria-label="Resume options"
          >
            <MoreVertical className="w-4 h-4" />
          </button>

          {menuOpen && (
            <>
              <div className="fixed inset-0 z-20" onClick={() => setMenuOpen(false)} />
              <div className="absolute right-0 top-8 z-30 w-44 rounded-xl bg-slate-950 border border-slate-800 p-1.5 shadow-2xl text-xs text-slate-300">
                <button
                  type="button"
                  onClick={() => { setMenuOpen(false); onView(resume); }}
                  className="w-full text-left px-3 py-2 rounded-lg hover:bg-slate-800 hover:text-white flex items-center gap-2"
                >
                  <ExternalLink className="w-3.5 h-3.5" /> View Parsed Data
                </button>
                {!isDefault && (
                  <button
                    type="button"
                    onClick={() => { setMenuOpen(false); onSetDefault(resume); }}
                    className="w-full text-left px-3 py-2 rounded-lg hover:bg-slate-800 hover:text-white flex items-center gap-2"
                  >
                    <Check className="w-3.5 h-3.5" /> Set as Default
                  </button>
                )}
                {resume.file_url && resume.file_url !== '#' && (
                  <a
                    href={resume.file_url}
                    target="_blank"
                    rel="noreferrer"
                    className="w-full text-left px-3 py-2 rounded-lg hover:bg-slate-800 hover:text-white flex items-center gap-2"
                  >
                    <FileText className="w-3.5 h-3.5" /> Download File
                  </a>
                )}
                <div className="h-px bg-slate-800 my-1" />
                <button
                  type="button"
                  onClick={() => { setMenuOpen(false); onDelete(resume); }}
                  className="w-full text-left px-3 py-2 rounded-lg hover:bg-rose-500/20 text-rose-400 flex items-center gap-2"
                >
                  <Trash2 className="w-3.5 h-3.5" /> Delete
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Score & Date Row */}
      <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-xs">
        <div className="flex items-center gap-2">
          {displayScore !== undefined && displayScore !== null && scoreInfo ? (
            <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border font-bold ${scoreInfo.bg} ${scoreInfo.text} ${scoreInfo.border}`}>
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Score {displayScore}%</span>
            </div>
          ) : (
            <span className="text-slate-500 text-[11px]">Not analyzed yet</span>
          )}
        </div>
        <div className="text-right text-[11px] text-slate-400">
          <div>{formatDate(resume.created_at)}</div>
          {resume.file_size && <div>{formatFileSize(resume.file_size)}</div>}
        </div>
      </div>

      {/* Footer Actions */}
      <div className="flex items-center gap-2 pt-1">
        {displayScore ? (
          <>
            <button
              type="button"
              onClick={() => onView(resume)}
              className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md transition-all"
            >
              <Sparkles className="w-3.5 h-3.5" />
              View Analysis
            </button>
            <button
              type="button"
              onClick={() => onAnalyze(resume)}
              disabled={isAnalyzing}
              className="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-all disabled:opacity-50"
              title="Re-run AI Analysis"
            >
              {isAnalyzing ? (
                <span className="w-3 h-3 border-2 border-indigo-400/20 border-t-indigo-400 rounded-full animate-spin" />
              ) : (
                'Re-analyze'
              )}
            </button>
          </>
        ) : (
          <>
            <button
              type="button"
              onClick={() => onAnalyze(resume)}
              disabled={isAnalyzing}
              className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md transition-all disabled:opacity-50"
            >
              {isAnalyzing ? (
                <span className="w-3 h-3 border-2 border-white/20 border-t-white rounded-full animate-spin" />
              ) : (
                <Sparkles className="w-3.5 h-3.5 text-white" />
              )}
              Analyze with AI
            </button>
            <button
              type="button"
              onClick={() => onView(resume)}
              className="px-3 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors"
            >
              Details
            </button>
          </>
        )}
      </div>
    </div>
  );
};
export default ResumeCard;
