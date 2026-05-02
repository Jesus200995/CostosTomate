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

export interface MercadoPropuesto {
  id: number
  nombre_mercado: string
  tipo_mercado: string
  tipo_mercado_otro?: string | null
  estado: string
  municipio: string
  localidad_colonia?: string | null
  latitud: number
  longitud: number
  dias_operacion: string[]
  horario?: string | null
  referencia?: string | null
  observaciones?: string | null
  status: string
  created_by: string
  created_by_nombre?: string | null
  tipo_capturista?: string | null
  cac_nombre?: string | null
  territorio?: string | null
  ruta?: string | null
  created_at: string
}
