import { useState, useEffect } from 'react'
import { proyectosApi } from '../../api/proyectos'
import { entidadesApi } from '../../api/entidades'
import { catalogosApi } from '../../api/catalogos'
import { cotizacionesApi } from '../../api/cotizaciones'

const BADGE_ESTADO = {
  'Planificación':  'badge-gray',
  'En ejecución':   'badge-blue',
  'Pausado':        'badge-yellow',
  'Finalizado':     'badge-green',
  'Cancelado':      'badge-red',
}

function formatFecha(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-BO')
}

export default function ProyectosPage() {
  const [proyectos, setProyectos]   = useState([])
  const [cargando, setCargando]     = useState(true)
  const [error, setError]           = useState(null)
  const [filtroEstado, setFiltroEstado] = useState('')
  const [busqueda, setBusqueda]     = useState('')
  const [detalle, setDetalle]       = useState(null)

  // Datos para el modal
  const [modalCrear, setModalCrear] = useState(false)
  const [estados, setEstados]       = useState([])
  const [clientes, setClientes]     = useState([])
  const [servicios, setServicios]   = useState([])
  const [cotizaciones, setCotizaciones] = useState([])
  const [sistemasCliente, setSistemasCliente] = useState([])
  const [form, setForm]             = useState({
    id_entidad: '', id_servicio: '', id_sistema: '', id_estado_proyecto: '',
    id_cotizacion: '', titulo: '', descripcion: '', fecha_inicio: '', fecha_fin: '',
  })
  const [guardando, setGuardando]   = useState(false)
  const [errForm, setErrForm]       = useState('')

  // Modal cambio de estado
  const [modalEstado, setModalEstado] = useState(null)
  const [nuevoEstado, setNuevoEstado] = useState('')
  const [obsEstado, setObsEstado]   = useState('')

  useEffect(() => { cargarProyectos() }, [])

  async function cargarProyectos() {
    try {
      setCargando(true)
      setProyectos(await proyectosApi.listar())
    } catch {
      setError('No se pudo cargar los proyectos.')
    } finally {
      setCargando(false)
    }
  }

  async function abrirCrear() {
    setForm({ id_entidad: '', id_servicio: '', id_sistema: '', id_estado_proyecto: '',
              id_cotizacion: '', titulo: '', descripcion: '', fecha_inicio: '', fecha_fin: '' })
    setErrForm('')
    setSistemasCliente([])
    setModalCrear(true)
    const [ests, ents, servs, cots] = await Promise.all([
      proyectosApi.estados(),
      entidadesApi.listar(),
      catalogosApi.servicios(),
      cotizacionesApi.listar(),
    ])
    setEstados(ests)
    setClientes(ents.filter(e => e.cliente))
    setServicios(servs)
    setCotizaciones(cots.filter(c => c.estado === 'aprobada'))
    if (ests.length > 0) setForm(f => ({ ...f, id_estado_proyecto: ests[0].id }))
  }

  async function onCambiarCliente(id_entidad) {
    setForm(f => ({ ...f, id_entidad, id_sistema: '', id_cotizacion: '' }))
    setSistemasCliente([])
    if (!id_entidad) return
    try {
      setSistemasCliente(await proyectosApi.sistemasPorEntidad(id_entidad))
    } catch {
      setSistemasCliente([])
    }
  }

  async function guardar(e) {
    e.preventDefault()
    if (!form.id_entidad || !form.id_servicio || !form.id_sistema || !form.titulo || !form.id_estado_proyecto) {
      setErrForm('Cliente, servicio, sistema y título son obligatorios.')
      return
    }
    setGuardando(true)
    setErrForm('')
    try {
      const nuevo = await proyectosApi.crear(form)
      setProyectos(prev => [nuevo, ...prev])
      setModalCrear(false)
    } catch (err) {
      setErrForm(err.error || 'Error al crear el proyecto.')
    } finally {
      setGuardando(false)
    }
  }

  async function cambiarEstado(e) {
    e.preventDefault()
    if (!nuevoEstado) return
    try {
      const actualizado = await proyectosApi.actualizar(modalEstado.id, {
        id_estado_proyecto: Number(nuevoEstado),
        observacion_cambio: obsEstado,
      })
      setProyectos(prev => prev.map(p => p.id === modalEstado.id ? actualizado : p))
      if (detalle?.id === modalEstado.id) setDetalle(actualizado)
      setModalEstado(null)
      setNuevoEstado('')
      setObsEstado('')
    } catch {
      alert('No se pudo cambiar el estado.')
    }
  }

  const cotizacionesCliente = cotizaciones.filter(c => c.id_entidad === Number(form.id_entidad))

  const filtrados = proyectos.filter(p => {
    const coincideEstado = filtroEstado === '' || p.estado_nombre === filtroEstado
    const coincideBusqueda = (p.titulo + p.codigo).toLowerCase().includes(busqueda.toLowerCase())
    return coincideEstado && coincideBusqueda
  })

  const nombresEstado = [...new Set(proyectos.map(p => p.estado_nombre).filter(Boolean))]

  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title">Proyectos</h1>
          <p className="page-subtitle">Seguimiento de instalaciones y obras</p>
        </div>
        <button className="btn btn-primary" onClick={abrirCrear}>+ Nuevo proyecto</button>
      </div>

      {/* Filtros */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <input className="input" style={{ flex: 1, minWidth: 200 }}
            placeholder="Buscar por título o código..."
            value={busqueda} onChange={e => setBusqueda(e.target.value)} />
          <select className="input" style={{ minWidth: 180 }}
            value={filtroEstado} onChange={e => setFiltroEstado(e.target.value)}>
            <option value="">Todos los estados</option>
            {nombresEstado.map(n => <option key={n} value={n}>{n}</option>)}
          </select>
        </div>
      </div>

      {/* Tabla */}
      <div className="card">
        {cargando ? (
          <div className="empty-state">Cargando proyectos...</div>
        ) : error ? (
          <div className="empty-state" style={{ color: 'var(--danger)' }}>{error}</div>
        ) : filtrados.length === 0 ? (
          <div className="empty-state">No hay proyectos.</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Título</th>
                  <th>Estado</th>
                  <th>Inicio</th>
                  <th>Fin</th>
                  <th style={{ width: 110 }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filtrados.map(p => (
                  <tr key={p.id}>
                    <td><code style={{ fontSize: 12 }}>{p.codigo}</code></td>
                    <td style={{ fontWeight: 500 }}>{p.titulo}</td>
                    <td>
                      <span className={`badge ${BADGE_ESTADO[p.estado_nombre] || 'badge-gray'}`}>
                        {p.estado_nombre || '—'}
                      </span>
                    </td>
                    <td className="text-sm text-muted">{formatFecha(p.fecha_inicio)}</td>
                    <td className="text-sm text-muted">{formatFecha(p.fecha_fin)}</td>
                    <td>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button className="btn btn-ghost btn-sm" title="Ver detalle"
                          onClick={() => setDetalle(p)}>👁️</button>
                        <button className="btn btn-ghost btn-sm" title="Cambiar estado"
                          onClick={() => { setModalEstado(p); setNuevoEstado(''); setObsEstado('') }}>🔄</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="text-muted text-sm" style={{ padding: '10px 0 0' }}>
          {filtrados.length} proyecto{filtrados.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Modal detalle */}
      {detalle && (
        <div className="modal-overlay" onClick={() => setDetalle(null)}>
          <div className="modal" style={{ maxWidth: 620 }} onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h2 className="modal-title">{detalle.titulo}</h2>
                <code style={{ fontSize: 12, color: 'var(--text-muted)' }}>{detalle.codigo}</code>
              </div>
              <button className="btn btn-ghost btn-sm" onClick={() => setDetalle(null)}>✕</button>
            </div>
            <div className="modal-body">
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 16 }}>
                <span className={`badge ${BADGE_ESTADO[detalle.estado_nombre] || 'badge-gray'}`}>
                  {detalle.estado_nombre}
                </span>
                {detalle.id_cotizacion && (
                  <span className="badge badge-blue">Cotización #{detalle.id_cotizacion}</span>
                )}
              </div>
              {detalle.descripcion && (
                <p className="text-sm text-muted" style={{ marginBottom: 16 }}>{detalle.descripcion}</p>
              )}
              <div className="form-grid" style={{ marginBottom: 16 }}>
                <div>
                  <div className="text-sm text-muted">Fecha inicio</div>
                  <div style={{ fontWeight: 500 }}>{formatFecha(detalle.fecha_inicio)}</div>
                </div>
                <div>
                  <div className="text-sm text-muted">Fecha fin estimada</div>
                  <div style={{ fontWeight: 500 }}>{formatFecha(detalle.fecha_fin)}</div>
                </div>
              </div>
              {detalle.historial && detalle.historial.length > 0 && (
                <>
                  <div style={{ fontWeight: 600, marginBottom: 8 }}>Historial de estados</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {detalle.historial.map((h, i) => (
                      <div key={i} style={{ fontSize: '0.82rem', color: 'var(--text-muted)', borderLeft: '2px solid var(--border)', paddingLeft: 10 }}>
                        <span style={{ fontWeight: 600, color: 'var(--text)' }}>
                          Estado #{h.id_estado_nuevo}
                        </span>
                        {' — '}{formatFecha(h.fecha_cambio)}
                        {h.observacion && <span> · {h.observacion}</span>}
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
            <div className="modal-footer">
              <button className="btn btn-ghost"
                onClick={() => { setModalEstado(detalle); setNuevoEstado(''); setObsEstado(''); setDetalle(null) }}>
                Cambiar estado
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal cambio de estado */}
      {modalEstado && (
        <div className="modal-overlay" onClick={() => setModalEstado(null)}>
          <div className="modal" style={{ maxWidth: 400 }} onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Cambiar estado</h2>
              <button className="btn btn-ghost btn-sm" onClick={() => setModalEstado(null)}>✕</button>
            </div>
            <form onSubmit={cambiarEstado}>
              <div className="modal-body">
                <p className="text-sm text-muted" style={{ marginBottom: 16 }}>
                  Proyecto: <strong>{modalEstado.titulo}</strong>
                </p>
                <div className="form-group">
                  <label className="form-label">Nuevo estado *</label>
                  <select className="input" value={nuevoEstado}
                    onChange={e => setNuevoEstado(e.target.value)}>
                    <option value="">Seleccioná</option>
                    {estados.map(e => (
                      <option key={e.id} value={e.id}
                        disabled={e.id === modalEstado.id_estado_proyecto}>
                        {e.nombre} {e.id === modalEstado.id_estado_proyecto ? '(actual)' : ''}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Observación</label>
                  <textarea className="input" rows={2} value={obsEstado}
                    onChange={e => setObsEstado(e.target.value)}
                    placeholder="Motivo del cambio..." />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-ghost" onClick={() => setModalEstado(null)}>Cancelar</button>
                <button type="submit" className="btn btn-primary" disabled={!nuevoEstado}>Confirmar</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal crear */}
      {modalCrear && (
        <div className="modal-overlay" onClick={() => setModalCrear(false)}>
          <div className="modal" style={{ maxWidth: 620 }} onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Nuevo proyecto</h2>
              <button className="btn btn-ghost btn-sm" onClick={() => setModalCrear(false)}>✕</button>
            </div>
            <form onSubmit={guardar}>
              <div className="modal-body">
                <div className="form-grid">
                  <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                    <label className="form-label">Título *</label>
                    <input className="input" value={form.titulo}
                      onChange={e => setForm(f => ({ ...f, titulo: e.target.value }))}
                      placeholder="Ej: Instalación CCTV Edificio Central" maxLength={200} />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Cliente *</label>
                    <select className="input" value={form.id_entidad}
                      onChange={e => onCambiarCliente(Number(e.target.value) || '')}>
                      <option value="">Seleccioná</option>
                      {clientes.map(c => <option key={c.id} value={c.id}>{c.nombre}</option>)}
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Servicio *</label>
                    <select className="input" value={form.id_servicio}
                      onChange={e => setForm(f => ({ ...f, id_servicio: Number(e.target.value) || '' }))}>
                      <option value="">Seleccioná</option>
                      {servicios.map(s => <option key={s.id} value={s.id}>{s.nombre}</option>)}
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Sistema *</label>
                    <select className="input" value={form.id_sistema}
                      onChange={e => setForm(f => ({ ...f, id_sistema: Number(e.target.value) || '' }))}
                      disabled={!form.id_entidad}>
                      <option value="">
                        {form.id_entidad ? sistemasCliente.length === 0 ? 'Sin sistemas' : 'Seleccioná' : 'Primero el cliente'}
                      </option>
                      {sistemasCliente.map(s => <option key={s.id} value={s.id}>{s.nombre || `Sistema #${s.id}`}</option>)}
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Estado inicial *</label>
                    <select className="input" value={form.id_estado_proyecto}
                      onChange={e => setForm(f => ({ ...f, id_estado_proyecto: Number(e.target.value) }))}>
                      {estados.map(e => <option key={e.id} value={e.id}>{e.nombre}</option>)}
                    </select>
                  </div>

                  <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                    <label className="form-label">Cotización aprobada (opcional)</label>
                    <select className="input" value={form.id_cotizacion}
                      onChange={e => setForm(f => ({ ...f, id_cotizacion: Number(e.target.value) || '' }))}
                      disabled={!form.id_entidad}>
                      <option value="">Sin cotización vinculada</option>
                      {cotizacionesCliente.map(c => (
                        <option key={c.id} value={c.id}>{c.codigo} — Bs {c.total}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Fecha inicio</label>
                    <input type="date" className="input" value={form.fecha_inicio}
                      onChange={e => setForm(f => ({ ...f, fecha_inicio: e.target.value }))} />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Fecha fin estimada</label>
                    <input type="date" className="input" value={form.fecha_fin}
                      onChange={e => setForm(f => ({ ...f, fecha_fin: e.target.value }))} />
                  </div>

                  <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                    <label className="form-label">Descripción</label>
                    <textarea className="input" rows={2} value={form.descripcion}
                      onChange={e => setForm(f => ({ ...f, descripcion: e.target.value }))}
                      placeholder="Detalles del proyecto..." />
                  </div>
                </div>
                {errForm && <div className="alert alert-danger" style={{ marginTop: 12 }}>{errForm}</div>}
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-ghost" onClick={() => setModalCrear(false)}>Cancelar</button>
                <button type="submit" className="btn btn-primary" disabled={guardando}>
                  {guardando ? 'Guardando...' : 'Crear proyecto'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  )
}
