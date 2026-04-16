export default function ModuloPlaceholder({ nombre, descripcion, icon }) {
  return (
    <div>
      <div className="page-header">
        <div>
          <h1>{nombre}</h1>
          <p>{descripcion}</p>
        </div>
        <button className="btn btn-primary">
          + Nuevo
        </button>
      </div>

      <div className="card">
        <div className="empty-state">
          <div className="icon">{icon}</div>
          <p>Este módulo está en desarrollo.</p>
          <p className="text-sm" style={{ marginTop: 6 }}>
            Los datos reales se mostrarán cuando esté conectado al backend.
          </p>
        </div>
      </div>
    </div>
  )
}
