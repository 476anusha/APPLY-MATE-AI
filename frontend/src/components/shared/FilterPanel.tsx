import React from 'react';
import { Filter, X, RotateCcw } from 'lucide-react';

export interface FilterPanelProps {
  title?: string;
  activeCount?: number;
  onReset?: () => void;
  isOpen?: boolean;
  onClose?: () => void;
  children: React.ReactNode;
  className?: string;
}

export const FilterPanel: React.FC<FilterPanelProps> = ({
  title = 'Filters',
  activeCount = 0,
  onReset,
  isOpen = true,
  onClose,
  children,
  className = '',
}) => {
  return (
    <div
      className={`rounded-2xl border border-slate-800 bg-slate-900/70 backdrop-blur-sm p-5 space-y-5 ${className}`}
    >
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-indigo-400" />
          <h3 className="text-sm font-semibold text-white">{title}</h3>
          {activeCount > 0 && (
            <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
              {activeCount}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {activeCount > 0 && onReset && (
            <button
              type="button"
              onClick={onReset}
              className="text-xs text-slate-400 hover:text-slate-200 transition-colors flex items-center gap-1"
            >
              <RotateCcw className="w-3 h-3" />
              Reset
            </button>
          )}

          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="md:hidden p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      <div className="space-y-5">{children}</div>
    </div>
  );
};
export default FilterPanel;
