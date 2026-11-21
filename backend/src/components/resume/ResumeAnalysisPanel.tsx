import React from 'react';
import { ResumeAnalysisResponse } from '../../types';
import { ScoreDisplay } from './ScoreDisplay';
import { CheckCircle, AlertCircle, Lightbulb, FileSearch, Sparkles } from 'lucide-react';

export interface ResumeAnalysisPanelProps {
  analysis?: ResumeAnalysisResponse | null;
  isLoading?: boolean;
  onReanalyze?: () => void;
  className?: string;
}

export const ResumeAnalysisPanel: React.FC<ResumeAnalysisPanelProps> = ({
  analysis,
  isLoading = false,
  onReanalyze,
  className = '',
}) => {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
        <Sparkles className="w-10 h-10 text-indigo-400 animate-spin" />
        <div className="space-y-1">
          <h4 className="text-base font-semibold text-white">Analyzing Resume with AI</h4>
          <p className="text-xs text-slate-400 max-w-sm">
            Scanning ATS keyword density, formatting parameters, experience clarity, and impact statements...
          </p>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="p-8 text-center rounded-2xl bg-slate-900/40 border border-slate-800 space-y-3">
        <FileSearch className="w-10 h-10 text-slate-600 mx-auto" />
        <h4 className="text-sm font-semibold text-slate-300">No Analysis Done Yet</h4>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          Run an AI scan to score your resume against ATS algorithms, detect formatting issues, and discover high-impact keyword optimizations.
        </p>
        {onReanalyze && (
          <button
            type="button"
            onClick={onReanalyze}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors"
          >
            Analyze with AI
          </button>
        )}
      </div>
    );
  }

  const overallScore = analysis.score ?? analysis.overall_score ?? 0;
  const weaknesses = analysis.weaknesses ?? analysis.improvements ?? [];
  const suggestions = analysis.suggestions ?? analysis.improvements ?? [];
  const missingKeywords = analysis.missing_keywords ?? [];

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Visual Score and Radar */}
      <ScoreDisplay
        overallScore={overallScore}
        sectionScores={analysis.section_scores}
      />

      {/* Strengths & Weaknesses Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Strengths */}
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-emerald-400">
            <CheckCircle className="w-4 h-4" />
            <h4 className="text-xs font-bold uppercase tracking-wider">
              Profile Strengths ({analysis.strengths?.length ?? 0})
            </h4>
          </div>
          <ul className="space-y-2 text-xs text-slate-300">
            {analysis.strengths?.map((str: string, i: number) => (
              <li key={i} className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0 mt-1.5" />
                <span className="leading-relaxed">{str}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Weaknesses */}
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-amber-400">
            <AlertCircle className="w-4 h-4" />
            <h4 className="text-xs font-bold uppercase tracking-wider">
              Areas to Improve ({weaknesses.length})
            </h4>
          </div>
          <ul className="space-y-2 text-xs text-slate-300">
            {weaknesses.map((weak: string, i: number) => (
              <li key={i} className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0 mt-1.5" />
                <span className="leading-relaxed">{weak}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* AI Suggestions */}
      {suggestions.length > 0 && (
        <div className="p-5 rounded-2xl bg-gradient-to-br from-indigo-950/40 to-purple-950/20 border border-indigo-500/20 space-y-3">
          <div className="flex items-center gap-2 text-indigo-300">
            <Lightbulb className="w-4 h-4 text-indigo-400" />
            <h4 className="text-xs font-bold uppercase tracking-wider">Actionable AI Recommendations</h4>
          </div>
          <div className="space-y-2.5">
            {suggestions.map((sug: string, idx: number) => (
              <div key={idx} className="flex items-start gap-3 p-3 rounded-xl bg-slate-900/70 border border-slate-800 text-xs text-slate-200">
                <span className="w-5 h-5 rounded-lg bg-indigo-500/20 text-indigo-300 font-bold flex items-center justify-center shrink-0 text-[10px]">
                  {idx + 1}
                </span>
                <p className="leading-relaxed">{sug}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Missing Keywords */}
      {missingKeywords.length > 0 && (
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Missing Keywords ({missingKeywords.length})
          </h4>
          <div className="flex flex-wrap gap-1.5">
            {missingKeywords.map((kw: string, i: number) => (
              <span key={i} className="px-2 py-0.5 rounded-md bg-rose-500/10 text-rose-300 border border-rose-500/20 text-xs">
                + {kw}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
export default ResumeAnalysisPanel;
