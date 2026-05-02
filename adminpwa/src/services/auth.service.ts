import api from './api'
import type { LoginPayload, RegisterPayload, AuthResponse, AdminUser, PWAUser, MercadoPropuesto } from '@/types'

export const authService = {
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

  async getUsuarios(token: string): Promise<AdminUser[]> {
    const res = await api.get('/admin/usuarios', { params: { token } })
    return res.data
  },

  async updateEstatus(userId: number, estatus: string, token: string): Promise<AdminUser> {
    const res = await api.patch(`/admin/usuarios/${userId}/estatus`, { estatus }, { params: { token } })
    return res.data
  },

  async updateRol(userId: number, rol: string, token: string): Promise<AdminUser> {
    const res = await api.patch(`/admin/usuarios/${userId}/rol`, { rol }, { params: { token } })
    return res.data
  },

  async updateUsuario(userId: number, data: Partial<AdminUser>, token: string): Promise<AdminUser> {
    const res = await api.put(`/admin/usuarios/${userId}`, data, { params: { token } })
    return res.data
  },

  async deleteUsuario(userId: number, token: string): Promise<void> {
    await api.delete(`/admin/usuarios/${userId}`, { params: { token } })
  },

  async getUsuariosPWA(token: string): Promise<PWAUser[]> {
    const res = await api.get('/admin/usuarios-pwa', { params: { token } })
    return res.data
  },

  async updateUsuarioPWA(userId: string, data: Partial<PWAUser>, token: string): Promise<PWAUser> {
    const res = await api.put(`/admin/usuarios-pwa/${userId}`, data, { params: { token } })
    return res.data
  },

  async deleteUsuarioPWA(userId: string, token: string): Promise<void> {
    await api.delete(`/admin/usuarios-pwa/${userId}`, { params: { token } })
  },

  // ── Mercados propuestos ──

  async getPropuestas(token: string, status?: string): Promise<MercadoPropuesto[]> {
    const params: Record<string, string> = { token }
    if (status) params.status = status
    const res = await api.get('/admin/propuestas', { params })
    return res.data
  },

  async autorizarPropuesta(id: number, token: string): Promise<void> {
    await api.patch(`/admin/propuestas/${id}/autorizar`, null, { params: { token } })
  },

  async rechazarPropuesta(id: number, token: string): Promise<void> {
    await api.patch(`/admin/propuestas/${id}/rechazar`, null, { params: { token } })
  }
}
