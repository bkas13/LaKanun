'use client';
import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function LoginPage() {
  const { user, login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const router = useRouter();

  useEffect(() => {
    if (user) router.push('/dashboard');
  }, [user, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) { setLoginError('Please fill in all fields'); return; }
    setIsLoading(true);
    try {
      setLoginError(null);
      await login(email, password, rememberMe);
      router.push('/dashboard');
    } catch (err: any) {
      const msg = err?.data?.detail || err?.message || 'An error occurred. Please try again.';
      setLoginError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const inputClass =
    'w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 outline-none bg-gray-50 focus:bg-white transition-colors';

  return (
    <div className="min-h-[calc(100vh-40px)] flex items-center justify-center px-4 bg-gradient-to-br from-cyan-50 to-blue-50 py-8">
      <div className="w-full max-w-md">
        <div className="text-center mb-5">
          <Link href="/" className="inline-flex items-center gap-1 text-cyan-700 font-bold text-xl mb-2">
            <span className="text-2xl">ल</span> Kanun
          </Link>
          <h1 className="text-lg font-semibold text-gray-800">Welcome back</h1>
          <p className="text-xs text-gray-500 mt-1">Sign in to access your dashboard</p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          {loginError && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-600 text-xs">
              {loginError}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={inputClass}
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={`${inputClass} pr-16`}
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-[11px] text-gray-400 hover:text-cyan-600 transition-colors"
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-3.5 h-3.5 rounded border-gray-300 text-cyan-600 focus:ring-cyan-500"
                />
                <span className="text-xs text-gray-500">Remember me</span>
              </label>
            </div>

            <button
              type="submit"
              disabled={isLoading || !email || !password}
              className="w-full py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white text-sm font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>
        </div>

        <p className="mt-4 text-center text-xs text-gray-500">
          Don&apos;t have an account?{' '}
          <Link href="/register" className="text-cyan-600 font-medium hover:underline">
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
}
