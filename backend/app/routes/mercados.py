from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.schemas import (
    CategoriaOut, SubcategoriaOut, ProductoOut, UnidadOut,
    MercadoCreate, MercadoOut, CatalogoMercadoOut,
    ReporteCreate, ReporteOut, ReporteDetalleOut, DetalleItemOut,
    PrecioIndividualCreate, PrecioHistorialItem,
    MercadoPropuestoCreate, MercadoPropuestoOut,
    HistorialGeneralItem
)
from app.database import get_db
from app.auth import get_current_user_id

router = APIRouter()


# ── Catálogos ──

@router.get("/categorias", response_model=List[CategoriaOut])
def list_categorias():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, descripcion FROM categorias ORDER BY nombre")
        return [dict(r) for r in cur.fetchall()]


@router.get("/subcategorias", response_model=List[SubcategoriaOut])
def list_subcategorias(categoria_id: str = Query(...)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, categoria_id, nombre FROM subcategorias WHERE categoria_id = %s ORDER BY nombre",
            (categoria_id,),
        )
        return [dict(r) for r in cur.fetchall()]


@router.get("/productos", response_model=List[ProductoOut])
def list_productos(subcategoria_id: str = Query(...)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, subcategoria_id, nombre FROM productos WHERE subcategoria_id = %s ORDER BY nombre",
            (subcategoria_id,),
        )
        return [dict(r) for r in cur.fetchall()]


@router.get("/unidades", response_model=List[UnidadOut])
def list_unidades(subcategoria_id: str = Query(...), tipo_precio: Optional[str] = Query(None)):
    with get_db() as conn:
        cur = conn.cursor()
        if tipo_precio and tipo_precio in ('MENUDEO', 'MAYOREO'):
            cur.execute(
                "SELECT id, subcategoria_id, nombre FROM unidades_subcategoria WHERE subcategoria_id = %s AND tipo = %s ORDER BY nombre",
                (subcategoria_id, tipo_precio),
            )
        else:
            cur.execute(
                "SELECT DISTINCT ON (subcategoria_id, nombre) id, subcategoria_id, nombre FROM unidades_subcategoria WHERE subcategoria_id = %s ORDER BY subcategoria_id, nombre",
                (subcategoria_id,),
            )
        return [dict(r) for r in cur.fetchall()]


# ── Catálogo de mercados (búsqueda) ──

@router.get("/catalogo", response_model=List[CatalogoMercadoOut])
def search_catalogo_mercados(
    entidad: Optional[str] = Query(None),
    municipio: Optional[str] = Query(None),
    nombre: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
):
    with get_db() as conn:
        cur = conn.cursor()
        conditions = []
        params: list = []

        if entidad:
            conditions.append("entidad = %s")
            params.append(entidad)
        if municipio:
            conditions.append("municipio = %s")
            params.append(municipio)
        if nombre:
            conditions.append("UPPER(nombre) LIKE %s")
            params.append(f"%{nombre.upper()}%")
        if tipo:
            conditions.append("tipo = %s")
            params.append(tipo)

        where = " AND ".join(conditions) if conditions else "TRUE"
        cur.execute(
            f"SELECT id, market_id, nombre, tipo, entidad, municipio, localidad, latitud, longitud, n_establecimientos, cve_ent, cve_mun FROM catalogo_mercados WHERE {where} ORDER BY entidad, municipio, nombre",
            params,
        )
        return [dict(r) for r in cur.fetchall()]


@router.get("/catalogo/entidades")
def list_catalogo_entidades():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT entidad FROM catalogo_mercados ORDER BY entidad")
        return [r["entidad"] for r in cur.fetchall()]


@router.get("/catalogo/municipios")
def list_catalogo_municipios(entidad: str = Query(...)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT DISTINCT municipio FROM catalogo_mercados WHERE entidad = %s ORDER BY municipio",
            (entidad,),
        )
        return [r["municipio"] for r in cur.fetchall()]


