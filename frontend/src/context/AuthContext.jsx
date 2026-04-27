import { createContext, useContext, useState } from 'react'
import { authApi } from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [usuario, setUsuario] = useState(() => {
    const u = localStorage.getItem('usuario')
    return u && u !== 'undefined' ? JSON.parse(u) : null
  })

  async function login(username, password) {
    const data = await authApi.login(username, password)
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    localStorage.setItem('usuario', JSON.stringify(data.usuario))
    setToken(data.access_token)
    setUsuario(data.usuario)
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch (_) {
      // Si falla el aviso al servidor, igual limpiamos la sesión local
    }
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('usuario')
    setToken(null)
    setUsuario(null)
  }

  return (
    <AuthContext.Provider value={{ token, usuario, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
