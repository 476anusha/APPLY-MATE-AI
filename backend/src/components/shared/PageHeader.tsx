import React from 'react';
import { ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export interface PageHeaderProps {
  title: string;
  description?: string;
  breadcrumbs?: BreadcrumbItem[];
  badge?: React.ReactNode;
  actions?: React.ReactNode;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  description,
  breadcrumbs,
  badge,
  actions,
}) => {
  return (
    <div className="flex flex-col gap-4 pb-6 border-b border-slate-800 md:flex-row md:items-center md:justify-between">
      <div className="space-y-1">
        {breadcrumbs && breadcrumbs.length > 0 && (
          <nav className="flex items-center gap-1.5 text-xs text-slate-400 mb-2">
            {breadcrumbs.map((item, index) => {
              const isLast = index === breadcrumbs.length - 1;
              return (
                <React.Fragment key={index}>
                  {item.href && !isLast ? (
                    <Link
                      to={item.href}
                      className="hover:text-indigo-400 transition-colors"
                    >
                      {item.label}
                    </Link>
                  ) : (
                    <span className={isLast ? 'text-slate-300 font-medium' : ''}>
                      {item.label}
                    </span>
                  )}
                  {!isLast && <ChevronRight className="w-3.5 h-3.5 text-slate-600" />}
                </React.Fragment>
              );
            })}
          </nav>
        )}

        <div className="flex items-center gap-3 flex-wrap">
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
            {title}
          </h1>
          {badge}
        </div>

        {description && (
          <p className="text-sm text-slate-400 max-w-2xl">{description}</p>
        )}
      </div>

      {actions && (
        <div className="flex items-center gap-3 shrink-0 flex-wrap">
          {actions}
        </div>
      )}
    </div>
  );
};
export default PageHeader;
