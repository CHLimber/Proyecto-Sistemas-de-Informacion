import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

const client = axios.create({ baseURL: BASE_URL })

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

function clearSession() {
  localStorage.removeItem('token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('usuario')
  window.location.href = '/login'
}

// Promesa compartida: si varias peticiones fallan a la vez, todas esperan el mismo refresh
let refreshPromise = null

client.interceptors.response.use(
  (res) => res.data,
  async (err) => {
    const original = err.config

    if (err.response?.status === 401 && !original._retry) {
      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken) {
        original._retry = true

        if (!refreshPromise) {
          refreshPromise = axios
            .post(`${BASE_URL}/auth/refresh`, {}, {
              headers: { Authorization: `Bearer ${refreshToken}` },
            })
            .then(({ data }) => {
              localStorage.setItem('token', data.access_token)
              return data.access_token
            })
            .catch(() => {
              clearSession()
              return Promise.reject()
            })
            .finally(() => { refreshPromise = null })
        }

        try {
          const newToken = await refreshPromise
          original.headers.Authorization = `Bearer ${newToken}`
          const retried = await axios(original)
          return retried.data
        } catch {
          return Promise.reject(err.response?.data || err)
        }
      }

      // No hay refresh token — sesión expirada definitivamente
      if (localStorage.getItem('token')) clearSession()
    }

    return Promise.reject(err.response?.data || err)
  }
)

export default client
