import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { api } from '../lib/api'
import { User, TokenPair } from '../types'

interface AuthContextType {
  user: User | null
  tokens: TokenPair | null
  isLoading: boolean
  login: (email: string, password: string, tenantSlug?: string) => Promise<void>
  logout: () => Promise<void>
  refreshToken: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [tokens, setTokens] = useState<TokenPair | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const initAuth = async () => {
      const accessToken = localStorage.getItem('access_token')
      const refreshToken = localStorage.getItem('refresh_token')
      const userData = localStorage.getItem('user')

      if (accessToken && refreshToken && userData) {
        setTokens({ access_token: accessToken, refresh_token: refreshToken })
        setUser(JSON.parse(userData))
        api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`
      }
      setIsLoading(false)
    }
    initAuth()
  }, [])

  const login = async (email: string, password: string, tenantSlug?: string) => {
    const response = await api.post('/auth/login', { email, password, tenant_slug: tenantSlug })
    const { access_token, refresh_token, ...userData } = response.data
    
    setTokens({ access_token, refresh_token })
    setUser(userData)
    
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
    localStorage.setItem('user', JSON.stringify(userData))
    
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
  }

  const logout = async () => {
    try {
      await api.post('/auth/logout')
    } finally {
      setUser(null)
      setTokens(null)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      delete api.defaults.headers.common['Authorization']
    }
  }

  const refreshToken = async () => {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) throw new Error('No refresh token')

    const response = await api.post('/auth/refresh', { refresh_token: refreshToken })
    const { access_token, refresh_token: newRefreshToken } = response.data
    
    setTokens({ access_token, refresh_token: newRefreshToken })
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', newRefreshToken)
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
  }

  return (
    <AuthContext.Provider value={{ user, tokens, isLoading, login, logout, refreshToken }}>
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