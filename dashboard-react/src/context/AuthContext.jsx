import React, { createContext, useContext, useState, useCallback, useEffect } from 'react'

const AuthContext = createContext(null)

// Simulated user roles
export const USER_ROLES = {
  ADMIN: 'admin',
  OPERATOR: 'operator',
  VIEWER: 'viewer',
  ANALYST: 'analyst'
}

// Permission definitions
export const PERMISSIONS = {
  VIEW_DASHBOARD: 'view_dashboard',
  VIEW_TECHNICAL: 'view_technical',
  VIEW_BUSINESS: 'view_business',
  VIEW_SECURITY: 'view_security',
  MANAGE_ALERTS: 'manage_alerts',
  EXECUTE_REMEDIATION: 'execute_remediation',
  EXPORT_DATA: 'export_data',
  ADMIN_SETTINGS: 'admin_settings'
}

// Role to permissions mapping
const ROLE_PERMISSIONS = {
  [USER_ROLES.ADMIN]: Object.values(PERMISSIONS),
  [USER_ROLES.OPERATOR]: [
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.VIEW_TECHNICAL,
    PERMISSIONS.VIEW_BUSINESS,
    PERMISSIONS.MANAGE_ALERTS,
    PERMISSIONS.EXECUTE_REMEDIATION,
    PERMISSIONS.EXPORT_DATA
  ],
  [USER_ROLES.ANALYST]: [
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.VIEW_TECHNICAL,
    PERMISSIONS.VIEW_BUSINESS,
    PERMISSIONS.VIEW_SECURITY,
    PERMISSIONS.EXPORT_DATA
  ],
  [USER_ROLES.VIEWER]: [
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.VIEW_TECHNICAL,
    PERMISSIONS.VIEW_BUSINESS
  ]
}

// Demo users for testing
const DEMO_USERS = {
  'admin@synapsix.io': { password: 'admin123', role: USER_ROLES.ADMIN, name: 'Admin User' },
  'operator@synapsix.io': { password: 'operator123', role: USER_ROLES.OPERATOR, name: 'Plant Operator' },
  'analyst@synapsix.io': { password: 'analyst123', role: USER_ROLES.ANALYST, name: 'Data Analyst' },
  'viewer@synapsix.io': { password: 'viewer123', role: USER_ROLES.VIEWER, name: 'Guest Viewer' }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [authError, setAuthError] = useState(null)

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const storedUser = localStorage.getItem('synapsix_user')
        const storedToken = localStorage.getItem('synapsix_token')

        if (storedUser && storedToken) {
          const userData = JSON.parse(storedUser)
          // Validate token (in real app, verify with backend)
          if (isTokenValid(storedToken)) {
            setUser(userData)
            setIsAuthenticated(true)
          } else {
            // Token expired
            logout()
          }
        }
      } catch (error) {
        console.error('Auth check failed:', error)
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  // Simple token validation (demo)
  const isTokenValid = (token) => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      return payload.exp > Date.now() / 1000
    } catch {
      return false
    }
  }

  // Generate demo JWT
  const generateToken = (user) => {
    const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
    const payload = btoa(JSON.stringify({
      sub: user.email,
      name: user.name,
      role: user.role,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + 86400 // 24 hours
    }))
    const signature = btoa('demo-signature')
    return `${header}.${payload}.${signature}`
  }

  const login = useCallback(async (email, password) => {
    setIsLoading(true)
    setAuthError(null)

    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 800))

      const demoUser = DEMO_USERS[email.toLowerCase()]

      if (!demoUser || demoUser.password !== password) {
        throw new Error('Invalid email or password')
      }

      const userData = {
        email: email.toLowerCase(),
        name: demoUser.name,
        role: demoUser.role,
        permissions: ROLE_PERMISSIONS[demoUser.role],
        avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(demoUser.name)}&background=0ea5e9&color=fff`
      }

      const token = generateToken(userData)

      // Store in localStorage
      localStorage.setItem('synapsix_user', JSON.stringify(userData))
      localStorage.setItem('synapsix_token', token)

      setUser(userData)
      setIsAuthenticated(true)

      return { success: true, user: userData }
    } catch (error) {
      setAuthError(error.message)
      return { success: false, error: error.message }
    } finally {
      setIsLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('synapsix_user')
    localStorage.removeItem('synapsix_token')
    setUser(null)
    setIsAuthenticated(false)
    setAuthError(null)
  }, [])

  const hasPermission = useCallback((permission) => {
    if (!user) return false
    return user.permissions?.includes(permission) || false
  }, [user])

  const hasRole = useCallback((role) => {
    if (!user) return false
    return user.role === role
  }, [user])

  // SSO redirect (placeholder for future implementation)
  const loginWithSSO = useCallback(async (provider) => {
    setIsLoading(true)
    try {
      // In real implementation, redirect to SSO provider
      console.log(`SSO login with ${provider} - placeholder`)

      // Simulate SSO callback with demo user
      await new Promise(resolve => setTimeout(resolve, 1000))

      const ssoUser = {
        email: 'sso-user@synapsix.io',
        name: 'SSO User',
        role: USER_ROLES.OPERATOR,
        permissions: ROLE_PERMISSIONS[USER_ROLES.OPERATOR],
        avatar: 'https://ui-avatars.com/api/?name=SSO+User&background=8b5cf6&color=fff',
        ssoProvider: provider
      }

      const token = generateToken(ssoUser)
      localStorage.setItem('synapsix_user', JSON.stringify(ssoUser))
      localStorage.setItem('synapsix_token', token)

      setUser(ssoUser)
      setIsAuthenticated(true)

      return { success: true, user: ssoUser }
    } catch (error) {
      setAuthError(error.message)
      return { success: false, error: error.message }
    } finally {
      setIsLoading(false)
    }
  }, [])

  const value = {
    user,
    isAuthenticated,
    isLoading,
    authError,
    login,
    logout,
    loginWithSSO,
    hasPermission,
    hasRole,
    PERMISSIONS,
    USER_ROLES
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext
