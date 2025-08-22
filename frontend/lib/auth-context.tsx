"use client"

import React, { createContext, useContext, useEffect, useState } from 'react'

interface User {
  username: string
  role: string
  loginTime: string
}


interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  login: (userData: User, token: string) => void
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is already authenticated on app start
    const authToken = localStorage.getItem('authToken')
    const userData = localStorage.getItem('userData')
    
    if (authToken && userData) {
      try {
        const parsedUser = JSON.parse(userData)
        setUser(parsedUser)
      } catch (error) {
        console.error('Error parsing user data:', error)
        localStorage.removeItem('authToken')
        localStorage.removeItem('userData')
      }
    }
    
    setIsLoading(false)
  }, [])

  const login = (userData: User, token: string) => {
    setUser(userData)
    localStorage.setItem('authToken', token)
    localStorage.setItem('userData', JSON.stringify(userData))
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('authToken')
    localStorage.removeItem('userData')
    window.location.href = '/login'
  }

  const value = {
    user,
    isAuthenticated: !!user,
    login,
    logout,
    isLoading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// HOC for protecting routes
export function withAuth<P extends object>(Component: React.ComponentType<P>) {
  return function AuthenticatedComponent(props: P) {
    const { isAuthenticated, isLoading } = useAuth()
    
    useEffect(() => {
      if (!isLoading && !isAuthenticated) {
        window.location.href = '/login'
      }
    }, [isAuthenticated, isLoading])

    if (isLoading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto"></div>
            <p className="mt-2 text-muted-foreground">Загрузка...</p>
          </div>
        </div>
      )
    }

    if (!isAuthenticated) {
      return null // Will redirect to login
    }

    return <Component {...props} />
  }
}