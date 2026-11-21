import React from 'react';
import { ExtractedResumeData } from '../../types';
import {
  User,
  Mail,
  Phone,
  MapPin,
  Briefcase,
  GraduationCap,
  Award,
  Code,
  Calendar,
  ExternalLink,
} from 'lucide-react';

export interface ExtractedDataViewProps {
  data?: ExtractedResumeData | null;
  className?: string;
}

export const ExtractedDataView: React.FC<ExtractedDataViewProps> = ({
  data,
  className = '',
}) => {
  if (!data) {
    return (
      <div className="p-8 text-center text-slate-500 rounded-2xl border border-slate-800 bg-slate-900/40">
        No parsed data available for this resume.
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Contact & Bio Card */}
      <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <User className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">
              {data.full_name || 'Anonymous Candidate'}
            </h3>
            <p className="text-xs text-slate-400">Parsed Personal Information</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-slate-300">
          {data.email && (
            <div className="flex items-center gap-2">
              <Mail className="w-4 h-4 text-slate-500 shrink-0" />
              <span className="truncate">{data.email}</span>
            </div>
          )}
          {data.phone && (
            <div className="flex items-center gap-2">
              <Phone className="w-4 h-4 text-slate-500 shrink-0" />
              <span>{data.phone}</span>
            </div>
          )}
          {data.location && (
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-slate-500 shrink-0" />
              <span>{data.location}</span>
            </div>
          )}
        </div>

        {data.summary && (
          <div className="pt-2 border-t border-slate-800/80">
            <p className="text-xs text-slate-400 leading-relaxed italic">
              "{data.summary}"
            </p>
          </div>
        )}
      </div>

      {/* Skills Pill Cloud */}
      {data.skills && data.skills.length > 0 && (
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2">
            <Code className="w-4 h-4 text-indigo-400" />
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
              Identified Skills ({data.skills.length})
            </h4>
          </div>
          <div className="flex flex-wrap gap-2">
            {data.skills.map((skill, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-800 text-slate-200 border border-slate-700/60"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Experience Section */}
      {data.experience && data.experience.length > 0 && (
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-indigo-400" />
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
              Work Experience ({data.experience.length})
            </h4>
          </div>

          <div className="space-y-4 divide-y divide-slate-800/60">
            {data.experience.map((exp, idx) => (
              <div key={idx} className={idx > 0 ? 'pt-4 space-y-1.5' : 'space-y-1.5'}>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                  <h5 className="text-sm font-bold text-white">{exp.title}</h5>
                  <span className="text-xs text-slate-400 flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5 text-slate-500" />
                    {exp.start_date || 'Past'} —{' '}
                    {exp.current ? 'Present' : exp.end_date || 'Past'}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs font-medium text-indigo-400">
                  <span>{exp.company}</span>
                  {exp.location && (
                    <>
                      <span className="text-slate-600">•</span>
                      <span className="text-slate-400">{exp.location}</span>
                    </>
                  )}
                </div>
                {exp.description && (
                  <p className="text-xs text-slate-300 leading-relaxed mt-1">
                    {exp.description}
                  </p>
                )}
                {exp.highlights && exp.highlights.length > 0 && (
                  <ul className="mt-2 space-y-1 list-disc list-inside text-xs text-slate-400">
                    {exp.highlights.map((h, i) => (
                      <li key={i}>{h}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Education Section */}
      {data.education && data.education.length > 0 && (
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2">
            <GraduationCap className="w-4 h-4 text-indigo-400" />
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
              Education
            </h4>
          </div>

          <div className="space-y-3">
            {data.education.map((edu, idx) => (
              <div key={idx} className="flex justify-between items-start gap-4">
                <div>
                  <h5 className="text-sm font-semibold text-white">
                    {edu.degree} {edu.field_of_study ? `in ${edu.field_of_study}` : ''}
                  </h5>
                  <p className="text-xs text-indigo-400 mt-0.5">{edu.institution}</p>
                  {edu.gpa && (
                    <span className="text-[11px] text-slate-400 mt-1 inline-block">
                      GPA: {edu.gpa}
                    </span>
                  )}
                </div>
                {(edu.start_date || edu.end_date) && (
                  <span className="text-xs text-slate-500 shrink-0">
                    {edu.start_date} {edu.end_date ? `- ${edu.end_date}` : ''}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Projects */}
      {data.projects && data.projects.length > 0 && (
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2">
            <Award className="w-4 h-4 text-indigo-400" />
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
              Featured Projects
            </h4>
          </div>

          <div className="space-y-3">
            {data.projects.map((proj, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex items-center justify-between">
                  <h5 className="text-sm font-semibold text-white">{proj.name}</h5>
                  {proj.url && (
                    <a
                      href={proj.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
                    >
                      View <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">{proj.description}</p>
                {proj.technologies && proj.technologies.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-1">
                    {proj.technologies.map((tech, i) => (
                      <span
                        key={i}
                        className="text-[10px] px-2 py-0.5 rounded bg-slate-800/80 text-slate-300 border border-slate-700/50"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
export default ExtractedDataView;