@router.get("/catalogo/todos", response_model=List[CatalogoMercadoOut])
def list_catalogo_todos():
    """Devuelve TODO el catálogo de mercados para cache offline."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, market_id, nombre, tipo, entidad, municipio, localidad, latitud, longitud, n_establecimientos, cve_ent, cve_mun FROM catalogo_mercados ORDER BY entidad, municipio, nombre"
        )
        return [dict(r) for r in cur.fetchall()]


@router.get("/catalogo/municipios-todos")
def list_catalogo_municipios_todos():
    """Devuelve todos los municipios agrupados por entidad para cache offline."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT entidad, municipio FROM catalogo_mercados ORDER BY entidad, municipio")
        result: dict = {}
        for r in cur.fetchall():
            result.setdefault(r["entidad"], []).append(r["municipio"])
        return result


@router.get("/catalogos-offline")
def get_catalogos_offline():
    """Devuelve TODOS los catálogos de productos para cache offline en una sola petición."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, descripcion FROM categorias ORDER BY nombre")
        categorias = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT id, categoria_id, nombre FROM subcategorias ORDER BY nombre")
        subcategorias = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT id, subcategoria_id, nombre FROM productos ORDER BY nombre")
        productos = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT id, subcategoria_id, nombre, tipo FROM unidades_subcategoria ORDER BY nombre")
        unidades = [dict(r) for r in cur.fetchall()]
        return {
            "categorias": categorias,
            "subcategorias": subcategorias,
            "productos": productos,
            "unidades": unidades,
        }


# ── Mercados del usuario (selección del catálogo) ──

@router.get("/", response_model=List[MercadoOut])
def list_mercados(user_id: str = Depends(get_current_user_id)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT m.id, cm.nombre, cm.tipo, cm.entidad, cm.municipio,
                      cm.localidad, cm.latitud, cm.longitud, cm.n_establecimientos,
                      m.created_at
               FROM mercados m
               JOIN catalogo_mercados cm ON cm.id = m.catalogo_mercado_id
               WHERE m.user_id = %s::uuid
               ORDER BY cm.nombre""",
            (user_id,),
        )
        rows = cur.fetchall()
    return [
        MercadoOut(
            id=r["id"], nombre=r["nombre"], tipo=r["tipo"],
            entidad=r["entidad"], municipio=r["municipio"],
            localidad=r["localidad"], latitud=r["latitud"], longitud=r["longitud"],
            n_establecimientos=r["n_establecimientos"],
            created_at=r["created_at"].isoformat(),
        ) for r in rows
    ]


@router.post("/", response_model=MercadoOut, status_code=201)
def add_mercado(data: MercadoCreate, user_id: str = Depends(get_current_user_id)):
    with get_db() as conn:
        cur = conn.cursor()
        # Verificar que el mercado del catálogo existe
        cur.execute(
            "SELECT id, nombre, tipo, entidad, municipio, localidad, latitud, longitud, n_establecimientos FROM catalogo_mercados WHERE id = %s",
            (data.catalogo_mercado_id,),
        )
        cm = cur.fetchone()
        if not cm:
            raise HTTPException(404, "Mercado no encontrado en el catálogo")

        # Verificar que no lo tenga ya
        cur.execute(
            "SELECT id FROM mercados WHERE user_id = %s::uuid AND catalogo_mercado_id = %s",
            (user_id, data.catalogo_mercado_id),
        )
        if cur.fetchone():
            raise HTTPException(409, "Ya tienes este mercado agregado")

        cur.execute(
            """INSERT INTO mercados (nombre, user_id, catalogo_mercado_id, latitud, longitud)
               VALUES (%s, %s::uuid, %s, %s, %s)
               RETURNING id, created_at""",
            (cm["nombre"], user_id, data.catalogo_mercado_id, cm["latitud"], cm["longitud"]),
        )
        r = cur.fetchone()
    return MercadoOut(
        id=r["id"], nombre=cm["nombre"], tipo=cm["tipo"],
        entidad=cm["entidad"], municipio=cm["municipio"],
        localidad=cm["localidad"], latitud=cm["latitud"], longitud=cm["longitud"],
        n_establecimientos=cm["n_establecimientos"],
        created_at=r["created_at"].isoformat(),
    )


