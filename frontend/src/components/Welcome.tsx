import { motion } from 'framer-motion'

interface WelcomeProps {
  message: string
  username: string // Add username prop
}

export const Welcome = ({ message, username }: WelcomeProps) => {
  return (
    <motion.div
      className="min-h-screen flex flex-col items-center justify-center py-8 px-4"
    >
      <h1 className="text-4xl font-bold text-blue-500 mb-2 tracking-tight">
        {message}
      </h1>
      {username && (
        <h2 className="text-lg text-gray-400">
          Welcome, <span className="text-white font-semibold">{username}</span>!
        </h2>
      )}
    </motion.div>
  )
}
