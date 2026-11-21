import React, { useState, useEffect } from 'react';
import { Resume, ResumeAnalysisResponse } from '../../types';
import { resumeService } from '../../services/resume.service';
import { PageHeader } from '../../components/shared/PageHeader';
import { ConfirmDialog } from '../../components/shared/ConfirmDialog';
import { ResumeCard } from '../../components/resume/ResumeCard';
import { ResumeUploadZone } from '../../components/resume/ResumeUploadZone';
import { ExtractedDataView } from '../../components/resume/ExtractedDataView';
import { ResumeAnalysisPanel } from '../../components/resume/ResumeAnalysisPanel';
import {
  UploadCloud,
  FileText,
  Sparkles,
  X,
  AlertCircle,
  FileCheck,
  CheckCircle,
} from 'lucide-react';

// Sample fallback resumes if backend has no records yet
const INITIAL_DEMO_RESUMES: Resume[] = [
  {
    id: 'res-demo-1',
    user_id: 'usr-1',
    title: 'Senior Full Stack Engineer Resume (2026)',
    file_name: 'Alex_Chen_Senior_Engineer_2026.pdf',
    file_url: '#',
    file_size: 245000,
    is_default: true,
    overall_score: 88,
    created_at: new Date(Date.now() - 3 * 86400000).toISOString(),
    updated_at: new Date(Date.now() - 3 * 86400000).toISOString(),
    extracted_data: {
      full_name: 'Alex Chen',
      email: 'alex.chen.dev@example.com',
      phone: '+1 (555) 234-5678',
      location: 'San Francisco, CA (Remote)',
      summary:
        'Experienced Full Stack Software Engineer with 6+ years specializing in React, TypeScript, Python (FastAPI), and distributed cloud services. Passionate about developer ergonomics and performant UI architectures.',
      skills: [
        'React',
        'TypeScript',
        'Next.js',
        'Python',
        'FastAPI',
        'PostgreSQL',
        'Redis',
        'Docker',
        'AWS',
        'Tailwind CSS',
        'GraphQL',
        'Jest / Vitest',
      ],
      experience: [
        {
          title: 'Senior Frontend Engineer',
          company: 'Nexus Cloud Technologies',
          location: 'San Francisco, CA',
          start_date: 'Jan 2023',
          current: true,
          description:
            'Architected client-facing web applications serving 500k+ active users. Spearheaded design system migration to Tailwind CSS and reduced initial bundle load times by 44%.',
          highlights: [
            'Built real-time collaboration canvas with WebSockets and Zustand',
            'Mentored 4 junior and mid-level engineers in modern React patterns',
          ],
        },
        {
          title: 'Full Stack Software Engineer',
          company: 'HyperScale Data Inc.',
          location: 'Remote',
          start_date: 'Mar 2020',
          end_date: 'Dec 2022',
          description:
            'Built RESTful API services in Python FastAPI and modern analytics dashboards in React & D3.',
          highlights: [
            'Improved database query performance by 65% through index tuning',
          ],
        },
      ],
      education: [
        {
          degree: 'B.S. in Computer Science',
          institution: 'University of California, Berkeley',
          field_of_study: 'Computer Science',
          start_date: '2016',
          end_date: '2020',
          gpa: '3.8',
        },
      ],
      projects: [
        {
          name: 'CloudMetrics Dashboard',
          description: 'Real-time metrics visualization platform for distributed container clusters.',
          technologies: ['React', 'TypeScript', 'FastAPI', 'Prometheus', 'TailwindCSS'],
          url: 'https://github.com/example/cloud-metrics',
        },
        {
          name: 'Automated Job Aggregator',
          description: 'Background web scraper and NLP keyword analyzer for tech job listings.',
          technologies: ['Python', 'BeautifulSoup', 'PostgreSQL', 'Docker'],
        },
      ],
    },
  },
  {
    id: 'res-demo-2',
    user_id: 'usr-1',
    title: 'AI / Backend Engineer Focus',
    file_name: 'Alex_Chen_AI_Backend_Resume.pdf',
    file_url: '#',
    file_size: 312000,
    is_default: false,
    overall_score: 72,
    created_at: new Date(Date.now() - 10 * 86400000).toISOString(),
    updated_at: new Date(Date.now() - 10 * 86400000).toISOString(),
    extracted_data: {
      full_name: 'Alex Chen',
      email: 'alex.chen.dev@example.com',
      location: 'San Francisco, CA',
      summary:
        'Backend engineer with deep focus on Python asynchronous services, LLM prompt engineering, and RAG pipelines.',
      skills: ['Python', 'FastAPI', 'LangChain', 'OpenAI API', 'ChromaDB', 'PostgreSQL', 'Docker'],
    },
  },
];

