import api from './api'
import type { Estado, Municipio } from '@/types'

export const catalogoService = {
  async getEstados(): Promise<Estado[]> {
    const { data } = await api.get<Estado[]>('/catalogos/estados')
    return data
  },

  async getMunicipios(cve_ent: string): Promise<Municipio[]> {
    const { data } = await api.get<Municipio[]>('/catalogos/municipios', {
      params: { cve_ent }
    })
    return data
  }
}
