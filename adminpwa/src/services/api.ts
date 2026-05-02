import axios from 'axios'

// Siempre usar API de producción (el backend local no está configurado)
const API_URL = 'https://apicostos.sembrandodatos.com/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para agregar token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token && config.params) {
    config.params.token = token
  }
  return config
})

export default api
