import client from './client'

export const entidadesApi = {
  listar: () => client.get('/entidades/'),
  obtener: (id) => client.get(`/entidades/${id}`),
  crear: (data) => client.post('/entidades/', data),
  actualizar: (id, data) => client.put(`/entidades/${id}`, data),
  desactivar: (id) => client.delete(`/entidades/${id}`),
}