@router.delete("/{mercado_id}", status_code=204)
def delete_mercado(mercado_id: int, user_id: str = Depends(get_current_user_id)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM mercados WHERE id = %s AND user_id = %s::uuid",
            (mercado_id, user_id),
        )
        if cur.rowcount == 0:
            raise HTTPException(404, "Mercado no encontrado")


# ── Reportes de precios ──

@router.post("/reportes", response_model=ReporteOut, status_code=201)
def create_reporte(data: ReporteCreate, user_id: str = Depends(get_current_user_id)):
    if not data.items:
        raise HTTPException(400, "Debe agregar al menos un producto")
    if data.tipo_precio not in ("MENUDEO", "MAYOREO"):
        raise HTTPException(400, "Tipo de precio inválido")

    seen = set()
    for item in data.items:
        if item.precio <= 0:
            raise HTTPException(400, "El precio debe ser mayor a 0")
        if item.precio != round(item.precio, 2):
            raise HTTPException(400, "El precio debe tener máximo 2 decimales")
        key = (item.producto_id, item.unidad)
        if key in seen:
            raise HTTPException(400, "Producto duplicado con la misma unidad")
        seen.add(key)

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM mercados WHERE id = %s AND user_id = %s::uuid",
            (data.mercado_id, user_id),
        )
        if not cur.fetchone():
            raise HTTPException(404, "Mercado no encontrado")

        cur.execute(
            """INSERT INTO reportes_precios (user_id, mercado_id, tipo_precio)
               VALUES (%s::uuid, %s, %s)
               RETURNING id, fecha, created_at""",
            (user_id, data.mercado_id, data.tipo_precio),
        )
        reporte = cur.fetchone()

        for item in data.items:
            cur.execute(
                """INSERT INTO detalle_precios (reporte_id, producto_id, precio, unidad)
                   VALUES (%s, %s, %s, %s)""",
                (reporte["id"], item.producto_id, item.precio, item.unidad),
            )

    return ReporteOut(
        id=reporte["id"],
        mercado_id=data.mercado_id,
        tipo_precio=data.tipo_precio,
        fecha=reporte["fecha"].isoformat(),
        created_at=reporte["created_at"].isoformat(),
        total_productos=len(data.items),
    )


@router.get("/reportes", response_model=List[ReporteOut])
def list_reportes(user_id: str = Depends(get_current_user_id), mercado_id: Optional[int] = None):
    with get_db() as conn:
        cur = conn.cursor()
        if mercado_id:
            cur.execute(
                """SELECT r.id, r.mercado_id, r.tipo_precio, r.fecha, r.created_at,
                       COUNT(d.id) as total_productos
                   FROM reportes_precios r
                   LEFT JOIN detalle_precios d ON d.reporte_id = r.id
                   WHERE r.user_id = %s::uuid AND r.mercado_id = %s
                   GROUP BY r.id ORDER BY r.created_at DESC""",
                (user_id, mercado_id),
            )
        else:
            cur.execute(
                """SELECT r.id, r.mercado_id, r.tipo_precio, r.fecha, r.created_at,
                       COUNT(d.id) as total_productos
                   FROM reportes_precios r
                   LEFT JOIN detalle_precios d ON d.reporte_id = r.id
                   WHERE r.user_id = %s::uuid
                   GROUP BY r.id ORDER BY r.created_at DESC""",
                (user_id,),
            )
        rows = cur.fetchall()
    return [
        ReporteOut(
            id=r["id"],
            mercado_id=r["mercado_id"],
            tipo_precio=r["tipo_precio"],
            fecha=r["fecha"].isoformat(),
            created_at=r["created_at"].isoformat(),
            total_productos=r["total_productos"],
        )
        for r in rows
    ]


