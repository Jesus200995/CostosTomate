from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    curp: str
    tipo_capturista: str = "CAPTURISTA"
    estado: str
    municipio: int
    localidad: Optional[str] = None
    telefono: Optional[str] = None
    consent: bool = False
    cac_id: Optional[str] = None
    cac_nombre: Optional[str] = None
    territorio: Optional[str] = None
    ruta: Optional[str] = None
    # COM_COMERCIALIZACION (legacy, ya no se pide)
    rol_comision: Optional[str] = None
    # OFICINAS
    correo_institucional: Optional[str] = None
    rol_interno: Optional[str] = None


class UpdateProfileRequest(BaseModel):
    name: str
    curp: str
    tipo_capturista: str
    estado: str
    municipio: int
    localidad: Optional[str] = None
    telefono: Optional[str] = None
    cac_id: Optional[str] = None
    cac_nombre: Optional[str] = None
    territorio: Optional[str] = None
    ruta: Optional[str] = None
    rol_comision: Optional[str] = None
    correo_institucional: Optional[str] = None
    rol_interno: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: str
    name: str
    email: str
    avatar: Optional[str] = None
    createdAt: str
    curp: Optional[str] = None
    tipo_capturista: Optional[str] = None
    estado: Optional[str] = None
    municipio: Optional[int] = None
    localidad: Optional[str] = None
    telefono: Optional[str] = None
    consent: bool = False
    cac_id: Optional[str] = None
    cac_nombre: Optional[str] = None
    territorio: Optional[str] = None
    ruta: Optional[str] = None
    rol_comision: Optional[str] = None
    correo_institucional: Optional[str] = None
    rol_interno: Optional[str] = None


class AuthResponse(BaseModel):
    user: UserPublic
    token: str


class EstadoOut(BaseModel):
    cve_ent: str
    nom_ent: str


class MunicipioOut(BaseModel):
    clave_mun: int
    nomgeo: str
    cve_ent: str
    territorio: Optional[str] = None


# ── Mercados / Precios ──

class CategoriaOut(BaseModel):
    id: str
    nombre: str
    descripcion: Optional[str] = None


class SubcategoriaOut(BaseModel):
    id: str
    categoria_id: str
    nombre: str


class ProductoOut(BaseModel):
    id: int
    subcategoria_id: str
    nombre: str


class UnidadOut(BaseModel):
    id: int
    subcategoria_id: str
    nombre: str


class CatalogoMercadoOut(BaseModel):
    id: int
    market_id: str
    nombre: str
    tipo: str
    entidad: str
    municipio: str
    localidad: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    n_establecimientos: int = 0
    cve_ent: Optional[str] = None
    cve_mun: Optional[str] = None


class MercadoCreate(BaseModel):
    catalogo_mercado_id: int


class MercadoOut(BaseModel):
    id: int
    nombre: str
    tipo: str
    entidad: str
    municipio: str
    localidad: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    n_establecimientos: int = 0
    created_at: str


class DetalleItem(BaseModel):
    producto_id: int
    precio: float
    unidad: str


class ReporteCreate(BaseModel):
    mercado_id: int
    tipo_precio: str
    items: List[DetalleItem]


class ReporteOut(BaseModel):
    id: int
    mercado_id: int
    tipo_precio: str
    fecha: str
    created_at: str
    total_productos: int


class DetalleItemOut(BaseModel):
    id: int
    producto_id: int
    producto_nombre: str
    precio: float
    unidad: str
    subcategoria_id: str


class ReporteDetalleOut(BaseModel):
    id: int
    mercado_id: int
    mercado_nombre: str
    tipo_precio: str
    fecha: str
    created_at: str
    items: List[DetalleItemOut]


# ── Precio individual ──

class PrecioIndividualCreate(BaseModel):
    mercado_id: int
    tipo_precio: str
    producto_id: int
    precio: float
    unidad: str


class PrecioHistorialItem(BaseModel):
    id: int
    producto_id: int
    producto_nombre: str
    subcategoria_nombre: str
    categoria_id: str
    precio: float
    unidad: str
    tipo_precio: str
    fecha: str
    created_at: str


