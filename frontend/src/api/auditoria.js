import client from './client'

export function getAuditoria(params = {}) {
  return client.get('/auditoria/', { params })
}

export function getAuditoriaPorId(id) {
  return client.get(`/auditoria/${id}`)
}

export function getAcciones() {
  return client.get('/auditoria/acciones')
}

export function getModulos() {
  return client.get('/auditoria/modulos')
}