@router.get("/reportes/{reporte_id}", response_model=ReporteDetalleOut)
def get_reporte(reporte_id: int, user_id: str = Depends(get_current_user_id)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT r.id, r.mercado_id, r.tipo_precio, r.fecha, r.created_at,
                   m.nombre as mercado_nombre
               FROM reportes_precios r
               JOIN mercados m ON m.id = r.mercado_id
               WHERE r.id = %s AND r.user_id = %s::uuid""",
            (reporte_id, user_id),
        )
        reporte = cur.fetchone()
        if not reporte:
            raise HTTPException(404, "Reporte no encontrado")

        cur.execute(
            """SELECT d.id, d.producto_id, p.nombre as producto_nombre,
                   d.precio, d.unidad, p.subcategoria_id
               FROM detalle_precios d
               JOIN productos p ON p.id = d.producto_id
               WHERE d.reporte_id = %s
               ORDER BY p.nombre""",
            (reporte_id,),
        )
        items = cur.fetchall()

    return ReporteDetalleOut(
        id=reporte["id"],
        mercado_id=reporte["mercado_id"],
        mercado_nombre=reporte["mercado_nombre"],
        tipo_precio=reporte["tipo_precio"],
        fecha=reporte["fecha"].isoformat(),
        created_at=reporte["created_at"].isoformat(),
        items=[
            DetalleItemOut(
                id=i["id"],
                producto_id=i["producto_id"],
                producto_nombre=i["producto_nombre"],
                precio=float(i["precio"]),
                unidad=i["unidad"],
                subcategoria_id=i["subcategoria_id"],
            )
            for i in items
        ],
    )


# ── Precio individual (producto por producto) ──

@router.post("/precio", response_model=PrecioHistorialItem, status_code=201)
def create_precio_individual(data: PrecioIndividualCreate, user_id: str = Depends(get_current_user_id)):
    if data.tipo_precio not in ("MENUDEO", "MAYOREO"):
        raise HTTPException(400, "Tipo de precio inválido")
    if data.precio <= 0:
        raise HTTPException(400, "El precio debe ser mayor a 0")
    if data.precio != round(data.precio, 2):
        raise HTTPException(400, "El precio debe tener máximo 2 decimales")

    with get_db() as conn:
        cur = conn.cursor()
        # Verificar mercado pertenece al usuario
        cur.execute(
            "SELECT id FROM mercados WHERE id = %s AND user_id = %s::uuid",
            (data.mercado_id, user_id),
        )
        if not cur.fetchone():
            raise HTTPException(404, "Mercado no encontrado")

        # Verificar producto existe
        cur.execute(
            "SELECT id, subcategoria_id, nombre FROM productos WHERE id = %s",
            (data.producto_id,),
        )
        prod = cur.fetchone()
        if not prod:
            raise HTTPException(404, "Producto no encontrado")

        # Deduplicación: si ya existe el mismo precio hoy, retornar el existente
        cur.execute(
            """SELECT dp.id AS detalle_id, rp.fecha, rp.created_at
               FROM reportes_precios rp
               JOIN detalle_precios dp ON dp.reporte_id = rp.id
               WHERE rp.user_id = %s::uuid
                 AND rp.mercado_id = %s
                 AND rp.tipo_precio = %s
                 AND dp.producto_id = %s
                 AND dp.precio = %s
                 AND dp.unidad = %s
                 AND rp.fecha = CURRENT_DATE""",
            (user_id, data.mercado_id, data.tipo_precio,
             data.producto_id, data.precio, data.unidad),
        )
        existing = cur.fetchone()

        if existing:
            cur.execute(
                "SELECT nombre, categoria_id FROM subcategorias WHERE id = %s",
                (prod["subcategoria_id"],),
            )
            sub = cur.fetchone()
            return PrecioHistorialItem(
                id=existing["detalle_id"],
                producto_id=data.producto_id,
                producto_nombre=prod["nombre"],
                subcategoria_nombre=sub["nombre"] if sub else "",
                categoria_id=sub["categoria_id"] if sub else "",
                precio=data.precio,
                unidad=data.unidad,
                tipo_precio=data.tipo_precio,
                fecha=existing["fecha"].isoformat(),
                created_at=existing["created_at"].isoformat(),
            )

        # Crear reporte de 1 item
        cur.execute(
            """INSERT INTO reportes_precios (user_id, mercado_id, tipo_precio)
               VALUES (%s::uuid, %s, %s)
               RETURNING id, fecha, created_at""",
            (user_id, data.mercado_id, data.tipo_precio),
        )
        reporte = cur.fetchone()

        cur.execute(
            """INSERT INTO detalle_precios (reporte_id, producto_id, precio, unidad)
               VALUES (%s, %s, %s, %s)
               RETURNING id""",
            (reporte["id"], data.producto_id, data.precio, data.unidad),
        )
        detalle = cur.fetchone()

        # Obtener nombre de subcategoría
        cur.execute(
            "SELECT nombre, categoria_id FROM subcategorias WHERE id = %s",
            (prod["subcategoria_id"],),
        )
        sub = cur.fetchone()

    return PrecioHistorialItem(
        id=detalle["id"],
        producto_id=data.producto_id,
        producto_nombre=prod["nombre"],
        subcategoria_nombre=sub["nombre"] if sub else "",
        categoria_id=sub["categoria_id"] if sub else "",
        precio=data.precio,
        unidad=data.unidad,
        tipo_precio=data.tipo_precio,
        fecha=reporte["fecha"].isoformat(),
        created_at=reporte["created_at"].isoformat(),
    )


@router.get("/precios-historial", response_model=List[PrecioHistorialItem])
def list_precios_historial(mercado_id: int = Query(...), user_id: str = Depends(get_current_user_id)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT d.id, d.producto_id, p.nombre as producto_nombre,
                   s.nombre as subcategoria_nombre, s.categoria_id,
                   d.precio, d.unidad, r.tipo_precio, r.fecha, r.created_at
               FROM detalle_precios d
               JOIN reportes_precios r ON r.id = d.reporte_id
               JOIN productos p ON p.id = d.producto_id
               JOIN subcategorias s ON s.id = p.subcategoria_id
               WHERE r.mercado_id = %s AND r.user_id = %s::uuid
               ORDER BY r.created_at DESC""",
            (mercado_id, user_id),
        )
        rows = cur.fetchall()
    return [
        PrecioHistorialItem(
            id=r["id"],
            producto_id=r["producto_id"],
            producto_nombre=r["producto_nombre"],
            subcategoria_nombre=r["subcategoria_nombre"],
            categoria_id=r["categoria_id"],
            precio=float(r["precio"]),
            unidad=r["unidad"],
            tipo_precio=r["tipo_precio"],
            fecha=r["fecha"].isoformat(),
            created_at=r["created_at"].isoformat(),
        )
        for r in rows
    ]


