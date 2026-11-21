import React from 'react';
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, ResponsiveContainer,
} from 'recharts';
import { ShieldCheck } from 'lucide-react';

export interface ScoreDisplayProps {
  overallScore: number;
  sectionScores?: Record<string, number>;
  size?: 'sm' | 'md' | 'lg';
  showRadar?: boolean;
}

function getScoreStyle(score: number) {
  if (score >= 80) return { stroke: '#10b981', bg: 'bg-emerald-500/15', text: 'text-emerald-400', border: 'border-emerald-500/30', label: 'Excellent' };
  if (score >= 65) return { stroke: '#f59e0b', bg: 'bg-amber-500/15', text: 'text-amber-400', border: 'border-amber-500/30', label: 'Good' };
  return { stroke: '#ef4444', bg: 'bg-rose-500/15', text: 'text-rose-400', border: 'border-rose-500/30', label: 'Needs Work' };
}

export const ScoreDisplay: React.FC<ScoreDisplayProps> = ({
  overallScore,
  sectionScores,
  showRadar = true,
}) => {
  const style = getScoreStyle(overallScore);
  const circumference = 2 * Math.PI * 38;
  const strokeDashoffset = circumference - (overallScore / 100) * circumference;

  const radarData = sectionScores
    ? Object.entries(sectionScores).map(([key, val]) => ({
        subject: key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
        score: val,
        fullMark: 100,
      }))
    : [];

  const sectionLabels: Record<string, string> = {
    contact_info: 'Contact Info',
    summary: 'Professional Summary',
    experience: 'Work Experience',
    skills: 'Skills & Keywords',
    education: 'Education',
    formatting: 'ATS Formatting',
    projects: 'Projects',
  };

  return (
    <div className="space-y-6">
      {/* Overall Score Banner */}
      <div className="flex flex-col sm:flex-row items-center gap-6 p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
        <div className="relative flex items-center justify-center shrink-0">
          <svg className="w-28 h-28 transform -rotate-90" viewBox="0 0 96 96">
            <circle cx="48" cy="48" r="38" className="stroke-slate-800" strokeWidth="7" fill="transparent" />
            <circle
              cx="48" cy="48" r="38"
              stroke={style.stroke}
              strokeWidth="7"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              fill="transparent"
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
            <span className="text-2xl font-black text-white">{overallScore}</span>
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">/ 100</span>
          </div>
        </div>

        <div className="space-y-2 text-center sm:text-left flex-1">
          <div className="flex items-center justify-center sm:justify-start gap-2">
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${style.bg} ${style.text} ${style.border}`}>
              {style.label}
            </span>
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" /> ATS Compatibility Score
            </span>
          </div>
          <h4 className="text-base font-bold text-white">
            {overallScore >= 80 ? 'Excellent ATS Profile'
              : overallScore >= 65 ? 'Competitive, with Room for Polish'
              : 'Needs Keyword & Structure Optimization'}
          </h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            {overallScore >= 80
              ? 'Your resume incorporates key technical skills and action verbs that pass modern applicant tracking systems.'
              : overallScore >= 65
              ? 'Good foundation! Addressing missing keywords and formatting will increase recruiter response rates.'
              : 'Critical resume sections or quantifiable achievements are missing. Follow AI recommendations to boost your score.'}
          </p>
        </div>
      </div>

      {/* Radar + Section Bars */}
      {sectionScores && Object.keys(sectionScores).length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-center">
          {showRadar && radarData.length > 0 && (
            <div className="h-64 flex flex-col items-center justify-center p-4 rounded-2xl bg-slate-900/40 border border-slate-800/80">
              <span className="text-xs font-semibold text-slate-400 mb-2">Section Competency Radar</span>
              <div className="w-full h-full">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                    <PolarGrid stroke="#334155" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 9 }} />
                    <Radar name="Score" dataKey="score" stroke="#818cf8" fill="#818cf8" fillOpacity={0.4} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          <div className="space-y-3.5 p-5 rounded-2xl bg-slate-900/40 border border-slate-800/80">
            <span className="text-xs font-semibold text-slate-300 block mb-3">Section Breakdown</span>
            {Object.entries(sectionScores).map(([key, val]) => (
              <div key={key} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">{sectionLabels[key] ?? key}</span>
                  <span className="font-semibold text-slate-200">{val}%</span>
                </div>
                <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${val >= 80 ? 'bg-emerald-500' : val >= 65 ? 'bg-indigo-500' : 'bg-amber-500'}`}
                    style={{ width: `${val}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
export default ScoreDisplay;
