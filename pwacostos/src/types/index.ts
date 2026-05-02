export interface User {
  id: string
  name: string
  email: string
  avatar?: string
  createdAt: string
  curp?: string
  tipo_capturista?: string
  estado?: string
  municipio?: number
  localidad?: string
  telefono?: string
  consent?: boolean
  cac_id?: string
  cac_nombre?: string
  territorio?: string
  ruta?: string
  rol_comision?: string
  correo_institucional?: string
  rol_interno?: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  name: string
  email: string
  password: string
  confirmPassword: string
  curp: string
  tipo_capturista: string
  estado: string
  municipio: number
  localidad?: string
  telefono?: string
  consent: boolean
  cac_id?: string
  cac_nombre?: string
  territorio?: string
  ruta?: string
  rol_comision?: string
  correo_institucional?: string
  rol_interno?: string
}

export interface AuthResponse {
  user: User
  token: string
}

export interface ApiError {
  message: string
  errors?: Record<string, string[]>
}

export interface Toast {
  id: number
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
  duration?: number
}

export interface Estado {
  cve_ent: string
  nom_ent: string
}

export interface Municipio {
  clave_mun: number
  nomgeo: string
  cve_ent: string
  territorio?: string | null
}

// ── Mercados / Precios ──

export interface Categoria {
  id: string
  nombre: string
  descripcion?: string
}

export interface Subcategoria {
  id: string
  categoria_id: string
  nombre: string
}

export interface Producto {
  id: number
  subcategoria_id: string
  nombre: string
}

export interface Unidad {
  id: number
  subcategoria_id: string
  nombre: string
}

export interface CatalogoMercado {
  id: number
  market_id: string
  nombre: string
  tipo: string
  entidad: string
  municipio: string
  localidad?: string
  latitud?: number
  longitud?: number
  n_establecimientos: number
  cve_ent?: string
  cve_mun?: string
}

export interface Mercado {
  id: number
  nombre: string
  tipo: string
  entidad: string
  municipio: string
  localidad?: string
  latitud?: number
  longitud?: number
  n_establecimientos: number
  created_at: string
}

export interface DetalleItem {
  producto_id: number
  precio: number
  unidad: string
}

export interface ReporteOut {
  id: number
  mercado_id: number
  tipo_precio: string
  fecha: string
  created_at: string
  total_productos: number
}

export interface DetalleItemOut {
  id: number
  producto_id: number
  producto_nombre: string
  precio: number
  unidad: string
  subcategoria_id: string
}

export interface ReporteDetalleOut {
  id: number
  mercado_id: number
  mercado_nombre: string
  tipo_precio: string
  fecha: string
  created_at: string
  items: DetalleItemOut[]
}

export interface CapturaItem {
  producto_id: number
  producto_nombre: string
  subcategoria_id: string
  categoria_id: string
  precio: number | null
  unidad: string
  unidades_disponibles: string[]
}

export interface PrecioHistorialItem {
  id: number
  producto_id: number
  producto_nombre: string
  subcategoria_nombre: string
  categoria_id: string
  precio: number
  unidad: string
  tipo_precio: string
  fecha: string
  created_at: string
}

export interface HistorialGeneralItem {
  id: number
  mercado_id: number
  mercado_nombre: string
  mercado_entidad: string
  mercado_municipio: string
  producto_id: number
  producto_nombre: string
  subcategoria_nombre: string
  categoria_id: string
  precio: number
  unidad: string
  tipo_precio: string
  fecha: string
  created_at: string
}

// ── Mercados propuestos ──

export interface MercadoPropuestoCreate {
  nombre_mercado: string
  tipo_mercado: string
  tipo_mercado_otro?: string
  estado: string
  municipio: string
  localidad_colonia?: string
  latitud: number
  longitud: number
  dias_operacion: string[]
  horario?: string
  referencia?: string
  observaciones?: string
}

export interface MercadoPropuesto {
  id: number
  nombre_mercado: string
  tipo_mercado: string
  tipo_mercado_otro?: string
  estado: string
  municipio: string
  localidad_colonia?: string
  latitud: number
  longitud: number
  dias_operacion: string[]
  horario?: string
  referencia?: string
  observaciones?: string
  status: string
  created_at: string
}
