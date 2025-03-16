import React from 'react';

interface AIFixableBadgeProps {
  isAIFixable: boolean;
}

const AIFixableBadge: React.FC<AIFixableBadgeProps> = ({ isAIFixable }) => {
  if (!isAIFixable) return null;
  
  return (
    <span className="px-2 py-1 text-xs bg-blue-900 text-blue-300 rounded-full flex items-center gap-1">
      <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" strokeWidth="2"/>
        <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
      </svg>
      AI-Fixable
    </span>
  );
};

export default AIFixableBadge;