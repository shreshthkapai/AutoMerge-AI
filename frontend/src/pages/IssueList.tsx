// frontend/src/pages/IssueList.tsx
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link, useParams } from 'react-router-dom';
import { fetchIssues, Issue } from '../services/apiService';
import AIFixableBadge from '../components/AIFixableBadge';

interface IssueListProps {
  userId: number;
}

export const IssueList: React.FC<IssueListProps> = ({ userId }) => {
  const { owner, repoName } = useParams<{ owner: string; repoName: string }>();
  const [issues, setIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [labelFilter, setLabelFilter] = useState<string>('');
  const [aiFixableOnly, setAiFixableOnly] = useState<boolean>(false);

  useEffect(() => {
    const fetchIssueData = async () => {
      if (!userId) return;

      setLoading(true);
      try {
        const filters: {
          repo_name?: string;
          search?: string;
          label?: string;
          is_ai_fixable?: boolean;
        } = {};
        
        if (owner && repoName) filters.repo_name = `${owner}/${repoName}`;
        if (searchTerm) filters.search = searchTerm;
        if (labelFilter) filters.label = labelFilter;
        if (aiFixableOnly) filters.is_ai_fixable = true;

        const issueData = await fetchIssues(userId, filters);
        setIssues(issueData);
        setError(null);
      } catch (err) {
        console.error('Error fetching issues:', err);
        setError('Failed to load issues. Please try again.');
        setIssues([]);
      } finally {
        setLoading(false);
      }
    };

    fetchIssueData();
  }, [userId, owner, repoName, searchTerm, labelFilter, aiFixableOnly]);

  // Format date function
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-4xl mx-auto p-4"
    >
      <h1 className="text-2xl font-bold text-white mb-6">
        {repoName ? `Issues for ${owner}/${repoName}` : 'All Issues'}
      </h1>

      {/* Search and Filters */}
      <div className="mb-6 space-y-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search issues..."
            className="px-4 py-2 bg-[#0d1117] border border-[#30363d] rounded-md text-white flex-1"
          />
          <select
            value={labelFilter}
            onChange={(e) => setLabelFilter(e.target.value)}
            className="px-4 py-2 bg-[#0d1117] border border-[#30363d] rounded-md text-white"
          >
            <option value="">All Labels</option>
            <option value="bug">bug</option>
            <option value="enhancement">enhancement</option>
            <option value="documentation">documentation</option>
          </select>
        </div>
        
        <div className="flex items-center">
          <input
            type="checkbox"
            id="aiFixable"
            checked={aiFixableOnly}
            onChange={(e) => setAiFixableOnly(e.target.checked)}
            className="mr-2"
          />
          <label htmlFor="aiFixable" className="text-gray-300">
            AI-fixable issues only
          </label>
        </div>
      </div>

      {/* Issues List */}
      {loading ? (
        <div className="text-center py-8">
          <p className="text-gray-400">Loading issues...</p>
        </div>
      ) : error ? (
        <div className="text-center py-8">
          <p className="text-red-400">{error}</p>
        </div>
      ) : issues.length === 0 ? (
        <div className="text-center py-8 border border-dashed border-[#30363d] rounded-md">
          <p className="text-gray-400">No issues found matching your criteria.</p>
        </div>
      ) : (
        <ul className="space-y-4">
          {issues.map((issue, index) => (
            <motion.li
              key={issue.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className="bg-[#161b22] p-4 rounded-md border border-[#30363d] hover:bg-[#21262d] transition-colors"
            >
              <Link to={`/issues/${issue.id}`} className="block">
                <div className="flex justify-between items-start">
                  <h3 className="text-lg font-semibold text-blue-400 mb-2">{issue.title}</h3>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    issue.state === 'open' ? 'bg-green-900 text-green-300' : 'bg-purple-900 text-purple-300'
                  }`}>
                    {issue.state}
                  </span>
                </div>
                
                <p className="text-sm text-gray-400 mb-2">
                  {issue.repo_full_name} • Created on {formatDate(issue.created_at)}
                </p>
                
                {issue.labels && issue.labels.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-3">
                    {issue.labels.map(label => (
                      <span 
                        key={label} 
                        className="px-2 py-1 text-xs bg-[#0d1117] border border-[#30363d] rounded-full text-gray-300"
                      >
                        {label}
                      </span>
                    ))}
                  </div>
                )}
                
                <AIFixableBadge isAIFixable={issue.is_ai_fixable} />
              </Link>
            </motion.li>
          ))}
        </ul>
      )}
    </motion.div>
  );
};

export default IssueList;