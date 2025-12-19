import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Activity,
  Mail,
  Lock,
  Eye,
  EyeOff,
  Loader2,
  AlertCircle,
  ArrowRight,
  Shield,
  Key
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useI18n } from '../i18n'

// SSO providers
const SSO_PROVIDERS = [
  { id: 'microsoft', name: 'Microsoft', icon: '🪟', color: 'bg-blue-600 hover:bg-blue-500' },
  { id: 'google', name: 'Google', icon: '🔵', color: 'bg-red-500 hover:bg-red-400' },
  { id: 'okta', name: 'Okta', icon: '🔐', color: 'bg-indigo-600 hover:bg-indigo-500' }
]

// Demo accounts info
const DEMO_ACCOUNTS = [
  { email: 'admin@synapsix.io', role: 'Admin', password: 'admin123' },
  { email: 'operator@synapsix.io', role: 'Operator', password: 'operator123' },
  { email: 'analyst@synapsix.io', role: 'Analyst', password: 'analyst123' },
  { email: 'viewer@synapsix.io', role: 'Viewer', password: 'viewer123' }
]

function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login, loginWithSSO, isAuthenticated, isLoading, authError } = useAuth()
  const { t } = useI18n()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(false)
  const [showDemoAccounts, setShowDemoAccounts] = useState(false)

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const from = location.state?.from?.pathname || '/'
      navigate(from, { replace: true })
    }
  }, [isAuthenticated, navigate, location])

  const handleSubmit = async (e) => {
    e.preventDefault()
    const result = await login(email, password)
    if (result.success) {
      if (rememberMe) {
        localStorage.setItem('synapsix_remember_email', email)
      } else {
        localStorage.removeItem('synapsix_remember_email')
      }
    }
  }

  const handleSSOLogin = async (provider) => {
    await loginWithSSO(provider)
  }

  const fillDemoAccount = (account) => {
    setEmail(account.email)
    setPassword(account.password)
    setShowDemoAccounts(false)
  }

  // Load remembered email
  useEffect(() => {
    const rememberedEmail = localStorage.getItem('synapsix_remember_email')
    if (rememberedEmail) {
      setEmail(rememberedEmail)
      setRememberMe(true)
    }
  }, [])

  return (
    <div className="min-h-screen bg-industrial-darker flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-industrial-dark via-industrial-darker to-black relative overflow-hidden">
        {/* Background animation */}
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
        </div>

        <div className="relative z-10 flex flex-col justify-center items-center w-full p-12">
          {/* Logo */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="flex items-center gap-4 mb-8"
          >
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500 via-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
              <Activity className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Synapsix</h1>
              <p className="text-gray-400">Industrial Observability Platform</p>
            </div>
          </motion.div>

          {/* Features */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="space-y-6 max-w-md"
          >
            {[
              { icon: Activity, title: 'Real-time Monitoring', desc: 'Track production metrics and equipment status in real-time' },
              { icon: Shield, title: 'Security & Compliance', desc: 'Enterprise-grade security with audit trails' },
              { icon: Key, title: 'AI-Powered Insights', desc: 'Intelligent alerts and predictive analytics' }
            ].map((feature, index) => (
              <div key={index} className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-industrial-card/50 border border-industrial-border flex items-center justify-center flex-shrink-0">
                  <feature.icon className="w-5 h-5 text-cyan-400" />
                </div>
                <div>
                  <h3 className="font-medium text-white">{feature.title}</h3>
                  <p className="text-sm text-gray-500">{feature.desc}</p>
                </div>
              </div>
            ))}
          </motion.div>
        </div>
      </div>

      {/* Right side - Login form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md"
        >
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 via-blue-500 to-purple-600 flex items-center justify-center">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Synapsix</h1>
              <p className="text-xs text-gray-500">Industrial Observability</p>
            </div>
          </div>

          <div className="bg-industrial-dark/50 border border-industrial-border rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-white mb-2">
              {t('login.title') || 'Welcome back'}
            </h2>
            <p className="text-gray-500 mb-8">
              {t('login.subtitle') || 'Sign in to your account to continue'}
            </p>

            {/* Error message */}
            {authError && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-2 p-3 mb-6 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm"
              >
                <AlertCircle className="w-4 h-4" />
                {authError}
              </motion.div>
            )}

            {/* Login form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Email */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  {t('login.email') || 'Email'}
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@company.com"
                    required
                    className="w-full pl-10 pr-4 py-3 rounded-lg bg-industrial-darker border border-industrial-border focus:border-cyan-500/50 focus:outline-none text-white placeholder-gray-600"
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  {t('login.password') || 'Password'}
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    className="w-full pl-10 pr-12 py-3 rounded-lg bg-industrial-darker border border-industrial-border focus:border-cyan-500/50 focus:outline-none text-white placeholder-gray-600"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              {/* Remember me & Forgot password */}
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 rounded border-industrial-border bg-industrial-darker text-cyan-500 focus:ring-cyan-500/50"
                  />
                  <span className="text-sm text-gray-400">
                    {t('login.rememberMe') || 'Remember me'}
                  </span>
                </label>
                <button
                  type="button"
                  className="text-sm text-cyan-400 hover:text-cyan-300 transition-colors"
                >
                  {t('login.forgotPassword') || 'Forgot password?'}
                </button>
              </div>

              {/* Submit button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex items-center justify-center gap-2 py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-medium hover:from-cyan-400 hover:to-blue-400 transition-all disabled:opacity-50"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <>
                    {t('login.signIn') || 'Sign in'}
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </form>

            {/* Divider */}
            <div className="flex items-center gap-4 my-6">
              <div className="flex-1 h-px bg-industrial-border" />
              <span className="text-sm text-gray-500">
                {t('login.or') || 'or continue with'}
              </span>
              <div className="flex-1 h-px bg-industrial-border" />
            </div>

            {/* SSO buttons */}
            <div className="grid grid-cols-3 gap-3">
              {SSO_PROVIDERS.map((provider) => (
                <button
                  key={provider.id}
                  onClick={() => handleSSOLogin(provider.id)}
                  className={`flex items-center justify-center gap-2 py-2.5 rounded-lg ${provider.color} text-white transition-colors`}
                >
                  <span>{provider.icon}</span>
                  <span className="text-sm hidden sm:inline">{provider.name}</span>
                </button>
              ))}
            </div>

            {/* Demo accounts */}
            <div className="mt-6 pt-6 border-t border-industrial-border">
              <button
                onClick={() => setShowDemoAccounts(!showDemoAccounts)}
                className="w-full text-center text-sm text-gray-500 hover:text-gray-400 transition-colors"
              >
                {showDemoAccounts ? 'Hide' : 'Show'} demo accounts
              </button>

              {showDemoAccounts && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="mt-4 space-y-2"
                >
                  {DEMO_ACCOUNTS.map((account) => (
                    <button
                      key={account.email}
                      onClick={() => fillDemoAccount(account)}
                      className="w-full flex items-center justify-between p-2 rounded-lg bg-industrial-border/30 hover:bg-industrial-border/50 transition-colors"
                    >
                      <div className="text-left">
                        <p className="text-sm text-white">{account.email}</p>
                        <p className="text-xs text-gray-500">{account.role}</p>
                      </div>
                      <ArrowRight className="w-4 h-4 text-gray-500" />
                    </button>
                  ))}
                </motion.div>
              )}
            </div>
          </div>

          {/* Footer */}
          <p className="text-center text-sm text-gray-600 mt-6">
            {t('login.terms') || 'By signing in, you agree to our Terms of Service and Privacy Policy'}
          </p>
        </motion.div>
      </div>
    </div>
  )
}

export default LoginPage
