/**
 * SHAMBA — Production Authentication & Login Page
 * Mpelabushi Farms
 */
import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Eye, EyeOff, ShieldCheck, Lock, User as UserIcon, AlertCircle, HelpCircle, X, CheckCircle2 } from 'lucide-react';

export const Login: React.FC = () => {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showForgotModal, setShowForgotModal] = useState(false);

  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // If already authenticated, redirect to dashboard immediately
  React.useEffect(() => {
    if (isAuthenticated) {
      const from = (location.state as any)?.from?.pathname || '/dashboard';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, location]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (isSubmitting) return; // Prevent duplicate requests

    const cleanIdentifier = identifier.trim();
    if (!cleanIdentifier || !password) {
      setErrorMessage('Please enter both your username/email and password.');
      return;
    }

    setErrorMessage(null);
    setIsSubmitting(true);

    try {
      const result = await login(cleanIdentifier, password);
      if (result.success) {
        const from = (location.state as any)?.from?.pathname || '/dashboard';
        navigate(from, { replace: true });
      } else {
        setErrorMessage(result.error || 'Invalid username or password.');
      }
    } catch {
      setErrorMessage('Unable to connect to Shamba. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-stone-950 text-stone-100 flex flex-col justify-between selection:bg-emerald-800 selection:text-white">
      {/* Background Subtle Agricultural Geometric Gradient */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_-20%,rgba(16,85,55,0.25),rgba(12,10,9,0))] pointer-events-none" />

      {/* Top Header Bar */}
      <header className="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-600 to-emerald-900 flex items-center justify-center shadow-md shadow-emerald-950/60 border border-emerald-500/30">
            <span className="font-serif font-black text-xl text-emerald-100 tracking-tight">S</span>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold tracking-wider text-stone-100 text-lg uppercase">
                SHAMBA
              </span>
              <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/60">
                v1.0-auth
              </span>
            </div>
            <p className="text-xs text-stone-400 font-medium">Mpelabushi Farms</p>
          </div>
        </div>

        <div className="hidden sm:flex items-center space-x-2 text-xs text-stone-400">
          <ShieldCheck className="w-4 h-4 text-emerald-500" />
          <span>Enterprise Secure Portal</span>
        </div>
      </header>

      {/* Main Content Area */}
      <section className="relative z-10 flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 py-8">
        <div className="w-full max-w-md">
          {/* Card Container */}
          <div
            id="login-card"
            className="bg-stone-900/90 backdrop-blur-sm border border-stone-800 rounded-2xl p-6 sm:p-8 shadow-2xl shadow-black/80"
          >
            {/* Title Section */}
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-emerald-950/80 border border-emerald-700/40 text-emerald-400 mb-4 shadow-inner">
                <Lock className="w-6 h-6" />
              </div>
              <h1 className="text-2xl font-bold text-stone-100 tracking-tight">
                Farm Portal Sign In
              </h1>
              <p className="text-sm text-stone-400 mt-1.5">
                Mpelabushi Farms AI Farm Assistant
              </p>
            </div>

            {/* Error Notification Container */}
            {errorMessage && (
              <div
                id="login-error-alert"
                role="alert"
                aria-live="assertive"
                className="mb-6 p-4 rounded-xl bg-red-950/50 border border-red-800/60 text-red-200 text-sm flex items-start space-x-3 animate-fadeIn"
              >
                <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-medium text-red-100">{errorMessage}</p>
                </div>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} noValidate className="space-y-5">
              {/* Username / Email Input */}
              <div>
                <label
                  htmlFor="identifier-input"
                  className="block text-xs font-semibold uppercase tracking-wider text-stone-300 mb-2"
                >
                  Email or Username
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-stone-500">
                    <UserIcon className="w-4 h-4" />
                  </div>
                  <input
                    id="identifier-input"
                    name="identifier"
                    type="text"
                    autoComplete="username"
                    disabled={isSubmitting}
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    placeholder="e.g. admin or farm.manager@mpelabushi.com"
                    required
                    className="w-full pl-10 pr-4 py-3 bg-stone-950/80 border border-stone-700/80 rounded-xl text-stone-100 placeholder-stone-500 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>
              </div>

              {/* Password Input */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label
                    htmlFor="password-input"
                    className="block text-xs font-semibold uppercase tracking-wider text-stone-300"
                  >
                    Password
                  </label>
                  <button
                    type="button"
                    id="forgot-password-link"
                    onClick={() => setShowForgotModal(true)}
                    className="text-xs font-medium text-emerald-400 hover:text-emerald-300 hover:underline transition focus:outline-none focus:ring-1 focus:ring-emerald-500 rounded px-1"
                  >
                    Forgot password?
                  </button>
                </div>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-stone-500">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    id="password-input"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    disabled={isSubmitting}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your security password"
                    required
                    className="w-full pl-10 pr-12 py-3 bg-stone-950/80 border border-stone-700/80 rounded-xl text-stone-100 placeholder-stone-500 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                  <button
                    type="button"
                    id="toggle-password-visibility"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    onClick={() => setShowPassword(!showPassword)}
                    disabled={isSubmitting}
                    className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-stone-400 hover:text-stone-200 transition focus:outline-none"
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                id="sign-in-button"
                disabled={isSubmitting}
                className="w-full mt-2 py-3.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white font-semibold text-sm tracking-wide shadow-lg shadow-emerald-950/50 transition-all flex items-center justify-center space-x-2 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:ring-offset-2 focus:ring-offset-stone-900 disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer"
              >
                {isSubmitting ? (
                  <>
                    <svg
                      className="animate-spin h-4 w-4 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8v8H4z"
                      />
                    </svg>
                    <span>Signing in...</span>
                  </>
                ) : (
                  <span>Sign In</span>
                )}
              </button>
            </form>

            {/* Credential Helper Info Box for Part 1 Testing */}
            <div className="mt-8 pt-6 border-t border-stone-800 text-xs text-stone-400">
              <div className="flex items-center space-x-2 font-semibold text-stone-300 mb-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Default Initial Administrator</span>
              </div>
              <div className="bg-stone-950/60 rounded-lg p-3 border border-stone-800/80 font-mono space-y-1 text-[11px]">
                <div className="flex justify-between">
                  <span className="text-stone-500">Username:</span>
                  <span className="text-emerald-300 font-semibold">admin</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-stone-500">Password:</span>
                  <span className="text-emerald-300 font-semibold">Admin@Mpelabushi2026!</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-center text-xs text-stone-500">
        <p>
          &copy; {new Date().getFullYear()} Mpelabushi Farms. All rights reserved. Shamba Production Assistant.
        </p>
      </footer>

      {/* Forgot Password Modal */}
      {showForgotModal && (
        <div
          id="forgot-password-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="forgot-modal-title"
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fadeIn"
        >
          <div className="bg-stone-900 border border-stone-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-lg bg-emerald-950 text-emerald-400 flex items-center justify-center border border-emerald-800/50">
                  <HelpCircle className="w-5 h-5" />
                </div>
                <div>
                  <h3 id="forgot-modal-title" className="text-lg font-bold text-stone-100">
                    Password Assistance
                  </h3>
                  <p className="text-xs text-stone-400">Mpelabushi Farms Access Security</p>
                </div>
              </div>
              <button
                type="button"
                id="close-forgot-modal"
                onClick={() => setShowForgotModal(false)}
                className="text-stone-400 hover:text-stone-100 transition p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="text-sm text-stone-300 space-y-3 leading-relaxed">
              <p>
                To maintain the integrity and bio-security of farm operations, password resets are managed directly by authorized system administrators.
              </p>
              <div className="bg-stone-950 p-3 rounded-xl border border-stone-800 text-xs text-stone-400 space-y-1.5">
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>Contact: <strong>admin@mpelabushifarms.com</strong></span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>Or speak directly with your Farm Operations Manager.</span>
                </div>
              </div>
            </div>

            <div className="pt-2">
              <button
                type="button"
                id="confirm-close-forgot-modal"
                onClick={() => setShowForgotModal(false)}
                className="w-full py-2.5 px-4 rounded-xl bg-stone-800 hover:bg-stone-700 text-stone-200 text-sm font-semibold transition cursor-pointer"
              >
                Understood
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
};
