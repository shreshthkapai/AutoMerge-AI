import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

interface Repo {
  name: string
  full_name: string
}

interface RepoListProps {
  repos: Repo[]
}

export const RepoList: React.FC<RepoListProps> = ({ repos }) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8, delay: 0.3 }}
      className="w-full max-w-2xl"
    >
      <h2 className="text-2xl font-semibold text-gray-300 mb-4">Your Repositories</h2>
      <ul className="space-y-3">
        {repos.length > 0 ? (
          repos.map((repo, index) => (
            <motion.li
              key={repo.full_name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-[#161b22] p-4 rounded-md border border-[#30363d] hover:bg-[#21262d] transition-colors duration-200"
            >
              <Link to={`/repos/${encodeURIComponent(repo.full_name)}/issues`} className="block">
                <span className="text-gray-100 font-medium">{repo.name}</span>
                <span className="text-gray-400 text-sm block">{repo.full_name}</span>
              </Link>
            </motion.li>
          ))
        ) : (
          <p className="text-gray-400">No repositories found.</p>
        )}
      </ul>
    </motion.div>
  )
}