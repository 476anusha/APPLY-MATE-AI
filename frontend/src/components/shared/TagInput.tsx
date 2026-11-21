import React, { useState, KeyboardEvent } from 'react';
import { X, Plus } from 'lucide-react';

export interface TagInputProps {
  value: string[];
  onChange: (tags: string[]) => void;
  placeholder?: string;
  maxTags?: number;
  suggestions?: string[];
  label?: string;
  className?: string;
}

export const TagInput: React.FC<TagInputProps> = ({
  value = [],
  onChange,
  placeholder = 'Add a skill and press Enter...',
  maxTags = 30,
  suggestions = [],
  label,
  className = '',
}) => {
  const [inputValue, setInputValue] = useState('');

  const addTag = (tagToAdd: string) => {
    const trimmed = tagToAdd.trim();
    if (!trimmed) return;
    if (value.includes(trimmed)) {
      setInputValue('');
      return;
    }
    if (value.length >= maxTags) return;

    onChange([...value, trimmed]);
    setInputValue('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addTag(inputValue);
    } else if (e.key === 'Backspace' && !inputValue && value.length > 0) {
      removeTag(value.length - 1);
    }
  };

  const removeTag = (indexToRemove: number) => {
    onChange(value.filter((_, idx) => idx !== indexToRemove));
  };

  // Filter suggestions to show ones not already added
  const availableSuggestions = suggestions
    .filter((s) => !value.includes(s) && s.toLowerCase().includes(inputValue.toLowerCase()))
    .slice(0, 5);

  return (
    <div className={`space-y-2 ${className}`}>
      {label && (
        <label className="block text-xs font-medium text-slate-300">{label}</label>
      )}

      <div className="flex flex-wrap items-center gap-2 p-2.5 rounded-xl bg-slate-900 border border-slate-800 focus-within:border-indigo-500 transition-colors min-h-[46px]">
        {value.map((tag, idx) => (
          <span
            key={idx}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-indigo-500/15 text-indigo-300 border border-indigo-500/30"
          >
            {tag}
            <button
              type="button"
              onClick={() => removeTag(idx)}
              className="text-indigo-300 hover:text-white transition-colors"
              aria-label={`Remove ${tag}`}
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </span>
        ))}

        {value.length < maxTags && (
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            onBlur={() => {
              if (inputValue.trim()) addTag(inputValue);
            }}
            placeholder={value.length === 0 ? placeholder : ''}
            className="flex-1 min-w-[140px] bg-transparent text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none"
          />
        )}
      </div>

      {availableSuggestions.length > 0 && inputValue.length > 0 && (
        <div className="flex flex-wrap gap-1.5 pt-1">
          <span className="text-[11px] text-slate-500 self-center">Suggestions:</span>
          {availableSuggestions.map((suggestion) => (
            <button
              key={suggestion}
              type="button"
              onClick={() => addTag(suggestion)}
              className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
            >
              <Plus className="w-3 h-3" />
              {suggestion}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
export default TagInput;
