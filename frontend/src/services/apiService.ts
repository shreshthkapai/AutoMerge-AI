// src/services/apiService.ts
import axios from 'axios';

// Define interfaces for the data structures
export interface User {
  id: number;
  username: string;
  avatar_url?: string;
}

export interface Repository {
  id: number;
  name: string;
  full_name: string;
  description?: string;
  html_url: string;
}

export interface Issue {
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

// User related API calls
export const fetchUserInfo = async (userId: number): Promise<User> => {
  try {
    // This should match your actual backend endpoint for user info
    const response = await axios.get(`/api/auth/github/user/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching user info:', error);
    throw error;
  }
};

// Repository related API calls
export const fetchUserRepositories = async (userId: number): Promise<Repository[]> => {
  try {
    // This should match your actual backend endpoint for repositories
    const response = await axios.get(`/api/auth/github/repos/${userId}`);
    return response.data.repos || [];
  } catch (error) {
    console.error('Error fetching repositories:', error);
    throw error;
  }
};

export const fetchRepositoryDetails = async (userId: number, owner: string, repo: string): Promise<Repository> => {
  try {
    // This should match your actual backend endpoint for repository details
    const response = await axios.get(`/api/github/repos/${owner}/${repo}`, {
      params: { user_id: userId }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching repository details:', error);
    throw error;
  }
};

// Issue related API calls
export const fetchIssues = async (
  userId: number, 
  filters: { repo_name?: string; search?: string; label?: string; is_ai_fixable?: boolean }
): Promise<Issue[]> => {
  try {
    const params = { user_id: userId, ...filters };
    // This should match your actual backend endpoint for issues
    const response = await axios.get('/api/github/issues', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching issues:', error);
    throw error;
  }
};

export const fetchIssueDetails = async (userId: number, issueId: number): Promise<Issue> => {
  try {
    // This should match your actual backend endpoint for issue details
    const response = await axios.get(`/api/github/issues/${issueId}`, {
      params: { user_id: userId }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching issue details:', error);
    throw error;
  }
};