import client from './client'

export const proyectosApi = {
  listar:           ()           => client.get('/proyectos/'),
  estados:          ()           => client.get('/proyectos/estados'),
  obtener:          (id)         => client.get(`/proyectos/${id}`),
  crear:            (data)       => client.post('/proyectos/', data),
  actualizar:       (id, data)   => client.put(`/proyectos/${id}`, data),
  sistemasPorEntidad: (id)       => client.get(`/entidades/${id}/sistemas`),
}