# ── Mercados propuestos ──

class HistorialGeneralItem(BaseModel):
    id: int
    mercado_id: int
    mercado_nombre: str
    mercado_entidad: str
    mercado_municipio: str
    producto_id: int
    producto_nombre: str
    subcategoria_nombre: str
    categoria_id: str
    precio: float
    unidad: str
    tipo_precio: str
    fecha: str
    created_at: str


class RegistroPrecioAdmin(BaseModel):
    id: int
    user_id: str
    user_name: str
    user_email: str
    mercado_id: int
    mercado_nombre: str
    mercado_entidad: str
    mercado_municipio: str
    producto_id: int
    producto_nombre: str
    subcategoria_nombre: str
    categoria_id: str
    precio: float
    unidad: str
    tipo_precio: str
    fecha: str
    created_at: str


class MercadoPropuestoCreate(BaseModel):
    nombre_mercado: str
    tipo_mercado: str
    tipo_mercado_otro: Optional[str] = None
    estado: str
    municipio: str
    localidad_colonia: Optional[str] = None
    latitud: float
    longitud: float
    dias_operacion: List[str]
    horario: Optional[str] = None
    referencia: Optional[str] = None
    observaciones: Optional[str] = None


class MercadoPropuestoOut(BaseModel):
    id: int
    nombre_mercado: str
    tipo_mercado: str
    tipo_mercado_otro: Optional[str] = None
    estado: str
    municipio: str
    localidad_colonia: Optional[str] = None
    latitud: float
    longitud: float
    dias_operacion: List[str]
    horario: Optional[str] = None
    referencia: Optional[str] = None
    observaciones: Optional[str] = None
    status: str
    created_at: str


# ── Centrales de Abasto ──

class CentralOut(BaseModel):
    id: int
    nombre_central: str
    tipo: Optional[str] = None
    municipio: Optional[str] = None
    estado: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    estatus: str
    visible_pwa: bool
    created_at: Optional[str] = None


class CentralCreate(BaseModel):
    central_id: int
    es_favorita: bool = False


class CaptoristasCentralOut(BaseModel):
    id: int
    central_id: int
    es_favorita: bool
    created_at: str
    nombre_central: str
    tipo: Optional[str] = None
    municipio: Optional[str] = None
    estado: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None


class PropuestaCentralCreate(BaseModel):
    nombre_central: str
    tipo: Optional[str] = None
    municipio: str
    estado: str
    latitud: float
    longitud: float


class PropuestaCentralOut(BaseModel):
    id: int
    nombre_central: str
    tipo: Optional[str] = None
    municipio: Optional[str] = None
    estado: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    estatus: str
    motivo_rechazo: Optional[str] = None
    created_at: str


# ── Jitomate ──

class PrecioCalidadCreate(BaseModel):
    calidad: str
    precio: Optional[float] = None
    sin_dato: bool = False


class ReporteJitomateCreate(BaseModel):
    central_id: int
    fecha: str
    corte: str
    precios: List[PrecioCalidadCreate]
    observaciones: Optional[str] = None


class ReporteJitomateOut(BaseModel):
    id: int
    central_id: int
    central_nombre: str
    usuario_id: str
    fecha: str
    corte: str
    hora_captura: str
    captura_tardia: bool
    created_at: str


class ReporteJitomateDetalleOut(BaseModel):
    id: int
    central_id: int
    central_nombre: str
    central_estado: Optional[str] = None
    central_municipio: Optional[str] = None
    usuario_id: str
    fecha: str
    corte: str
    hora_captura: str
    captura_tardia: bool
    observaciones: Optional[str] = None
    created_at: str
    precios: List[Dict[str, Any]]


class HistorialJitomateItem(BaseModel):
    id: int
    central_id: int
    central_nombre: str
    central_estado: Optional[str] = None
    central_municipio: Optional[str] = None
    fecha: str
    corte: str
    calidad: str
    precio: Optional[float] = None
    sin_dato: bool
    captura_tardia: bool
    created_at: str