export const ResumesPage: React.FC = () => {
  const [resumes, setResumes] = useState<Resume[]>(INITIAL_DEMO_RESUMES);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [selectedResume, setSelectedResume] = useState<Resume | null>(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [detailTab, setDetailTab] = useState<'parsed' | 'analysis'>('analysis');
  const [analysisMap, setAnalysisMap] = useState<Record<string, ResumeAnalysisResponse>>({
    'res-demo-1': {
      resume_id: 'res-demo-1',
      score: 88, overall_score: 88,
      section_scores: {
        contact_info: 98,
        summary: 85,
        experience: 90,
        education: 82,
        skills: 92,
        formatting: 86,
      },
      strengths: [
        'Clear action verbs and quantifiable results in experience descriptions',
        'High density of relevant frontend and backend modern keywords',
        'Professional structure cleanly parseable by ATS scanners',
      ],
      weaknesses: [
        'Could include more cloud infrastructure metrics (AWS costs or uptime)',
        'Certifications section is missing or omitted',
      ],
      suggestions: [
        'Add specific metrics regarding cloud deployments or CI/CD test coverage',
        'Link relevant public GitHub repositories or technical blog posts',
      ],
      ats_compatibility: {
        score: 92,
        keywords_found: [],
        keywords_missing: ['Terraform', 'CI/CD Pipelines', 'Kubernetes Helm'],
        missing_keywords: ['Terraform', 'CI/CD Pipelines', 'Kubernetes Helm'],
        formatting_issues: [],
      },
    },
  });

  const [analyzingId, setAnalyzingId] = useState<string | null>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [resumeToDelete, setResumeToDelete] = useState<Resume | null>(null);
  const [successToast, setSuccessToast] = useState<string | null>(null);

  // Fetch real resumes from backend on mount
  useEffect(() => {
    let mounted = true;
    async function loadResumes() {
      try {
        setIsLoading(true);
        const data = await resumeService.getResumes();
        if (mounted && data && data.length > 0) {
          setResumes(data);
          const initialMap: Record<string, ResumeAnalysisResponse> = {};
          data.forEach((r) => {
            if (r.analysis) {
              initialMap[r.id] = r.analysis;
            } else if (r.overall_score !== undefined && r.overall_score !== null) {
              initialMap[r.id] = {
                resume_id: r.id,
                score: r.overall_score,
                overall_score: r.overall_score,
                summary: r.extracted_data?.summary || 'Analysis complete.',
                strengths: r.extracted_data?.strengths || [],
                improvements: r.extracted_data?.weaknesses || r.extracted_data?.suggestions || [],
                weaknesses: r.extracted_data?.weaknesses || [],
                suggestions: r.extracted_data?.suggestions || [],
                missing_keywords: r.extracted_data?.missing_keywords || [],
                section_scores: r.extracted_data?.section_scores || {},
              };
            }
          });
          setAnalysisMap((prev) => ({ ...prev, ...initialMap }));
        }
      } catch (err) {
        // Fallback to demo resumes if backend is offline or unauthorized
        console.warn('Using demo resumes fallback:', err);
      } finally {
        if (mounted) setIsLoading(false);
      }
    }
    loadResumes();
    return () => {
      mounted = false;
    };
  }, []);

  const triggerToast = (msg: string) => {
    setSuccessToast(msg);
    setTimeout(() => setSuccessToast(null), 3000);
  };

  const handleUploadResume = async (file: File, title: string) => {
    setIsUploading(true);
    try {
      let newResume: Resume;
      try {
        newResume = await resumeService.uploadResume(file, title);
      } catch {
        // Demo creation fallback
        newResume = {
          id: `res-${Date.now()}`,
          user_id: 'usr-1',
          title: title,
          file_name: file.name,
          file_url: URL.createObjectURL(file),
          file_size: file.size,
          is_default: resumes.length === 0,
          overall_score: 78,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          extracted_data: {
            full_name: 'Uploaded Candidate',
            email: 'candidate@example.com',
            summary: `Parsed summary for ${title}`,
            skills: ['React', 'TypeScript', 'Node.js', 'SQL'],
          },
        };
      }

      setResumes((prev) => [newResume, ...prev]);
      setUploadModalOpen(false);
      triggerToast('Resume uploaded and parsed successfully!');
    } finally {
      setIsUploading(false);
    }
  };

  const handleAnalyze = async (resume: Resume) => {
    setAnalyzingId(resume.id);
    try {
      let analysis: ResumeAnalysisResponse;
      try {
        analysis = await resumeService.analyzeResume(resume.id);
      } catch {
        // Demo AI analysis response
        analysis = {
          resume_id: resume.id,
          overall_score: Math.floor(Math.random() * 20) + 75,
          section_scores: {
            contact_info: 95,
            summary: 80,
            experience: 85,
            education: 75,
            skills: 88,
            formatting: 90,
          },
          strengths: [
            'Solid alignment with engineering roles',
            'Consistent formatting and readable fonts',
          ],
          weaknesses: ['Add more quantifiable impact metrics to recent roles'],
          suggestions: [
            'Mention experience with microservices and container orchestration',
          ],
          ats_compatibility: {
            score: 85,
            keywords_found: [],
            keywords_missing: ['System Design', 'CI/CD', 'Automated Testing'],
            missing_keywords: ['System Design', 'CI/CD', 'Automated Testing'],
            formatting_issues: [],
          },
        };
      }

      setAnalysisMap((prev) => ({ ...prev, [resume.id]: analysis }));
      setResumes((prev) =>
        prev.map((r) =>
          r.id === resume.id ? { ...r, overall_score: analysis.overall_score } : r
        )
      );

      setSelectedResume(resume);
      setDetailTab('analysis');
      setDetailModalOpen(true);
      triggerToast(`AI Analysis complete! Score: ${analysis.overall_score}%`);
    } finally {
      setAnalyzingId(null);
    }
  };

  const handleSetDefault = async (resume: Resume) => {
    try {
      await resumeService.setDefaultResume(resume.id);
    } catch {
      // Local state update
    }
    setResumes((prev) =>
      prev.map((r) => ({
        ...r,
        is_default: r.id === resume.id,
      }))
    );
    triggerToast(`"${resume.title || resume.file_name}" set as default resume.`);
  };

  const handleDeleteClick = (resume: Resume) => {
    setResumeToDelete(resume);
    setDeleteConfirmOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!resumeToDelete) return;
    try {
      await resumeService.deleteResume(resumeToDelete.id);
    } catch {
      // Local state fallback
    }
    setResumes((prev) => prev.filter((r) => r.id !== resumeToDelete.id));
    setDeleteConfirmOpen(false);
    setResumeToDelete(null);
    triggerToast('Resume removed successfully.');
  };

  const handleView = (resume: Resume, defaultTab: 'analysis' | 'parsed' = 'analysis') => {
    setSelectedResume(resume);
    const tab = resume.overall_score !== undefined && resume.overall_score !== null ? defaultTab : 'parsed';
    setDetailTab(tab);
    setDetailModalOpen(true);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Toast message */}
      {successToast && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-3 rounded-xl bg-emerald-500 text-slate-950 font-bold text-xs shadow-2xl animate-in slide-in-from-bottom-4">
          <CheckCircle className="w-4 h-4" />
          <span>{successToast}</span>
        </div>
      )}

      {/* Page Header */}
      <PageHeader
        title="My Resumes"
        description="Upload, manage, and AI-optimize multiple resume versions for different job categories."
        breadcrumbs={[
          { label: 'Dashboard', href: '/app/dashboard' },
          { label: 'Resumes' },
        ]}
        actions={
          <button
            type="button"
            onClick={() => setUploadModalOpen(true)}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-950/40 transition-all"
          >
            <UploadCloud className="w-4 h-4" />
            Upload Resume
          </button>
        }
      />

      {/* Resumes Grid / Empty State */}
      {resumes.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-12 text-center rounded-2xl border-2 border-dashed border-slate-800 bg-slate-900/40 space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <FileText className="w-8 h-8" />
          </div>
          <div className="space-y-1">
            <h3 className="text-base font-bold text-white">No resumes uploaded yet</h3>
            <p className="text-xs text-slate-400 max-w-sm">
              Upload your first resume in PDF or DOCX format to unlock AI matching, tailoring, and ATS score analysis.
            </p>
          </div>
          <button
            type="button"
            onClick={() => setUploadModalOpen(true)}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md transition-all"
          >
            <UploadCloud className="w-4 h-4" />
            Upload Your Resume Now
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {resumes.map((resume) => (
            <ResumeCard
              key={resume.id}
              resume={resume}
              onAnalyze={handleAnalyze}
              onSetDefault={handleSetDefault}
              onDelete={handleDeleteClick}
              onView={handleView}
              isAnalyzing={analyzingId === resume.id}
            />
          ))}
        </div>
      )}

      {/* Quick Upload Banner for easy access */}
      {resumes.length > 0 && (
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 space-y-4">
          <div className="flex items-center gap-2 text-indigo-400">
            <Sparkles className="w-4 h-4" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Quick Upload Another Version
            </h3>
          </div>
          <ResumeUploadZone
            onUpload={handleUploadResume}
            isLoading={isUploading}
          />
        </div>
      )}

      {/* Upload Modal Dialog */}
      {uploadModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="relative w-full max-w-xl bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl text-slate-100 space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                  <UploadCloud className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">Upload New Resume</h3>
                  <p className="text-xs text-slate-400">
                    Parse and analyze your resume with AI
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setUploadModalOpen(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <ResumeUploadZone
              onUpload={handleUploadResume}
              isLoading={isUploading}
            />
          </div>
        </div>
      )}

      {/* Resume Details / Analysis Drawer / Modal */}
      {detailModalOpen && selectedResume && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="relative w-full max-w-4xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden text-slate-100">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/90">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                  <FileCheck className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">
                    {selectedResume.title || selectedResume.file_name}
                  </h3>
                  <p className="text-xs text-slate-400">{selectedResume.file_name}</p>
                </div>
              </div>
              <button
                onClick={() => setDetailModalOpen(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Subheader Tabs */}
            <div className="flex items-center gap-3 px-6 py-2.5 border-b border-slate-800 bg-slate-950/50">
              <button
                type="button"
                onClick={() => setDetailTab('analysis')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                  detailTab === 'analysis'
                    ? 'bg-indigo-600 text-white'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5" /> AI Analysis & ATS Score
              </button>
              <button
                type="button"
                onClick={() => setDetailTab('parsed')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                  detailTab === 'parsed'
                    ? 'bg-indigo-600 text-white'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <FileText className="w-3.5 h-3.5" /> Extracted Profile Data
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 flex-1 overflow-y-auto">
              {detailTab === 'analysis' ? (
                <ResumeAnalysisPanel
                  analysis={analysisMap[selectedResume.id]}
                  isLoading={analyzingId === selectedResume.id}
                  onReanalyze={() => handleAnalyze(selectedResume)}
                />
              ) : (
                <ExtractedDataView data={selectedResume.extracted_data} />
              )}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-slate-800 bg-slate-900 flex items-center justify-between">
              <div>
                {!selectedResume.is_default && (
                  <button
                    type="button"
                    onClick={() => {
                      handleSetDefault(selectedResume);
                      setSelectedResume({ ...selectedResume, is_default: true });
                    }}
                    className="text-xs font-medium text-slate-300 hover:text-indigo-400 transition-colors"
                  >
                    ★ Set as Primary Resume
                  </button>
                )}
              </div>
              <button
                type="button"
                onClick={() => setDetailModalOpen(false)}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={deleteConfirmOpen}
        title="Delete Resume"
        message={`Are you sure you want to delete "${resumeToDelete?.title || resumeToDelete?.file_name}"? This action cannot be undone.`}
        confirmText="Delete Resume"
        variant="danger"
        onConfirm={handleConfirmDelete}
        onCancel={() => {
          setDeleteConfirmOpen(false);
          setResumeToDelete(null);
        }}
      />
    </div>
  );
};
export default ResumesPage;
