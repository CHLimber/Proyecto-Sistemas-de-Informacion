import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout/Layout'
import LoginPage from './pages/auth/LoginPage'
import DashboardPage from './pages/dashboard/DashboardPage'
import ProductosPage from './pages/productos/ProductosPage'
import EntidadesPage from './pages/entidades/EntidadesPage'
import CotizacionesPage from './pages/cotizaciones/CotizacionesPage'
import ProyectosPage from './pages/proyectos/ProyectosPage'
import OrdenesPage from './pages/ordenes/OrdenesPage'
import MantenimientoPage from './pages/mantenimiento/MantenimientoPage'
import FinanzasPage from './pages/finanzas/FinanzasPage'
import UsuariosPage from './pages/usuarios/UsuariosPage'
import AuditoriaPage from './pages/auditoria/AuditoriaPage'
import ModuloPlaceholder from './pages/ModuloPlaceholder'

function RutaProtegida({ children }) {
  const { token } = useAuth()
  return token ? <Layout>{children}</Layout> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route path="/" element={
        <RutaProtegida><DashboardPage /></RutaProtegida>
      } />
      <Route path="/entidades" element={
        <RutaProtegida><EntidadesPage /></RutaProtegida>
      } />
      <Route path="/cotizaciones" element={
        <RutaProtegida><CotizacionesPage /></RutaProtegida>
      } />
      <Route path="/proyectos" element={
        <RutaProtegida><ProyectosPage /></RutaProtegida>
      } />
      <Route path="/ordenes" element={
        <RutaProtegida><OrdenesPage /></RutaProtegida>
      } />
      <Route path="/mantenimiento" element={
        <RutaProtegida><MantenimientoPage /></RutaProtegida>
      } />
      <Route path="/finanzas" element={
        <RutaProtegida><FinanzasPage /></RutaProtegida>
      } />
      <Route path="/productos" element={
        <RutaProtegida><ProductosPage /></RutaProtegida>
      } />
      <Route path="/catalogos" element={
        <RutaProtegida>
          <ModuloPlaceholder nombre="Catálogos" descripcion="Datos maestros del sistema" icon="📂" />
        </RutaProtegida>
      } />
      <Route path="/usuarios" element={
        <RutaProtegida><UsuariosPage /></RutaProtegida>
      } />
      <Route path="/auditoria" element={
        <RutaProtegida><AuditoriaPage /></RutaProtegida>
      } />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
