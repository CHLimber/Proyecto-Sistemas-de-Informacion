/** Formatea un número como moneda boliviana: Bs 1.234,56 */
export function formatBs(monto) {
  if (monto == null) return '—'
  return `Bs ${Number(monto).toLocaleString('es-BO', { minimumFractionDigits: 2 })}`
}

/** Formatea una fecha ISO a dd/mm/aaaa */
export function formatFecha(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleDateString('es-BO')
}
