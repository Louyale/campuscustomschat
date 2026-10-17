import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import * as api from './api'

interface AuthState {
  user: api.User | null
  ready: boolean
  login: (email: string, password: string) => Promise<api.User>
  register: (data: Parameters<typeof api.register>[0]) => Promise<api.User>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

/** Keeps the signed-in shopper in one place. The session itself lives in an HttpOnly cookie. */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<api.User | null>(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    api.getMe().then(setUser).catch(() => setUser(null)).finally(() => setReady(true))
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const signedIn = await api.login(email, password)
    setUser(signedIn)
    return signedIn
  }, [])

  const register = useCallback(async (data: Parameters<typeof api.register>[0]) => {
    const created = await api.register(data)
    setUser(created)
    return created
  }, [])

  const logout = useCallback(async () => {
    await api.logout()
    setUser(null)
  }, [])

  return <AuthContext.Provider value={{ user, ready, login, register, logout }}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const value = useContext(AuthContext)
  if (!value) throw new Error('useAuth must be used inside <AuthProvider>')
  return value
}
