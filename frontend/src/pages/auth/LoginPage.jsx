import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { useTheme } from '../../context/ThemeContext'

export default function LoginPage() {
  const { login } = useAuth()
  const { tema, toggleTema } = useTheme()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState(null)
  const [cargando, setCargando] = useState(false)
  const [shake, setShake] = useState(false)
  const timerRef = useRef(null)

  useEffect(() => () => clearTimeout(timerRef.current), [])

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setCargando(true)
    try {
      await login(form.username, form.password)
      navigate('/')
    } catch (err) {
      const mensaje = err?.error || 'Error al iniciar sesión'
      setError(mensaje)
      // Limpiar solo la contraseña, mantener el username
      setForm(f => ({ ...f, password: '' }))
      // Animación de shake
      setShake(true)
      setTimeout(() => setShake(false), 600)
      // Auto-dismiss a los 8 segundos
      clearTimeout(timerRef.current)
      timerRef.current = setTimeout(() => setError(null), 8000)
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="login-page" style={{ position: 'relative' }}>
      <button className="theme-toggle login-theme" onClick={toggleTema} title="Cambiar tema">
        {tema === 'dark' ? '☀️' : '🌙'}
      </button>

      <div className={`login-card${shake ? ' login-shake' : ''}`}>
        <div className="login-brand">
          <h1>Servi<span>Control</span></h1>
          <p>Sistema de gestión para seguridad electrónica</p>
        </div>

        {error && (
          <div className="login-error">
            <span>⚠️ {error}</span>
            <div className="login-error-bar" />
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Usuario</label>
            <input
              className="form-input"
              type="text"
              placeholder="Ingresa tu usuario"
              value={form.username}
              onChange={e => setForm({ ...form, username: e.target.value })}
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label className="form-label">Contraseña</label>
            <input
              className="form-input"
              type="password"
              placeholder="••••••••"
              value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })}
              required
            />
          </div>

          <button type="submit" className="login-submit" disabled={cargando}>
            {cargando ? 'Ingresando...' : 'Ingresar'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: 20, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          ServiControl v1.0 · UAGRM FICCT
        </p>
      </div>
    </div>
  )
}
