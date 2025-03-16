import axios from 'axios';

export interface Fix {
  id: number;
  content: string;
  status: string;
  created_at: string;
  is_submitted: boolean;
  submission_message: string | null;
  pr_url: string | null;
}

export const generateFix = async (userId: number, issueId: number): Promise<Fix> => {
  const response = await axios.post(`/api/issues/issues/${issueId}/generate-fix`, null, {
    params: { user_id: userId }
  });
  return response.data;
};

export const submitFix = async (userId: number, fixId: number, submissionMessage: string): Promise<Fix> => {
  const response = await axios.post(`/api/issues/fixes/${fixId}/submit`, 
    { submission_message: submissionMessage },
    { params: { user_id: userId } }
  );
  return response.data;
};

export const deleteFix = async (userId: number, fixId: number): Promise<void> => {
  await axios.delete(`/api/issues/fixes/${fixId}`, {
    params: { user_id: userId }
  });
};
