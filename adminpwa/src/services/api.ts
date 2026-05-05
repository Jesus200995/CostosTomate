import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.PROD
    ? 'https://adminmonitoreo.geodatos.com.mx/api'
    : '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor: agrega token como query param (admin endpoints lo esperan así)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    if (!config.params) config.params = {}
    config.params.token = token
  }
  return config
})

export default api
