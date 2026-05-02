import api from './api'
import type { LoginPayload, RegisterPayload, AuthResponse } from '@/types'

export const authService = {
  async login(payload: LoginPayload): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>('/auth/login', payload)
    return data
  },

  async register(payload: RegisterPayload): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>('/auth/register', {
      name: payload.name,
      email: payload.email,
      password: payload.password,
      curp: payload.curp,
      tipo_capturista: payload.tipo_capturista,
      estado: payload.estado,
      municipio: payload.municipio,
      localidad: payload.localidad || null,
      telefono: payload.telefono || null,
      consent: payload.consent,
      cac_id: payload.cac_id || null,
      cac_nombre: payload.cac_nombre || null,
      territorio: payload.territorio || null,
      ruta: payload.ruta || null,
      rol_comision: payload.rol_comision || null,
      correo_institucional: payload.correo_institucional || null,
      rol_interno: payload.rol_interno || null,
    })
    return data
  },

  async getProfile(): Promise<AuthResponse['user']> {
    const { data } = await api.get<AuthResponse['user']>('/auth/profile')
    return data
  },

  async updateProfile(payload: Record<string, unknown>): Promise<AuthResponse['user']> {
    const { data } = await api.put<AuthResponse['user']>('/auth/profile', payload)
    return data
  }
}
