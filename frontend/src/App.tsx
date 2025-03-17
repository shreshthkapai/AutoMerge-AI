// frontend/src/App.tsx
import { useEffect, useState } from 'react'
import { Welcome } from './components/Welcome'
import { RepoList } from './components/RepoList'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import IssueList from './pages/IssueList'
import IssueDetail from './pages/IssueDetail'
import { fetchUserInfo, fetchUserRepositories } from './services/apiService'
import Header from './components/Header'

const App: React.FC = () => {
  const [message, setMessage] = useState<string>('Welcome to AutoMerge AI')
  const [username, setUsername] = useState<string>('Guest')
  const [repos, setRepos] = useState<{ name: string; full_name: string }[]>([])
  const [userId, setUserId] = useState<number>(0)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  const getUserId = () => {
    const params = new URLSearchParams(window.location.search)
    const idFromUrl = parseInt(params.get('user_id') || '0', 10)
    const storedId = parseInt(localStorage.getItem('user_id') || '0', 10)
    const id = idFromUrl || storedId
    if (idFromUrl) localStorage.setItem('user_id', idFromUrl.toString())
    return id
  }

  useEffect(() => {
    const id = getUserId()
    setUserId(id)

    const fetchData = async () => {
      if (id === 0) {
        setUsername('Guest')
        setRepos([])
        setLoading(false)
        return
      }

      setLoading(true)
      try {
        // Fetch user info
        const userInfo = await fetchUserInfo(id)
        setUsername(userInfo.username || 'Guest')
        
        // Fetch repositories
        const repositories = await fetchUserRepositories(id)
        setRepos(repositories)
        
        setError(null)
      } catch (err) {
        console.error('Error fetching data:', err)
        setError('Failed to load user data. Please try logging in again.')
        setUsername('Guest')
        setRepos([])
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('user_id')
    setUserId(0)
    setUsername('Guest')
    setRepos([])
  }

  const handleLogin = () => {
    window.location.href = '/api/auth/github/login'
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-400">Loading...</p>
      </div>
    )
  }

  return (
    <Router>
      <div className="min-h-screen flex flex-col">
        {userId !== 0 && <Header username={username} onLogout={handleLogout} />}
        
        <div className="flex-grow flex flex-col items-center py-8 px-4">
          {userId === 0 ? (
            <>
              <Welcome message={message} username={username} />
              <button
                onClick={handleLogin}
                className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Login with GitHub
              </button>
            </>
          ) : (
            <Routes>
              <Route path="/" element={<RepoList repos={repos} />} />
              <Route path="/issues" element={<IssueList userId={userId} />} />
              <Route path="/issues/:issueId" element={<IssueDetail userId={userId} />} />
              <Route path="/repos/:owner/:repoName/issues" element={<IssueList userId={userId} />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          )}
          
          {error && (
            <div className="mt-4 p-4 bg-red-900 text-red-100 rounded-md">
              {error}
            </div>
          )}
        </div>
      </div>
    </Router>
  )
}

export default App