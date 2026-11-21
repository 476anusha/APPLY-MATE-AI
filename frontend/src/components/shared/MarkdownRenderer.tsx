import React from 'react';

export interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({
  content,
  className = '',
}) => {
  if (!content) return null;

  // Simple, safe Markdown parser that doesn't require heavy dependencies
  const renderMarkdown = (text: string) => {
    const lines = text.split('\n');
    const elements: React.ReactNode[] = [];
    let inCodeBlock = false;
    let codeBuffer: string[] = [];
    let listBuffer: string[] = [];
    let listType: 'ul' | 'ol' = 'ul';

    const flushList = () => {
      if (listBuffer.length > 0) {
        if (listType === 'ul') {
          elements.push(
            <ul key={`ul-${elements.length}`} className="my-3 space-y-1.5 list-disc list-inside text-slate-300">
              {listBuffer.map((item, i) => (
                <li key={i} className="leading-relaxed">
                  {parseInlineFormatting(item)}
                </li>
              ))}
            </ul>
          );
        } else {
          elements.push(
            <ol key={`ol-${elements.length}`} className="my-3 space-y-1.5 list-decimal list-inside text-slate-300">
              {listBuffer.map((item, i) => (
                <li key={i} className="leading-relaxed">
                  {parseInlineFormatting(item)}
                </li>
              ))}
            </ol>
          );
        }
        listBuffer = [];
      }
    };

    const flushCodeBlock = () => {
      if (inCodeBlock) {
        elements.push(
          <div key={`code-${elements.length}`} className="my-3 overflow-x-auto rounded-xl bg-slate-950 p-4 border border-slate-800 text-xs font-mono text-emerald-400">
            <pre>{codeBuffer.join('\n')}</pre>
          </div>
        );
        codeBuffer = [];
        inCodeBlock = false;
      }
    };

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      // Code blocks
      if (line.trim().startsWith('```')) {
        if (inCodeBlock) {
          flushCodeBlock();
        } else {
          flushList();
          inCodeBlock = true;
        }
        continue;
      }

      if (inCodeBlock) {
        codeBuffer.push(line);
        continue;
      }

      // Headers
      if (line.startsWith('### ')) {
        flushList();
        elements.push(
          <h3 key={i} className="text-base font-semibold text-white mt-4 mb-2">
            {parseInlineFormatting(line.replace('### ', ''))}
          </h3>
        );
        continue;
      }
      if (line.startsWith('## ')) {
        flushList();
        elements.push(
          <h2 key={i} className="text-lg font-bold text-white mt-5 mb-2.5">
            {parseInlineFormatting(line.replace('## ', ''))}
          </h2>
        );
        continue;
      }
      if (line.startsWith('# ')) {
        flushList();
        elements.push(
          <h1 key={i} className="text-xl font-extrabold text-white mt-6 mb-3">
            {parseInlineFormatting(line.replace('# ', ''))}
          </h1>
        );
        continue;
      }

      // Blockquotes
      if (line.startsWith('> ')) {
        flushList();
        elements.push(
          <blockquote key={i} className="border-l-4 border-indigo-500 pl-4 py-1 my-2 text-slate-400 italic">
            {parseInlineFormatting(line.replace('> ', ''))}
          </blockquote>
        );
        continue;
      }

      // Unordered lists
      if (line.trim().match(/^[-*•]\s+/)) {
        if (listBuffer.length > 0 && listType !== 'ul') flushList();
        listType = 'ul';
        listBuffer.push(line.trim().replace(/^[-*•]\s+/, ''));
        continue;
      }

      // Ordered lists
      if (line.trim().match(/^\d+\.\s+/)) {
        if (listBuffer.length > 0 && listType !== 'ol') flushList();
        listType = 'ol';
        listBuffer.push(line.trim().replace(/^\d+\.\s+/, ''));
        continue;
      }

      // Normal text
      flushList();
      if (line.trim() === '') {
        elements.push(<div key={i} className="h-2" />);
      } else {
        elements.push(
          <p key={i} className="text-sm leading-relaxed text-slate-300 my-1.5">
            {parseInlineFormatting(line)}
          </p>
        );
      }
    }

    flushList();
    flushCodeBlock();

    return elements;
  };

  const parseInlineFormatting = (text: string): React.ReactNode => {
    // Splits text into bold, inline code, and normal text
    const parts: React.ReactNode[] = [];
    let remaining = text;
    let keyIdx = 0;

    while (remaining.length > 0) {
      // Bold **bold**
      const boldMatch = remaining.match(/\*\*(.*?)\*\*/);
      // Inline code `code`
      const codeMatch = remaining.match(/`(.*?)`/);

      const boldIndex = boldMatch ? remaining.indexOf(boldMatch[0]) : -1;
      const codeIndex = codeMatch ? remaining.indexOf(codeMatch[0]) : -1;

      // Find first occurrence
      if (boldIndex !== -1 && (codeIndex === -1 || boldIndex < codeIndex)) {
        if (boldIndex > 0) {
          parts.push(remaining.substring(0, boldIndex));
        }
        parts.push(
          <strong key={keyIdx++} className="font-semibold text-white">
            {boldMatch![1]}
          </strong>
        );
        remaining = remaining.substring(boldIndex + boldMatch![0].length);
      } else if (codeIndex !== -1) {
        if (codeIndex > 0) {
          parts.push(remaining.substring(0, codeIndex));
        }
        parts.push(
          <code
            key={keyIdx++}
            className="px-1.5 py-0.5 rounded bg-slate-800 text-indigo-300 font-mono text-xs"
          >
            {codeMatch![1]}
          </code>
        );
        remaining = remaining.substring(codeIndex + codeMatch![0].length);
      } else {
        parts.push(remaining);
        break;
      }
    }

    return parts;
  };

  return <div className={`markdown-content ${className}`}>{renderMarkdown(content)}</div>;
};
export default MarkdownRenderer;
