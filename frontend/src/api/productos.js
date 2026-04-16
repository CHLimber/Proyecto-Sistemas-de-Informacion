import client from './client'

export const productosApi = {
  listar:     ()           => client.get('/productos/'),
  obtener:    (id)         => client.get(`/productos/${id}`),
  crear:      (data)       => client.post('/productos/', data),
  actualizar: (id, data)   => client.put(`/productos/${id}`, data),
  desactivar: (id)         => client.delete(`/productos/${id}`),
}
