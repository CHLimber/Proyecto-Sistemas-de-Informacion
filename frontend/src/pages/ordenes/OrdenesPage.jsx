import { useState, useEffect } from 'react'
import { ordenesApi } from '../../api/ordenes'
import { proyectosApi } from '../../api/proyectos'
import { catalogosApi } from '../../api/catalogos'

const BADGE_ESTADO = {
  'Pendiente':   'badge-gray',
  'Asignada':    'badge-blue',
  'En proceso':  'badge-yellow',
  'Completada':  'badge-green',
  'Cancelada':   'badge-red',
}

function formatFecha(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-BO')
}

export default function OrdenesPage() {
  const [ordenes, setOrdenes]       = useState([])
  const [cargando, setCargando]     = useState(true)
  const [error, setError]           = useState(null)
  const [filtroEstado, setFiltroEstado] = useState('')
  const [busqueda, setBusqueda]     = useState('')
  const [detalle, setDetalle]       = useState(null)

  // Modal crear
  const [modalCrear, setModalCrear] = useState(false)
  const [estados, setEstados]       = useState([])
  const [proyectos, setProyectos]   = useState([])
  const [servicios, setServicios]   = useState([])
  const [empleados, setEmpleados]   = useState([])
  const [productos, setProductos]   = useState([])
  const [form, setForm]             = useState({
    id_proyecto: '', id_servicio: '', id_estado_orden: '',
    descripcion: '', fecha_ejecucion: '', tiempo_estimado: '', observaciones: '',
    empleados: [], productos: [],
  })
  const [guardando, setGuardando]   = useState(false)
  const [errForm, setErrForm]       = useState('')

  // Modal cambio estado
  const [modalEstado, setModalEstado] = useState(null)
  const [nuevoEstado, setNuevoEstado] = useState('')
  const [obsEstado, setObsEstado]   = useState('')

  useEffect(() => { cargarOrdenes() }, [])

  async function cargarOrdenes() {
    try {
      setCargando(true)
      setOrdenes(await ordenesApi.listar())
    } catch {
      setError('No se pudo cargar las órdenes.')
    } finally {
      setCargando(false)
    }
  }

  async function abrirCrear() {
    setForm({ id_proyecto: '', id_servicio: '', id_estado_orden: '',
              descripcion: '', fecha_ejecucion: '', tiempo_estimado: '', observaciones: '',
              empleados: [], productos: [] })
    setErrForm('')
    setModalCrear(true)
    const [ests, proys, servs, emps, prods] = await Promise.all([
      ordenesApi.estados(),
      proyectosApi.listar(),
      catalogosApi.servicios(),
      catalogosApi.empleados(),
      catalogosApi.categorias().then(() => import('../../api/productos').then(m => m.productosApi.listar())),
    ])
    setEstados(ests)
    setProyectos(proys)
    setServicios(servs)
    setEmpleados(emps)
    setProductos(prods)
    if (ests.length > 0) setForm(f => ({ ...f, id_estado_orden: ests[0].id }))
  }

  function toggleEmpleado(id_empleado) {
    setForm(f => {
      const existe = f.empleados.find(e => e.id_empleado === id_empleado)
      if (existe) {
        return { ...f, empleados: f.empleados.filter(e => e.id_empleado !== id_empleado) }
      }
      return { ...f, empleados: [...f.empleados, { id_empleado, es_responsable: f.empleados.length === 0 }] }
    })
  }

  function toggleResponsable(id_empleado) {
    setForm(f => ({
      ...f,
      empleados: f.empleados.map(e => ({ ...e, es_responsable: e.id_empleado === id_empleado }))
    }))
  }

  function agregarProducto() {
    setForm(f => ({ ...f, productos: [...f.productos, { id_producto: '', cantidad_asignada: 1 }] }))
  }

  function actualizarProducto(idx, campo, valor) {
    setForm(f => ({
      ...f,
      productos: f.productos.map((p, i) => i === idx ? { ...p, [campo]: valor } : p)
    }))
  }

  function quitarProducto(idx) {
    setForm(f => ({ ...f, productos: f.productos.filter((_, i) => i !== idx) }))
  }

  async function guardar(e) {
    e.preventDefault()
    if (!form.id_proyecto || !form.id_servicio || !form.id_estado_orden) {
      setErrForm('Proyecto, servicio y estado son obligatorios.')
      return
    }
    setGuardando(true)
    setErrForm('')
    try {
      const productosValidos = form.productos.filter(p => p.id_producto && p.cantidad_asignada > 0)
      const nueva = await ordenesApi.crear({ ...form, productos: productosValidos })
      setOrdenes(prev => [nueva, ...prev])
      setModalCrear(false)
    } catch (err) {
      setErrForm(err.error || 'Error al crear la orden.')
    } finally {
      setGuardando(false)
    }
  }

  async function cambiarEstado(e) {
    e.preventDefault()
    if (!nuevoEstado) return
    try {
      const actualizada = await ordenesApi.actualizar(modalEstado.id, {
        id_estado_orden: Number(nuevoEstado),
        observacion_cambio: obsEstado,
      })
      setOrdenes(prev => prev.map(o => o.id === modalEstado.id ? actualizada : o))
      setModalEstado(null)
    } catch {
      alert('No se pudo cambiar el estado.')
    }
  }

  const nombresEstado = [...new Set(ordenes.map(o => o.estado_nombre).filter(Boolean))]
  const filtradas = ordenes.filter(o => {
    const coincideEstado = filtroEstado === '' || o.estado_nombre === filtroEstado
    const coincideBusqueda = o.codigo.toLowerCase().includes(busqueda.toLowerCase())
    return coincideEstado && coincideBusqueda
  })

  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title">Órdenes de trabajo</h1>
          <p className="page-subtitle">Asignación y seguimiento de tareas técnicas</p>
        </div>
        <button className="btn btn-primary" onClick={abrirCrear}>+ Nueva OT</button>
      </div>

      {/* Filtros */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <input className="input" style={{ flex: 1, minWidth: 180 }}
            placeholder="Buscar por código..."
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
          <div className="empty-state">Cargando órdenes...</div>
        ) : error ? (
          <div className="empty-state" style={{ color: 'var(--danger)' }}>{error}</div>
        ) : filtradas.length === 0 ? (
          <div className="empty-state">No hay órdenes de trabajo.</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Estado</th>
                  <th>Proyecto</th>
                  <th>Ejecución</th>
                  <th>Horas est.</th>
                  <th style={{ width: 110 }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filtradas.map(o => (
                  <tr key={o.id}>
                    <td><code style={{ fontSize: 12 }}>{o.codigo}</code></td>
                    <td>
                      <span className={`badge ${BADGE_ESTADO[o.estado_nombre] || 'badge-gray'}`}>
                        {o.estado_nombre || '—'}
                      </span>
                    </td>
                    <td className="text-sm text-muted">Proy. #{o.id_proyecto}</td>
                    <td className="text-sm text-muted">{formatFecha(o.fecha_ejecucion)}</td>
                    <td className="text-sm text-muted">{o.tiempo_estimado ? `${o.tiempo_estimado}h` : '—'}</td>
                    <td>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button className="btn btn-ghost btn-sm" onClick={() => setDetalle(o)} title="Ver detalle">👁️</button>
                        <button className="btn btn-ghost btn-sm" title="Cambiar estado"
                          onClick={() => { setModalEstado(o); setNuevoEstado(''); setObsEstado('') }}>🔄</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="text-muted text-sm" style={{ padding: '10px 0 0' }}>
          {filtradas.length} orden{filtradas.length !== 1 ? 'es' : ''}
        </div>
      </div>

      {/* Modal detalle */}
      {detalle && (
        <div className="modal-overlay" onClick={() => setDetalle(null)}>
          <div className="modal" style={{ maxWidth: 560 }} onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h2 className="modal-title">{detalle.codigo}</h2>
                <span className={`badge ${BADGE_ESTADO[detalle.estado_nombre] || 'badge-gray'}`}>{detalle.estado_nombre}</span>
              </div>
              <button className="btn btn-ghost btn-sm" onClick={() => setDetalle(null)}>✕</button>
            </div>
            <div className="modal-body">
              {detalle.descripcion && <p className="text-sm" style={{ marginBottom: 12 }}>{detalle.descripcion}</p>}
              <div className="form-grid" style={{ marginBottom: 12 }}>
                <div><div className="text-sm text-muted">Proyecto</div><div style={{ fontWeight: 500 }}>#{detalle.id_proyecto}</div></div>
                <div><div className="text-sm text-muted">Ejecución</div><div style={{ fontWeight: 500 }}>{formatFecha(detalle.fecha_ejecucion)}</div></div>
                <div><div className="text-sm text-muted">Horas estimadas</div><div style={{ fontWeight: 500 }}>{detalle.tiempo_estimado ? `${detalle.tiempo_estimado}h` : '—'}</div></div>
              </div>
              {detalle.observaciones && <p className="text-sm text-muted">{detalle.observaciones}</p>}
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

      {/* Modal cambio estado */}
      {modalEstado && (
        <div className="modal-overlay" onClick={() => setModalEstado(null)}>
          <div className="modal" style={{ maxWidth: 400 }} onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Cambiar estado — {modalEstado.codigo}</h2>
              <button className="btn btn-ghost btn-sm" onClick={() => setModalEstado(null)}>✕</button>
            </div>
            <form onSubmit={cambiarEstado}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Nuevo estado *</label>
                  <select className="input" value={nuevoEstado} onChange={e => setNuevoEstado(e.target.value)}>
                    <option value="">Seleccioná</option>
                    {estados.map(e => (
                      <option key={e.id} value={e.id}
                        disabled={e.id === modalEstado.id_estado_orden}>
                        {e.nombre}{e.id === modalEstado.id_estado_orden ? ' (actual)' : ''}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Observación</label>
                  <textarea className="input" rows={2} value={obsEstado}
                    onChange={e => setObsEstado(e.target.value)} placeholder="Motivo..." />
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
          <div className="modal" style={{ maxWidth: 680 }} onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Nueva orden de trabajo</h2>
              <button className="btn btn-ghost btn-sm" onClick={() => setModalCrear(false)}>✕</button>
            </div>
            <form onSubmit={guardar}>
              <div className="modal-body">
                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">Proyecto *</label>
                    <select className="input" value={form.id_proyecto}
                      onChange={e => setForm(f => ({ ...f, id_proyecto: Number(e.target.value) || '' }))}>
                      <option value="">Seleccioná</option>
                      {proyectos.map(p => <option key={p.id} value={p.id}>{p.codigo} — {p.titulo}</option>)}
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
                    <label className="form-label">Estado inicial *</label>
                    <select className="input" value={form.id_estado_orden}
                      onChange={e => setForm(f => ({ ...f, id_estado_orden: Number(e.target.value) }))}>
                      {estados.map(e => <option key={e.id} value={e.id}>{e.nombre}</option>)}
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Fecha de ejecución</label>
                    <input type="date" className="input" value={form.fecha_ejecucion}
                      onChange={e => setForm(f => ({ ...f, fecha_ejecucion: e.target.value }))} />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Horas estimadas</label>
                    <input type="number" className="input" min="1" value={form.tiempo_estimado}
                      onChange={e => setForm(f => ({ ...f, tiempo_estimado: e.target.value }))}
                      placeholder="Ej: 8" />
                  </div>

                  <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                    <label className="form-label">Descripción</label>
                    <textarea className="input" rows={2} value={form.descripcion}
                      onChange={e => setForm(f => ({ ...f, descripcion: e.target.value }))}
                      placeholder="Detalle de la tarea..." />
                  </div>
                </div>

                {/* Técnicos */}
                <div style={{ fontWeight: 600, margin: '16px 0 8px', fontSize: '0.9rem' }}>
                  Técnicos asignados
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 4 }}>
                  {empleados.map(emp => {
                    const asignado = form.empleados.find(e => e.id_empleado === emp.id)
                    const esResp   = asignado?.es_responsable
                    return (
                      <div key={emp.id} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer',
                          padding: '4px 10px', borderRadius: 20,
                          background: asignado ? 'var(--accent-light)' : 'var(--bg)',
                          border: `1px solid ${asignado ? 'var(--accent)' : 'var(--border)'}`,
                          fontSize: '0.82rem' }}>
                          <input type="checkbox" checked={!!asignado}
                            onChange={() => toggleEmpleado(emp.id)} style={{ display: 'none' }} />
                          {emp.nombre}
                          {esResp && <span style={{ color: 'var(--accent)', fontWeight: 700 }}> ★</span>}
                        </label>
                        {asignado && !esResp && (
                          <button type="button" className="btn btn-ghost btn-sm"
                            title="Marcar como responsable"
                            onClick={() => toggleResponsable(emp.id)}
                            style={{ fontSize: '0.75rem', padding: '2px 6px' }}>★</button>
                        )}
                      </div>
                    )
                  })}
                </div>
                <div className="text-muted text-sm" style={{ marginBottom: 16 }}>
                  Hacé click en ★ para marcar al responsable principal.
                </div>

                {/* Productos */}
                <div style={{ fontWeight: 600, margin: '4px 0 8px', fontSize: '0.9rem' }}>Materiales</div>
                {form.productos.map((prod, idx) => (
                  <div key={idx} style={{ display: 'flex', gap: 8, marginBottom: 8, alignItems: 'center' }}>
                    <select className="input" style={{ flex: 2 }} value={prod.id_producto}
                      onChange={e => actualizarProducto(idx, 'id_producto', Number(e.target.value) || '')}>
                      <option value="">Seleccioná producto</option>
                      {productos.map(p => <option key={p.id} value={p.id}>{p.nombre}</option>)}
                    </select>
                    <input type="number" className="input" style={{ width: 80 }} min="0.01" step="0.01"
                      value={prod.cantidad_asignada}
                      onChange={e => actualizarProducto(idx, 'cantidad_asignada', e.target.value)}
                      placeholder="Cant." />
                    <button type="button" className="btn btn-ghost btn-sm"
                      style={{ color: 'var(--danger)' }} onClick={() => quitarProducto(idx)}>✕</button>
                  </div>
                ))}
                <button type="button" className="btn btn-ghost btn-sm" onClick={agregarProducto}>
                  + Agregar material
                </button>

                {errForm && <div className="alert alert-danger" style={{ marginTop: 12 }}>{errForm}</div>}
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-ghost" onClick={() => setModalCrear(false)}>Cancelar</button>
                <button type="submit" className="btn btn-primary" disabled={guardando}>
                  {guardando ? 'Guardando...' : 'Crear orden'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  )
}
