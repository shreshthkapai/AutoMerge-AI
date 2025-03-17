import { useState, useEffect } from 'react';
import axios from 'axios';

export function useAuth() {
  const [userId, setUserId] = useState<number>(0);
  const [username, setUsername] = useState<string>('Guest');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const initAuth = async () => {
      setLoading(true);
      
      // Get user ID from URL or localStorage
      const params = new URLSearchParams(window.location.search);
      const idFromUrl = parseInt(params.get('user_id') || '0', 10);
      const storedId = parseInt(localStorage.getItem('user_id') || '0', 10);
      const id = idFromUrl || storedId;
      
      if (idFromUrl) {
        localStorage.setItem('user_id', idFromUrl.toString());
      }
      
      setUserId(id);
      
      // If we have a user ID, fetch the username
      if (id > 0) {
        try {
          const response = await axios.get(`/api/auth/user/${id}`);
          setUsername(response.data.username || 'Guest');
        } catch (error) {
          console.error('Error fetching user data:', error);
          setUsername('Guest');
        }
      }
      
      setLoading(false);
    };
    
    initAuth();
  }, []);
  
  const login = () => {
    window.location.href = 'http://localhost:8000/api/auth/github/login';
  };
  
  const logout = () => {
    localStorage.removeItem('user_id');
    setUserId(0);
    setUsername('Guest');
  };
  
  return {
    userId,
    username,
    loading,
    isAuthenticated: userId > 0,
    login,
    logout
  };
}