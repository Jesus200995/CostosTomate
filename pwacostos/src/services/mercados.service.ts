import api from './api'
import type {
  Categoria, Subcategoria, Producto, Unidad,
  Mercado, CatalogoMercado, ReporteOut, ReporteDetalleOut, DetalleItem, PrecioHistorialItem,
  MercadoPropuestoCreate, MercadoPropuesto, HistorialGeneralItem
} from '@/types'

export const mercadosService = {
  // Catálogo de mercados
  async getCatalogoEntidades(): Promise<string[]> {
    const { data } = await api.get<string[]>('/mercados/catalogo/entidades')
    return data
  },

  async getCatalogoMunicipios(entidad: string): Promise<string[]> {
    const { data } = await api.get<string[]>('/mercados/catalogo/municipios', {
      params: { entidad }
    })
    return data
  },

  async searchCatalogo(params: { entidad?: string; municipio?: string; nombre?: string; tipo?: string }): Promise<CatalogoMercado[]> {
    const { data } = await api.get<CatalogoMercado[]>('/mercados/catalogo', { params })
    return data
  },

  async getCatalogoTodos(): Promise<CatalogoMercado[]> {
    const { data } = await api.get<CatalogoMercado[]>('/mercados/catalogo/todos')
    return data
  },

  async getMunicipiosTodos(): Promise<Record<string, string[]>> {
    const { data } = await api.get<Record<string, string[]>>('/mercados/catalogo/municipios-todos')
    return data
  },

  async getCatalogosOffline(): Promise<{
    categorias: Categoria[]
    subcategorias: Subcategoria[]
    productos: Producto[]
    unidades: Array<Unidad & { tipo?: string }>
  }> {
    const { data } = await api.get('/mercados/catalogos-offline')
    return data
  },

  // Catálogos de productos
  async getCategorias(): Promise<Categoria[]> {
    const { data } = await api.get<Categoria[]>('/mercados/categorias')
    return data
  },

  async getSubcategorias(categoria_id: string): Promise<Subcategoria[]> {
    const { data } = await api.get<Subcategoria[]>('/mercados/subcategorias', {
      params: { categoria_id }
    })
    return data
  },

  async getProductos(subcategoria_id: string): Promise<Producto[]> {
    const { data } = await api.get<Producto[]>('/mercados/productos', {
      params: { subcategoria_id }
    })
    return data
  },

  async getUnidades(subcategoria_id: string, tipo_precio?: string): Promise<Unidad[]> {
    const params: Record<string, string> = { subcategoria_id }
    if (tipo_precio) params.tipo_precio = tipo_precio
    const { data } = await api.get<Unidad[]>('/mercados/unidades', { params })
    return data
  },

  // Mercados del usuario
  async getMercados(): Promise<Mercado[]> {
    const { data } = await api.get<Mercado[]>('/mercados/')
    return data
  },

  async addMercado(catalogo_mercado_id: number): Promise<Mercado> {
    const { data } = await api.post<Mercado>('/mercados/', { catalogo_mercado_id })
    return data
  },

  async deleteMercado(id: number): Promise<void> {
    await api.delete(`/mercados/${id}`)
  },

  // Reportes
  async createReporte(payload: { mercado_id: number; tipo_precio: string; items: DetalleItem[] }): Promise<ReporteOut> {
    const { data } = await api.post<ReporteOut>('/mercados/reportes', payload)
    return data
  },

  async getReportes(mercado_id?: number): Promise<ReporteOut[]> {
    const { data } = await api.get<ReporteOut[]>('/mercados/reportes', {
      params: mercado_id ? { mercado_id } : {}
    })
    return data
  },

  async getReporte(id: number): Promise<ReporteDetalleOut> {
    const { data } = await api.get<ReporteDetalleOut>(`/mercados/reportes/${id}`)
    return data
  },

  // Precio individual
  async savePrecioIndividual(payload: {
    mercado_id: number
    tipo_precio: string
    producto_id: number
    precio: number
    unidad: string
  }): Promise<PrecioHistorialItem> {
    const { data } = await api.post<PrecioHistorialItem>('/mercados/precio', payload)
    return data
  },

  async getPreciosHistorial(mercado_id: number): Promise<PrecioHistorialItem[]> {
    const { data } = await api.get<PrecioHistorialItem[]>('/mercados/precios-historial', {
      params: { mercado_id }
    })
    return data
  },

  // Mercados propuestos
  async proponerMercado(payload: MercadoPropuestoCreate): Promise<MercadoPropuesto> {
    const { data } = await api.post<MercadoPropuesto>('/mercados/proponer', payload)
    return data
  },

  async getMercadosPropuestos(): Promise<MercadoPropuesto[]> {
    const { data } = await api.get<MercadoPropuesto[]>('/mercados/propuestos')
    return data
  },

  async getMercadosRecientes(): Promise<Mercado[]> {
    const { data } = await api.get<Mercado[]>('/mercados/recientes')
    return data
  },

  async getHistorialGeneral(params?: { fecha_desde?: string; fecha_hasta?: string }): Promise<HistorialGeneralItem[]> {
    const { data } = await api.get<HistorialGeneralItem[]>('/mercados/historial-general', { params })
    return data
  }
}