# ── Mercados recientes ──

@router.get("/recientes", response_model=List[MercadoOut])
def list_mercados_recientes(user_id: str = Depends(get_current_user_id)):
    """Returns all markets where user has captured prices, sorted by most recently used."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT m.id, cm.nombre, cm.tipo, cm.entidad, cm.municipio,
                      cm.localidad, cm.latitud, cm.longitud, cm.n_establecimientos,
                      m.created_at, MAX(r.created_at) AS last_used
               FROM mercados m
               JOIN catalogo_mercados cm ON cm.id = m.catalogo_mercado_id
               JOIN reportes_precios r ON r.mercado_id = m.id
               WHERE m.user_id = %s::uuid
               GROUP BY m.id, cm.nombre, cm.tipo, cm.entidad, cm.municipio,
                        cm.localidad, cm.latitud, cm.longitud, cm.n_establecimientos,
                        m.created_at
               ORDER BY last_used DESC""",
            (user_id,),
        )
        rows = cur.fetchall()
    return [
        MercadoOut(
            id=r["id"], nombre=r["nombre"], tipo=r["tipo"],
            entidad=r["entidad"], municipio=r["municipio"],
            localidad=r["localidad"], latitud=r["latitud"], longitud=r["longitud"],
            n_establecimientos=r["n_establecimientos"],
            created_at=r["created_at"].isoformat(),
        ) for r in rows
    ]


