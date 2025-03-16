import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';

interface HeaderProps {
  username: string;
  onLogout: () => void;
}

export const Header: React.FC<HeaderProps> = ({ username, onLogout }) => {
  const location = useLocation();

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="w-full bg-[#161b22] border-b border-[#30363d] mb-6"
    >
      <div className="max-w-6xl mx-auto px-4 py-4 flex flex-col sm:flex-row items-center justify-between">
        <div className="flex items-center mb-4 sm:mb-0">
          <Link to="/" className="text-xl font-bold text-blue-400">AutoMerge AI</Link>
          <span className="ml-4 text-gray-400">Welcome, {username}</span>
        </div>
        
        <nav className="flex items-center space-x-6">
          <Link 
            to="/" 
            className={`text-sm ${location.pathname === '/' ? 'text-blue-400' : 'text-gray-300 hover:text-white'}`}
          >
            Repositories
          </Link>
          <Link 
            to="/issues" 
            className={`text-sm ${location.pathname.includes('/issues') ? 'text-blue-400' : 'text-gray-300 hover:text-white'}`}
          >
            All Issues
          </Link>
          <button
            onClick={onLogout}
            className="ml-4 px-3 py-1.5 bg-[#21262d] text-sm text-white rounded hover:bg-[#30363d]"
          >
            Logout
          </button>
        </nav>
      </div>
    </motion.header>
  );
};

export default Header;