import api from './api'
import type {
  LoginPayload, RegisterPayload, AuthResponse, AdminUser, PWAUser,
  Central, PropuestaCentral, ReporteJitomate, DashboardData, MapaData, Alerta
} from '@/types'

export const authService = {
  // ── Auth ──
  async login(data: LoginPayload): Promise<AuthResponse> {
    const res = await api.post('/admin/login', data)
    return res.data
  },
  async register(data: RegisterPayload): Promise<AuthResponse> {
    const res = await api.post('/admin/register', data)
    return res.data
  },
  async getMe(token: string): Promise<AdminUser> {
    const res = await api.get('/admin/me', { params: { token } })
    return res.data
  },

  // ── Admin users ──
  async getUsuarios(): Promise<AdminUser[]> {
    const res = await api.get('/admin/usuarios')
    return res.data
  },
  async updateEstatus(userId: number, estatus: string): Promise<AdminUser> {
    const res = await api.patch(`/admin/usuarios/${userId}/estatus`, { estatus })
    return res.data
  },
  async updateRol(userId: number, rol: string): Promise<AdminUser> {
    const res = await api.patch(`/admin/usuarios/${userId}/rol`, { rol })
    return res.data
  },
  async updatePermisos(userId: number, permisos: string[]): Promise<{ permisos: string[] }> {
    const res = await api.patch(`/admin/usuarios/${userId}/permisos`, { permisos })
    return res.data
  },
  async createUsuario(data: Record<string, any>): Promise<AdminUser> {
    const res = await api.post('/admin/usuarios', data)
    return res.data
  },
  async deleteUsuario(userId: number): Promise<void> {
    await api.delete(`/admin/usuarios/${userId}`)
  },

  // ── PWA Users ──
  async getUsuariosPWA(): Promise<PWAUser[]> {
    const res = await api.get('/admin/usuarios-pwa')
    return res.data
  },
  async updateUsuarioPWA(userId: string, data: Record<string, any>): Promise<PWAUser> {
    const res = await api.put(`/admin/usuarios-pwa/${userId}`, data)
    return res.data
  },
  async deleteUsuarioPWA(userId: string): Promise<void> {
    await api.delete(`/admin/usuarios-pwa/${userId}`)
  },

  // ── Catalogos geo ──
  async getEstados(): Promise<{ cve_ent: string; nom_ent: string }[]> {
    const res = await api.get('/catalogos/estados')
    return res.data
  },
  async getMunicipios(cve_ent: string): Promise<{ clave_mun: number; nomgeo: string; cve_ent: string; territorio: string | null }[]> {
    const res = await api.get('/catalogos/municipios', { params: { cve_ent } })
    return res.data
  },

  // ── Centrales (admin CRUD) ──
  async getCentrales(): Promise<Central[]> {
    const res = await api.get('/admin/jitomate/centrales')
    return res.data
  },
  async updateCentral(id: number, data: Record<string, any>): Promise<Central> {
    const res = await api.patch(`/admin/jitomate/centrales/${id}`, null, { params: data })
    return res.data
  },

  // ── Propuestas centrales ──
  async getPropuestasCentrales(estatus?: string): Promise<PropuestaCentral[]> {
    const params: Record<string, string> = {}
    if (estatus) params.estatus = estatus
    const res = await api.get('/admin/jitomate/propuestas-centrales', { params })
    return res.data
  },
  async autorizarPropuesta(id: number): Promise<void> {
    await api.patch(`/admin/jitomate/propuestas-centrales/${id}/autorizar`)
  },
  async rechazarPropuesta(id: number, motivo?: string): Promise<void> {
    const params: Record<string, string> = {}
    if (motivo) params.motivo = motivo
    await api.patch(`/admin/jitomate/propuestas-centrales/${id}/rechazar`, null, { params })
  },

  // ── Reportes jitomate ──
  async getReportes(filtros?: Record<string, any>): Promise<ReporteJitomate[]> {
    const res = await api.get('/admin/jitomate/reportes', { params: filtros })
    return res.data
  },
  async deleteReporte(id: number): Promise<void> {
    await api.delete(`/admin/jitomate/reportes/${id}`)
  },

  // ── Dashboard ──
  async getDashboard(filtros?: Record<string, any>): Promise<DashboardData> {
    const res = await api.get('/admin/jitomate/dashboard', { params: filtros })
    return res.data
  },

  // ── Mapa ──
  async getMapa(fecha?: string, corte?: string): Promise<MapaData> {
    const params: Record<string, string> = {}
    if (fecha) params.fecha = fecha
    if (corte) params.corte = corte
    const res = await api.get('/admin/jitomate/mapa', { params })
    return res.data
  },

  // ── Alertas ──
  async getAlertas(estatus?: string): Promise<Alerta[]> {
    const params: Record<string, string> = {}
    if (estatus) params.estatus = estatus
    const res = await api.get('/admin/jitomate/alertas', { params })
    return res.data
  },
}
