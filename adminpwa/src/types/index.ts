export interface AdminUser {
  id: number
  nombre: string
  apellido_paterno: string
  apellido_materno: string
  curp: string
  correo: string
  telefono: string
  rol: 'usuario' | 'administrador'
  estatus: 'activo' | 'inactivo'
  created_at: string
  permisos: string[]
}

export interface PWAUser {
  id: string
  name: string
  email: string
  curp: string | null
  tipo_capturista: string | null
  estado: string | null
  municipio: number | null
  localidad: string | null
  telefono: string | null
  cac_id: string | null
  cac_nombre: string | null
  territorio: string | null
  ruta: string | null
  rol_comision: string | null
  correo_institucional: string | null
  rol_interno: string | null
  created_at: string
}

export interface LoginPayload {
  correo: string
  password: string
}

export interface RegisterPayload {
  nombre: string
  apellido_paterno: string
  apellido_materno: string
  curp: string
  correo: string
  telefono: string
  password: string
  rol: 'usuario' | 'administrador'
}

export interface AuthResponse {
  user: AdminUser
  token: string
}

export interface Central {
  id: number
  nombre_central: string
  tipo: string | null
  municipio: string
  estado: string
  latitud: number | null
  longitud: number | null
  estatus: string
  visible_pwa: boolean
  created_at: string
  updated_at: string | null
  tiene_reporte?: boolean
  reporte?: ReporteResumen | null
  alertas?: Alerta[]
}

export interface ReporteResumen {
  central_id: number
  corte: string
  captura_tardia: boolean
  hora_captura: string | null
  primera: number | null
  segunda: number | null
  tercera: number | null
  sin_dato_primera: boolean
  sin_dato_segunda: boolean
  sin_dato_tercera: boolean
}

export interface ReporteJitomate {
  id: number
  fecha: string
  corte: string
  hora_captura: string | null
  captura_tardia: boolean
  observaciones: string | null
  central_id: number
  nombre_central: string
  estado: string
  municipio: string
  capturista_nombre: string
  capturista_email: string
  precio_primera: number | null
  sin_dato_primera: boolean
  precio_segunda: number | null
  sin_dato_segunda: boolean
  precio_tercera: number | null
  sin_dato_tercera: boolean
}

export interface PropuestaCentral {
  id: number
  usuario_id: string
  nombre_central: string
  tipo: string | null
  municipio: string
  estado: string
  latitud: number | null
  longitud: number | null
  estatus: string
  motivo_rechazo: string | null
  usuario_nombre: string | null
  usuario_email: string | null
  created_at: string
}

export interface DashboardData {
  calidades: CalidadStats[]
  cobertura: { total: number; con_reporte: number }
  total_reportes: number
  capturas_tardias: number
  alertas_activas: number
  por_estado: EstadoStats[]
}

export interface CalidadStats {
  calidad: string
  promedio: number
  minimo: number
  maximo: number
  con_dato: number
  sin_dato: number
}

export interface EstadoStats {
  estado: string
  promedio: number
  centrales_con_reporte: number
}

export interface Alerta {
  id: number
  central_id: number
  tipo: string
  descripcion: string | null
  fecha_alerta: string | null
  corte: string | null
  calidad: string | null
  precio_anterior: number | null
  precio_actual: number | null
  variacion_porcentaje: number | null
  estatus: string
  nombre_central?: string
  estado?: string
  municipio?: string
}

export interface MapaData {
  centrales: Central[]
  propuestas: PropuestaCentral[]
}
