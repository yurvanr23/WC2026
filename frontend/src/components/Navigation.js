import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../utils/AuthContext';

function Navigation() {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50 backdrop-blur-lg bg-opacity-90">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">⚽</span>
            </div>
            <span className="text-2xl font-bold gradient-text">WC26</span>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-8">
            {user ? (
              <>
                <Link
                  to="/dashboard"
                  className="text-slate-300 hover:text-white transition-colors duration-200"
                >
                  Dashboard
                </Link>
                <Link
                  to="/leaderboard"
                  className="text-slate-300 hover:text-white transition-colors duration-200"
                >
                  Leaderboard
                </Link>
                <Link
                  to="/simulation"
                  className="text-slate-300 hover:text-white transition-colors duration-200"
                >
                  Simulation
                </Link>
                <Link
                  to="/profile"
                  className="text-slate-300 hover:text-white transition-colors duration-200"
                >
                  Profile
                </Link>
              </>
            ) : (
              <>
                <Link
                  to="/leaderboard"
                  className="text-slate-300 hover:text-white transition-colors duration-200"
                >
                  Leaderboard
                </Link>
                <Link
                  to="/simulation"
                  className="text-slate-300 hover:text-white transition-colors duration-200"
                >
                  Simulation
                </Link>
              </>
            )}
          </div>

          {/* Auth Buttons */}
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <div className="hidden md:block text-slate-300">
                  <span className="text-sm">Welcome, </span>
                  <span className="font-semibold text-indigo-400">{user.username}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-all duration-200"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="px-4 py-2 text-slate-300 hover:text-white transition-colors duration-200"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg transition-all duration-200 shadow-lg hover:shadow-indigo-500/50"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navigation;