# ── Historial general ──

@router.get("/historial-general", response_model=List[HistorialGeneralItem])
def list_historial_general(
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id),
):
    with get_db() as conn:
        cur = conn.cursor()
        query = """SELECT d.id, r.mercado_id, cm.nombre as mercado_nombre,
                          cm.entidad as mercado_entidad, cm.municipio as mercado_municipio,
                          d.producto_id, p.nombre as producto_nombre,
                          s.nombre as subcategoria_nombre, s.categoria_id,
                          d.precio, d.unidad, r.tipo_precio, r.fecha, r.created_at
                   FROM detalle_precios d
                   JOIN reportes_precios r ON r.id = d.reporte_id
                   JOIN productos p ON p.id = d.producto_id
                   JOIN subcategorias s ON s.id = p.subcategoria_id
                   JOIN mercados m ON m.id = r.mercado_id
                   JOIN catalogo_mercados cm ON cm.id = m.catalogo_mercado_id
                   WHERE r.user_id = %s::uuid"""
        params: list = [user_id]
        if fecha_desde:
            query += " AND r.fecha >= %s"
            params.append(fecha_desde)
        if fecha_hasta:
            query += " AND r.fecha <= %s"
            params.append(fecha_hasta)
        query += " ORDER BY r.created_at DESC"
        cur.execute(query, params)
        rows = cur.fetchall()
    return [
        HistorialGeneralItem(
            id=r["id"],
            mercado_id=r["mercado_id"],
            mercado_nombre=r["mercado_nombre"],
            mercado_entidad=r["mercado_entidad"],
            mercado_municipio=r["mercado_municipio"],
            producto_id=r["producto_id"],
            producto_nombre=r["producto_nombre"],
            subcategoria_nombre=r["subcategoria_nombre"],
            categoria_id=r["categoria_id"],
            precio=float(r["precio"]),
            unidad=r["unidad"],
            tipo_precio=r["tipo_precio"],
            fecha=r["fecha"].isoformat(),
            created_at=r["created_at"].isoformat(),
        )
        for r in rows
    ]


# ── Mercados propuestos ──

