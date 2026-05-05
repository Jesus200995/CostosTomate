import api from './api'
import type {
  Central, MiCentral, PropuestaCentral, PropuestaCentralCreate,
  ReporteJitomateCreate, ReporteJitomateOut, ReporteJitomateDetalle,
  HistorialJitomateItem
} from '@/types'

// ── Centrales ──

export const centralesService = {
  async getEstadosDisponibles(): Promise<string[]> {
    const { data } = await api.get<string[]>('/centrales/estados-disponibles')
    return data
  },

  async getMunicipiosDisponibles(estado: string): Promise<string[]> {
    const { data } = await api.get<string[]>('/centrales/municipios-disponibles', { params: { estado } })
    return data
  },

  async getCentrales(params?: { estado?: string; municipio?: string; nombre?: string }): Promise<Central[]> {
    const { data } = await api.get<Central[]>('/centrales', { params })
    return data
  },

  async getCentralesTodas(): Promise<Central[]> {
    const { data } = await api.get<Central[]>('/centrales/todas')
    return data
  },

  async getCentral(id: number): Promise<Central> {
    const { data } = await api.get<Central>(`/centrales/${id}`)
    return data
  },

  async getMisCentrales(): Promise<MiCentral[]> {
    const { data } = await api.get<MiCentral[]>('/centrales/capturista/mis-centrales')
    return data
  },

  async addMiCentral(central_id: number, es_favorita = false): Promise<MiCentral> {
    const { data } = await api.post<MiCentral>('/centrales/capturista/mis-centrales', { central_id, es_favorita })
    return data
  },

  async removeMiCentral(relacionId: number): Promise<void> {
    await api.delete(`/centrales/capturista/mis-centrales/${relacionId}`)
  },

  async getPropuestas(): Promise<PropuestaCentral[]> {
    const { data } = await api.get<PropuestaCentral[]>('/centrales/capturista/propuestas')
    return data
  },

  async proponerCentral(payload: PropuestaCentralCreate): Promise<PropuestaCentral> {
    const { data } = await api.post<PropuestaCentral>('/centrales/propuestas', payload)
    return data
  },
}

// ── Jitomate ──

export const jitomateService = {
  async crearReporte(payload: ReporteJitomateCreate): Promise<ReporteJitomateOut> {
    const { data } = await api.post<ReporteJitomateOut>('/jitomate/reportes', payload)
    return data
  },

  async getReportes(params?: { central_id?: number; fecha_desde?: string; fecha_hasta?: string }): Promise<ReporteJitomateOut[]> {
    const { data } = await api.get<ReporteJitomateOut[]>('/jitomate/reportes', { params })
    return data
  },

  async getReporte(id: number): Promise<ReporteJitomateDetalle> {
    const { data } = await api.get<ReporteJitomateDetalle>(`/jitomate/reportes/${id}`)
    return data
  },

  async getHistorial(params?: {
    central_id?: number
    fecha_desde?: string
    fecha_hasta?: string
    corte?: string
  }): Promise<HistorialJitomateItem[]> {
    const { data } = await api.get<HistorialJitomateItem[]>('/jitomate/historial', { params })
    return data
  },
}
