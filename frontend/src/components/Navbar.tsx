"use client";

import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";

const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <nav className="bg-teal-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link href="/" className="text-xl font-bold">
              Sparing Mingguan
            </Link>
          </div>

          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link
                  href="/quizzes"
                  className="hover:bg-teal-700 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Quizzes
                </Link>
                <Link
                  href="/leaderboard"
                  className="hover:bg-teal-700 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Leaderboard
                </Link>
                <div className="flex items-center space-x-2">
                  <span className="text-sm">Welcome, {user?.username}!</span>
                  <button
                    onClick={logout}
                    className="bg-red-500 hover:bg-red-600 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Logout
                  </button>
                </div>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="hover:bg-teal-700 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="bg-teal-700 hover:bg-teal-800 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
