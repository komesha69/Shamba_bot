/**
 * SHAMBA — Part 1 Minimal Protected Dashboard Verification Page
 * Mpelabushi Farms
 *
 * NOTE: As per Part 1 specifications, this is NOT the full farm dashboard.
 * It exists purely as a protected route to verify authentication, session state,
 * role-based access control, and clean logout.
 */
import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { LogOut, Shield, Key, CheckCircle, Clock, UserCheck } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    await logout();
  };

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 flex flex-col justify-between selection:bg-emerald-800 selection:text-white">
      {/* Background Subtle Gradient */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_-20%,rgba(16,85,55,0.2),rgba(12,10,9,0))] pointer-events-none" />

      {/* Top Navbar */}
      <header className="relative z-10 w-full max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex items-center justify-between border-b border-stone-800/80">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-emerald-700 flex items-center justify-center text-white font-bold text-lg shadow">
            S
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold tracking-wider text-stone-100 text-base uppercase">
                SHAMBA
              </span>
              <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/60">
                Auth Verified
              </span>
            </div>
            <p className="text-xs text-stone-400 font-medium">Mpelabushi Farms</p>
          </div>
        </div>

        <button
          type="button"
          id="logout-button-nav"
          onClick={handleLogout}
          disabled={isLoggingOut}
          className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-stone-900 hover:bg-stone-800 text-stone-300 hover:text-stone-100 border border-stone-700 text-xs font-semibold transition cursor-pointer disabled:opacity-50"
        >
          <LogOut className="w-3.5 h-3.5 text-stone-400" />
          <span>{isLoggingOut ? 'Logging out...' : 'Sign Out'}</span>
        </button>
      </header>

      {/* Main Verification Card Area */}
      <main className="relative z-10 flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 py-10">
        <div className="w-full max-w-2xl">
          <div
            id="auth-verification-card"
            className="bg-stone-900/90 backdrop-blur-sm border border-stone-800 rounded-2xl p-6 sm:p-10 shadow-2xl space-y-6"
          >
            {/* Status Header */}
            <div className="flex items-center space-x-3 p-4 rounded-xl bg-emerald-950/60 border border-emerald-800/60 text-emerald-300">
              <CheckCircle className="w-6 h-6 text-emerald-400 shrink-0" />
              <div>
                <h2 className="text-sm font-bold uppercase tracking-wider text-emerald-200">
                  Authentication successful.
                </h2>
                <p className="text-xs text-emerald-400/90 mt-0.5">
                  Part 1 Authentication &amp; Protected Route Foundation is active.
                </p>
              </div>
            </div>

            {/* User Greeting & Role Details */}
            <div className="space-y-4 pt-2">
              <div className="border-b border-stone-800 pb-4">
                <h1 className="text-2xl sm:text-3xl font-extrabold text-stone-100 tracking-tight">
                  Welcome to Shamba, {user.name}
                </h1>
                <div className="flex flex-wrap items-center gap-3 mt-3">
                  <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-stone-800 text-stone-200 text-xs font-medium border border-stone-700">
                    <Shield className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Role: <strong className="text-stone-100">{user.role}</strong></span>
                  </div>

                  <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-stone-800 text-stone-200 text-xs font-medium border border-stone-700">
                    <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Status: <strong className="text-emerald-400 capitalize">{user.status}</strong></span>
                  </div>

                  {user.last_login_at && (
                    <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-stone-800 text-stone-300 text-xs font-medium border border-stone-700">
                      <Clock className="w-3.5 h-3.5 text-stone-400" />
                      <span>Last Login: {new Date(user.last_login_at).toLocaleTimeString()}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Granted Permissions List (Backend RBAC proof) */}
              <div className="space-y-2 pt-2">
                <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-stone-400">
                  <Key className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Authorized Permissions ({user.permissions?.length || 0})</span>
                </div>
                <div className="flex flex-wrap gap-2 pt-1">
                  {user.permissions && user.permissions.length > 0 ? (
                    user.permissions.map((perm) => (
                      <span
                        key={perm}
                        className="px-2.5 py-1 rounded-md bg-stone-950 text-stone-300 border border-stone-800 text-[11px] font-mono"
                      >
                        {perm}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-stone-500 italic">No permissions assigned.</span>
                  )}
                </div>
              </div>
            </div>

            {/* Logout Primary Action */}
            <div className="pt-6 border-t border-stone-800 flex justify-end">
              <button
                type="button"
                id="logout-button-primary"
                onClick={handleLogout}
                disabled={isLoggingOut}
                className="w-full sm:w-auto px-6 py-3 rounded-xl bg-stone-800 hover:bg-stone-700 active:bg-stone-900 text-stone-200 hover:text-white text-sm font-semibold transition flex items-center justify-center space-x-2 border border-stone-700 shadow-md cursor-pointer disabled:opacity-50"
              >
                <LogOut className="w-4 h-4 text-stone-400" />
                <span>{isLoggingOut ? 'Signing out...' : 'Logout'}</span>
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 w-full max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-center text-xs text-stone-500">
        <p>&copy; {new Date().getFullYear()} Mpelabushi Farms. Shamba Operations &amp; Livestock Management.</p>
      </footer>
    </div>
  );
};
