import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';

interface Issue {
  id: number;
  github_issue_id: number;
  title: string;
  repo_full_name: string;
  description: string;
  state: string;
  html_url: string;
  created_at: string;
  is_ai_fixable: boolean;
  labels: string[];
}

interface Fix {
  id: number;
  content: string;
  status: string;
  created_at: string;
  is_submitted: boolean;
  submission_message: string | null;
  pr_url: string | null;
}

interface IssueDetailProps {
  userId: number;
}

export const IssueDetail: React.FC<IssueDetailProps> = ({ userId }) => {
  const { issueId } = useParams<{ issueId: string }>();
  const navigate = useNavigate();
  
  const [issue, setIssue] = useState<Issue | null>(null);
  const [fixes, setFixes] = useState<Fix[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchIssueData = async () => {
      if (!userId || !issueId) return;

      setLoading(true);
      try {
        // Fetch issue details
        const issueResponse = await axios.get(`/api/issues/issues/${issueId}`, {
          params: { user_id: userId }
        });
        setIssue(issueResponse.data);

        // Fetch fixes for this issue
        const fixesResponse = await axios.get(`/api/issues/issues/${issueId}/fixes`, {
          params: { user_id: userId }
        });
        setFixes(fixesResponse.data);
        
        setError(null);
      } catch (err) {
        console.error('Error fetching issue details:', err);
        setError('Failed to load issue details. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchIssueData();
  }, [userId, issueId]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const handleBackClick = () => {
    navigate(-1);
  };

  if (loading) {
    return (
      <div className="w-full max-w-4xl mx-auto p-4 text-center">
        <p className="text-gray-400">Loading issue details...</p>
      </div>
    );
  }

  if (error || !issue) {
    return (
      <div className="w-full max-w-4xl mx-auto p-4 text-center">
        <p className="text-red-400">{error || 'Issue not found'}</p>
        <button
          onClick={handleBackClick}
          className="mt-4 px-4 py-2 bg-[#21262d] text-white rounded-md hover:bg-[#30363d]"
        >
          Back to Issues
        </button>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-4xl mx-auto p-4"
    >
      {/* Navigation */}
      <div className="mb-6">
        <button
          onClick={handleBackClick}
          className="text-blue-400 hover:underline flex items-center"
        >
          <span className="mr-1">←</span> Back to Issues
        </button>
      </div>

      {/* Issue Header */}
      <div className="bg-[#161b22] p-6 rounded-md border border-[#30363d] mb-6">
        <div className="flex justify-between items-start mb-4">
          <h1 className="text-2xl font-bold text-white">{issue.title}</h1>
          <span className={`px-3 py-1 text-sm rounded-full ${
            issue.state === 'open' ? 'bg-green-900 text-green-300' : 'bg-purple-900 text-purple-300'
          }`}>
            {issue.state}
          </span>
        </div>
        
        <p className="text-sm text-gray-400 mb-4">
          <span className="font-medium">{issue.repo_full_name}</span> • 
          Created on {formatDate(issue.created_at)}
        </p>
        
        {issue.labels && issue.labels.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
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
        
        {/* Issue Description */}
        <div className="mt-6 p-4 bg-[#0d1117] rounded-md border border-[#30363d] whitespace-pre-wrap">
          {issue.description || 'No description provided.'}
        </div>
        
        {/* External Link */}
        <div className="mt-4">
          <a 
            href={issue.html_url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-400 hover:underline"
          >
            View on GitHub →
          </a>
        </div>
      </div>

      {/* Fixes Section */}
      <div className="mt-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-white">AI Generated Fixes</h2>
          {issue.is_ai_fixable && (
            <button 
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              onClick={() => {/* Logic for generating an AI fix */}}
            >
              Generate New Fix
            </button>
          )}
        </div>

        {fixes.length === 0 ? (
          <div className="text-center py-8 border border-dashed border-[#30363d] rounded-md">
            <p className="text-gray-400">No fixes generated yet.</p>
            {issue.is_ai_fixable && (
              <button 
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                onClick={() => {/* Logic for generating an AI fix */}}
              >
                Generate Fix
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-6">
            {fixes.map((fix, index) => (
              <motion.div
                key={fix.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="bg-[#161b22] p-4 rounded-md border border-[#30363d]"
              >
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-medium text-white">Fix #{index + 1}</h3>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    fix.status === 'approved' ? 'bg-green-900 text-green-300' : 
                    fix.status === 'rejected' ? 'bg-red-900 text-red-300' : 
                    'bg-yellow-900 text-yellow-300'
                  }`}>
                    {fix.status.charAt(0).toUpperCase() + fix.status.slice(1)}
                  </span>
                </div>
                
                <p className="text-sm text-gray-400 mb-3">
                  Generated on {formatDate(fix.created_at)}
                </p>
                
                <div className="p-3 bg-[#0d1117] rounded-md border border-[#30363d] mb-4 overflow-x-auto">
                  <pre className="text-sm text-gray-300 whitespace-pre-wrap">{fix.content}</pre>
                </div>
                
                {fix.is_submitted ? (
                  <div className="mt-3">
                    <p className="text-sm text-gray-400">
                      {fix.pr_url ? (
                        <>
                          Submitted as PR: <a 
                            href={fix.pr_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-blue-400 hover:underline"
                          >
                            View on GitHub
                          </a>
                        </>
                      ) : 'Submitted to GitHub'}
                    </p>
                    {fix.submission_message && (
                      <p className="mt-2 text-sm text-gray-400">
                        Message: {fix.submission_message}
                      </p>
                    )}
                  </div>
                ) : (
                  <div className="mt-3 flex gap-3">
                    <button 
                      className="px-3 py-1.5 bg-green-700 text-white text-sm rounded-md hover:bg-green-800"
                      onClick={() => {/* Submit fix logic */}}
                    >
                      Submit to GitHub
                    </button>
                    <button 
                      className="px-3 py-1.5 bg-red-700 text-white text-sm rounded-md hover:bg-red-800"
                      onClick={() => {/* Delete fix logic */}}
                    >
                      Delete
                    </button>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default IssueDetail;