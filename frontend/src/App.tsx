import { useEffect, useState } from 'react'
import { Welcome } from './components/Welcome'
import { RepoList } from './components/RepoList'
import axios from 'axios'

const App: React.FC = () => {
  const [message, setMessage] = useState<string>('')
  const [username, setUsername] = useState<string>('Guest')
  const [repos, setRepos] = useState<{ name: string; full_name: string }[]>([])
  const [userId, setUserId] = useState<number>(0)

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

    const fetchMessage = async () => {
      try {
        const response = await axios.get('/api/')
        setMessage(response.data.message)
      } catch (error) {
        console.error('Error fetching message:', error)
        setMessage('Welcome to AutoMerge AI!')
      }
    }

    const fetchRepos = async () => {
      if (id === 0) {
        setUsername('Guest')
        setRepos([])
        return
      }
      try {
        const response = await axios.get(`/api/auth/repos/${id}`)
        setUsername(response.data.username || 'Guest')
        setRepos(response.data.repos || [])
      } catch (error) {
        console.error('Error fetching repos:', error)
        setUsername('Guest')
        setRepos([])
      }
    }

    fetchMessage()
    fetchRepos()
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('user_id')
    setUserId(0)
    setUsername('Guest')
    setRepos([])
  }

  const handleLogin = () => {
    window.location.href = 'http://localhost:8000/api/auth/github/login'
  }

  return (
    <div className="min-h-screen flex flex-col items-center py-8 px-4">
      <Welcome message={message} username={username} />
      {userId === 0 ? (
        <button
          onClick={handleLogin}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
        >
          Login with GitHub
        </button>
      ) : (
        <>
          <RepoList repos={repos} />
          <button
            onClick={handleLogout}
            className="mt-4 px-4 py-2 bg-red-500 text-white rounded"
          >
            Logout
          </button>
        </>
      )}
    </div>
  )
}

export default App