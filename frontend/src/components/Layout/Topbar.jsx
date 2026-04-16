import { useLocation } from 'react-router-dom'
import { useTheme } from '../../context/ThemeContext'

const TITULOS = {
  '/':              ['Dashboard',          'Resumen general del sistema'],
  '/entidades':     ['Entidades',          'Clientes, empleados y proveedores'],
  '/cotizaciones':  ['Cotizaciones',       'Gestión de propuestas comerciales'],
  '/proyectos':     ['Proyectos',          'Seguimiento de proyectos activos'],
  '/ordenes':       ['Órdenes de trabajo', 'Asignación y seguimiento de OT'],
  '/mantenimiento': ['Mantenimiento',      'Mantenimientos programados y correctivos'],
  '/finanzas':      ['Finanzas',           'Pagos y gastos operativos'],
  '/catalogos':     ['Catálogos',          'Datos maestros del sistema'],
  '/usuarios':      ['Usuarios',           'Gestión de accesos y roles'],
}

export default function Topbar() {
  const { tema, toggleTema } = useTheme()
  const { pathname } = useLocation()
  const [titulo, subtitulo] = TITULOS[pathname] || ['ServiControl', '']

  return (
    <header className="topbar">
      <div className="topbar-title">
        {titulo}
        {subtitulo && <span>— {subtitulo}</span>}
      </div>

      <button className="theme-toggle" onClick={toggleTema} title="Cambiar tema">
        {tema === 'dark' ? '☀️' : '🌙'}
      </button>
    </header>
  )
}