@router.post("/proponer", response_model=MercadoPropuestoOut, status_code=201)
def proponer_mercado(data: MercadoPropuestoCreate, user_id: str = Depends(get_current_user_id)):
    # Validaciones
    if len(data.nombre_mercado.strip()) < 4:
        raise HTTPException(400, "El nombre debe tener al menos 4 caracteres")
    if data.tipo_mercado not in ("MERCADO_PUBLICO", "TIANGUIS", "CENTRAL_ABASTO", "OTRO"):
        raise HTTPException(400, "Tipo de mercado inválido")
    if not (-90 <= data.latitud <= 90) or not (-180 <= data.longitud <= 180):
        raise HTTPException(400, "Coordenadas fuera de rango")
    if data.latitud == 0 and data.longitud == 0:
        raise HTTPException(400, "Coordenadas inválidas (0,0)")
    if not data.dias_operacion or len(data.dias_operacion) == 0:
        raise HTTPException(400, "Selecciona al menos un día de operación")

    with get_db() as conn:
        cur = conn.cursor()

        # Deduplicación: si ya existe propuesta igual del mismo usuario, retornar existente
        cur.execute(
            """SELECT id, status, created_at FROM mercados_propuestos
               WHERE created_by = %s::uuid
                 AND nombre_mercado = %s
                 AND estado = %s
                 AND municipio = %s
                 AND ABS(latitud - %s) < 0.001
                 AND ABS(longitud - %s) < 0.001
               ORDER BY created_at DESC LIMIT 1""",
            (user_id, data.nombre_mercado.strip(), data.estado,
             data.municipio, data.latitud, data.longitud),
        )
        existing = cur.fetchone()
        if existing:
            return MercadoPropuestoOut(
                id=existing["id"],
                nombre_mercado=data.nombre_mercado.strip(),
                tipo_mercado=data.tipo_mercado,
                tipo_mercado_otro=data.tipo_mercado_otro,
                estado=data.estado,
                municipio=data.municipio,
                localidad_colonia=data.localidad_colonia,
                latitud=data.latitud,
                longitud=data.longitud,
                dias_operacion=data.dias_operacion,
                horario=data.horario,
                referencia=data.referencia,
                observaciones=data.observaciones,
                status=existing["status"],
                created_at=existing["created_at"].isoformat(),
            )

        # Obtener datos del perfil del usuario
        cur.execute(
            "SELECT tipo_capturista, cac_id, cac_nombre, territorio, ruta FROM users WHERE id = %s::uuid",
            (user_id,),
        )
        user = cur.fetchone()

        cur.execute(
            """INSERT INTO mercados_propuestos
                   (nombre_mercado, tipo_mercado, tipo_mercado_otro, estado, municipio,
                    localidad_colonia, latitud, longitud, dias_operacion, horario,
                    referencia, observaciones, created_by,
                    tipo_capturista, cac_id, cac_nombre, territorio, ruta)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::uuid,
                       %s, %s, %s, %s, %s)
               RETURNING id, status, created_at""",
            (
                data.nombre_mercado.strip(), data.tipo_mercado, data.tipo_mercado_otro,
                data.estado, data.municipio, data.localidad_colonia,
                data.latitud, data.longitud, data.dias_operacion,
                data.horario, data.referencia, data.observaciones, user_id,
                user["tipo_capturista"] if user else None,
                user["cac_id"] if user else None,
                user["cac_nombre"] if user else None,
                user["territorio"] if user else None,
                user["ruta"] if user else None,
            ),
        )
        r = cur.fetchone()

    return MercadoPropuestoOut(
        id=r["id"],
        nombre_mercado=data.nombre_mercado.strip(),
        tipo_mercado=data.tipo_mercado,
        tipo_mercado_otro=data.tipo_mercado_otro,
        estado=data.estado,
        municipio=data.municipio,
        localidad_colonia=data.localidad_colonia,
        latitud=data.latitud,
        longitud=data.longitud,
        dias_operacion=data.dias_operacion,
        horario=data.horario,
        referencia=data.referencia,
        observaciones=data.observaciones,
        status=r["status"],
        created_at=r["created_at"].isoformat(),
    )


@router.get("/propuestos", response_model=List[MercadoPropuestoOut])
def list_mercados_propuestos(user_id: str = Depends(get_current_user_id)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, nombre_mercado, tipo_mercado, tipo_mercado_otro,
                      estado, municipio, localidad_colonia, latitud, longitud,
                      dias_operacion, horario, referencia, observaciones,
                      status, created_at
               FROM mercados_propuestos
               WHERE created_by = %s::uuid
               ORDER BY created_at DESC""",
            (user_id,),
        )
        rows = cur.fetchall()
    return [
        MercadoPropuestoOut(
            id=r["id"],
            nombre_mercado=r["nombre_mercado"],
            tipo_mercado=r["tipo_mercado"],
            tipo_mercado_otro=r["tipo_mercado_otro"],
            estado=r["estado"],
            municipio=r["municipio"],
            localidad_colonia=r["localidad_colonia"],
            latitud=r["latitud"],
            longitud=r["longitud"],
            dias_operacion=r["dias_operacion"],
            horario=r["horario"],
            referencia=r["referencia"],
            observaciones=r["observaciones"],
            status=r["status"],
            created_at=r["created_at"].isoformat(),
        )
        for r in rows
    ]
