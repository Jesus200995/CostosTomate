"""
Admin Jitomate — Endpoints para el panel administrativo de monitoreo de jitomate.
Centrales CRUD, reportes, dashboard, mapa y alertas.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.database import get_db
from app.routes.admin_auth import require_admin

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════
# CENTRALES — Catálogo completo (admin)
# ═══════════════════════════════════════════════════════════════════

@router.get("/centrales")
def admin_list_centrales(token: str):
    """Lista todas las centrales (incluye inactivas) para gestión admin."""
    require_admin(token)
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nombre_central, tipo, municipio, estado,
                   latitud, longitud, estatus, visible_pwa, created_at, updated_at
            FROM catalogo_centrales
            ORDER BY estado, municipio, nombre_central
        """)
        return [dict(r) for r in cur.fetchall()]


@router.patch("/centrales/{central_id}")
def admin_update_central(central_id: int, token: str, estatus: Optional[str] = None,
                         visible_pwa: Optional[bool] = None,
                         latitud: Optional[float] = None, longitud: Optional[float] = None,
                         nombre_central: Optional[str] = None, tipo: Optional[str] = None,
                         municipio: Optional[str] = None, estado: Optional[str] = None):
    """Editar central: estatus, visible_pwa, coordenadas, nombre, tipo."""
    require_admin(token)

    updates = []
    values = []
    if estatus is not None:
        if estatus not in ('autorizado', 'pendiente', 'inactivo'):
            raise HTTPException(400, "Estatus inválido")
        updates.append("estatus = %s")
        values.append(estatus)
    if visible_pwa is not None:
        updates.append("visible_pwa = %s")
        values.append(visible_pwa)
    if latitud is not None:
        updates.append("latitud = %s")
        values.append(latitud)
    if longitud is not None:
        updates.append("longitud = %s")
        values.append(longitud)
    if nombre_central is not None:
        updates.append("nombre_central = %s")
        values.append(nombre_central)
    if tipo is not None:
        updates.append("tipo = %s")
        values.append(tipo)
    if municipio is not None:
        updates.append("municipio = %s")
        values.append(municipio)
    if estado is not None:
        updates.append("estado = %s")
        values.append(estado)

    if not updates:
        raise HTTPException(400, "Nada que actualizar")

    updates.append("updated_at = CURRENT_TIMESTAMP")
    values.append(central_id)

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""UPDATE catalogo_centrales SET {', '.join(updates)}
                WHERE id = %s
                RETURNING id, nombre_central, tipo, municipio, estado,
                          latitud, longitud, estatus, visible_pwa, created_at, updated_at""",
            values
        )
        row = cur.fetchone()
    if not row:
        raise HTTPException(404, "Central no encontrada")
    return dict(row)


# ═══════════════════════════════════════════════════════════════════
# PROPUESTAS DE CENTRALES
# ═══════════════════════════════════════════════════════════════════

@router.get("/propuestas-centrales")
def admin_list_propuestas(token: str, estatus: Optional[str] = None):
    """Lista propuestas de centrales."""
    require_admin(token)
    with get_db() as conn:
        cur = conn.cursor()
        q = """SELECT pc.*, u.name AS usuario_nombre, u.email AS usuario_email
               FROM propuestas_centrales pc
               LEFT JOIN users u ON u.id = pc.usuario_id"""
        params = []
        if estatus:
            q += " WHERE pc.estatus = %s"
            params.append(estatus)
        q += " ORDER BY pc.created_at DESC"
        cur.execute(q, params)
        return [dict(r) for r in cur.fetchall()]


@router.patch("/propuestas-centrales/{prop_id}/autorizar")
def admin_autorizar_propuesta(prop_id: int, token: str):
    """Aprobar propuesta → insertar en catalogo_centrales."""
    require_admin(token)
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM propuestas_centrales WHERE id = %s", (prop_id,))
        prop = cur.fetchone()
        if not prop:
            raise HTTPException(404, "Propuesta no encontrada")
        if prop["estatus"] != "pendiente":
            raise HTTPException(400, f"Propuesta ya fue {prop['estatus']}")

        cur.execute(
            """INSERT INTO catalogo_centrales (nombre_central, tipo, municipio, estado, latitud, longitud, estatus, visible_pwa)
               VALUES (%s, %s, %s, %s, %s, %s, 'autorizado', TRUE)
               RETURNING id""",
            (prop["nombre_central"], prop["tipo"], prop["municipio"], prop["estado"],
             prop["latitud"], prop["longitud"])
        )
        new_id = cur.fetchone()["id"]
        cur.execute(
            "UPDATE propuestas_centrales SET estatus = 'aprobada', updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (prop_id,)
        )
    return {"message": "Propuesta aprobada", "central_id": new_id}


@router.patch("/propuestas-centrales/{prop_id}/rechazar")
def admin_rechazar_propuesta(prop_id: int, token: str, motivo: Optional[str] = None):
    """Rechazar propuesta."""
    require_admin(token)
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT estatus FROM propuestas_centrales WHERE id = %s", (prop_id,))
        prop = cur.fetchone()
        if not prop:
            raise HTTPException(404, "Propuesta no encontrada")
        if prop["estatus"] != "pendiente":
            raise HTTPException(400, f"Propuesta ya fue {prop['estatus']}")
        cur.execute(
            "UPDATE propuestas_centrales SET estatus = 'rechazada', motivo_rechazo = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (motivo, prop_id)
        )
    return {"message": "Propuesta rechazada"}


# ═══════════════════════════════════════════════════════════════════
# REPORTES JITOMATE — Tabla filtrable
# ═══════════════════════════════════════════════════════════════════

@router.get("/reportes")
def admin_reportes_jitomate(
    token: str,
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    corte: Optional[str] = Query(None),
    central_id: Optional[int] = Query(None),
    estado: Optional[str] = Query(None),
    calidad: Optional[str] = Query(None),
    capturista: Optional[str] = Query(None),
):
    """Reportes de jitomate con precios por calidad — tabla admin."""
    require_admin(token)
    with get_db() as conn:
        cur = conn.cursor()
        where = []
        params: list = []
        if fecha_desde:
            where.append("rj.fecha >= %s"); params.append(fecha_desde)
        if fecha_hasta:
            where.append("rj.fecha <= %s"); params.append(fecha_hasta)
        if corte:
            where.append("rj.corte = %s"); params.append(corte)
        if central_id:
            where.append("rj.central_id = %s"); params.append(central_id)
        if estado:
            where.append("cc.estado = %s"); params.append(estado)
        if capturista:
            where.append("(LOWER(u.name) LIKE LOWER(%s) OR LOWER(u.email) LIKE LOWER(%s))")
            params.extend([f"%{capturista}%", f"%{capturista}%"])

        where_sql = (" AND " + " AND ".join(where)) if where else ""

        cur.execute(f"""
            SELECT rj.id, rj.fecha, rj.corte, rj.hora_captura, rj.captura_tardia,
                   rj.observaciones, rj.central_id,
                   cc.nombre_central, cc.estado, cc.municipio,
                   u.name AS capturista_nombre, u.email AS capturista_email,
                   pj1.precio AS precio_primera, pj1.sin_dato AS sin_dato_primera,
                   pj2.precio AS precio_segunda, pj2.sin_dato AS sin_dato_segunda,
                   pj3.precio AS precio_tercera, pj3.sin_dato AS sin_dato_tercera
            FROM reportes_jitomate rj
            JOIN catalogo_centrales cc ON cc.id = rj.central_id
            JOIN users u ON u.id = rj.usuario_id
            LEFT JOIN precios_jitomate_calidad pj1 ON pj1.reporte_jitomate_id = rj.id AND pj1.calidad = 'primera'
            LEFT JOIN precios_jitomate_calidad pj2 ON pj2.reporte_jitomate_id = rj.id AND pj2.calidad = 'segunda'
            LEFT JOIN precios_jitomate_calidad pj3 ON pj3.reporte_jitomate_id = rj.id AND pj3.calidad = 'tercera'
            WHERE 1=1{where_sql}
            ORDER BY rj.fecha DESC, rj.corte, cc.nombre_central
            LIMIT 500
        """, params)

        rows = []
        for r in cur.fetchall():
            d = dict(r)
            d["fecha"] = d["fecha"].isoformat() if d["fecha"] else None
            d["hora_captura"] = d["hora_captura"].isoformat() if d["hora_captura"] else None
            d["precio_primera"] = float(d["precio_primera"]) if d["precio_primera"] else None
            d["precio_segunda"] = float(d["precio_segunda"]) if d["precio_segunda"] else None
            d["precio_tercera"] = float(d["precio_tercera"]) if d["precio_tercera"] else None
            rows.append(d)
        return rows


# ═══════════════════════════════════════════════════════════════════
# DASHBOARD — KPIs y estadísticas
# ═══════════════════════════════════════════════════════════════════

@router.get("/dashboard")
def admin_dashboard(
    token: str,
    fecha: Optional[str] = Query(None),
    corte: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
):
    """Dashboard de jitomate: KPIs, promedios por calidad, cobertura, alertas."""
    require_admin(token)
    with get_db() as conn:
        cur = conn.cursor()

        where = []
        params: list = []
        if fecha:
            where.append("rj.fecha = %s"); params.append(fecha)
        if corte:
            where.append("rj.corte = %s"); params.append(corte)
        if estado:
            where.append("cc.estado = %s"); params.append(estado)
        where_sql = (" AND " + " AND ".join(where)) if where else ""

        # Promedios por calidad
        cur.execute(f"""
            SELECT pjc.calidad,
                   ROUND(AVG(pjc.precio)::numeric, 2) AS promedio,
                   ROUND(MIN(pjc.precio)::numeric, 2) AS minimo,
                   ROUND(MAX(pjc.precio)::numeric, 2) AS maximo,
                   COUNT(*) FILTER (WHERE pjc.sin_dato = FALSE AND pjc.precio IS NOT NULL) AS con_dato,
                   COUNT(*) FILTER (WHERE pjc.sin_dato = TRUE OR pjc.precio IS NULL) AS sin_dato
            FROM precios_jitomate_calidad pjc
            JOIN reportes_jitomate rj ON rj.id = pjc.reporte_jitomate_id
            JOIN catalogo_centrales cc ON cc.id = rj.central_id
            WHERE pjc.precio IS NOT NULL AND pjc.sin_dato = FALSE{where_sql}
            GROUP BY pjc.calidad
            ORDER BY pjc.calidad
        """, params)
        calidades = []
        for r in cur.fetchall():
            d = dict(r)
            d["promedio"] = float(d["promedio"]) if d["promedio"] else 0
            d["minimo"] = float(d["minimo"]) if d["minimo"] else 0
            d["maximo"] = float(d["maximo"]) if d["maximo"] else 0
            calidades.append(d)

        # Total centrales y con reporte
        cur.execute("SELECT COUNT(*) AS total FROM catalogo_centrales WHERE estatus = 'autorizado' AND visible_pwa = TRUE")
        total_centrales = cur.fetchone()["total"]

        cur.execute(f"""
            SELECT COUNT(DISTINCT rj.central_id) AS con_reporte
            FROM reportes_jitomate rj
            JOIN catalogo_centrales cc ON cc.id = rj.central_id
            WHERE 1=1{where_sql}
        """, params)
        con_reporte = cur.fetchone()["con_reporte"]

        # Total reportes
        cur.execute(f"""
            SELECT COUNT(*) AS total FROM reportes_jitomate rj
            JOIN catalogo_centrales cc ON cc.id = rj.central_id
            WHERE 1=1{where_sql}
        """, params)
        total_reportes = cur.fetchone()["total"]

        # Capturas tardías
        cur.execute(f"""
            SELECT COUNT(*) AS total FROM reportes_jitomate rj
            JOIN catalogo_centrales cc ON cc.id = rj.central_id
            WHERE rj.captura_tardia = TRUE{where_sql}
        """, params)
        tardias = cur.fetchone()["total"]

        # Alertas activas
        cur.execute("SELECT COUNT(*) AS total FROM alertas_jitomate WHERE estatus = 'activa'")
        alertas_activas = cur.fetchone()["total"]

        # Promedios por estado
        cur.execute(f"""
            SELECT cc.estado,
                   ROUND(AVG(pjc.precio)::numeric, 2) AS promedio,
                   COUNT(DISTINCT rj.central_id) AS centrales_con_reporte
            FROM precios_jitomate_calidad pjc
            JOIN reportes_jitomate rj ON rj.id = pjc.reporte_jitomate_id
            JOIN catalogo_centrales cc ON cc.id = rj.central_id
            WHERE pjc.precio IS NOT NULL AND pjc.sin_dato = FALSE{where_sql}
            GROUP BY cc.estado
            ORDER BY promedio DESC
        """, params)
        por_estado = []
        for r in cur.fetchall():
            d = dict(r)
            d["promedio"] = float(d["promedio"]) if d["promedio"] else 0
            por_estado.append(d)

    return {
        "calidades": calidades,
        "cobertura": {"total": total_centrales, "con_reporte": con_reporte},
        "total_reportes": total_reportes,
        "capturas_tardias": tardias,
        "alertas_activas": alertas_activas,
        "por_estado": por_estado,
    }


# ═══════════════════════════════════════════════════════════════════
# MAPA — Centrales con estado de reporte
# ═══════════════════════════════════════════════════════════════════

@router.get("/mapa")
def admin_mapa_centrales(
    token: str,
    fecha: Optional[str] = Query(None),
    corte: Optional[str] = Query(None),
):
    """Centrales para el mapa admin, con indicador de reporte del día."""
    require_admin(token)
    with get_db() as conn:
        cur = conn.cursor()

        fecha_sql = fecha or "CURRENT_DATE"
        params: list = []

        if fecha:
            date_filter = "AND rj.fecha = %s"
            params_rep = [fecha]
        else:
            date_filter = "AND rj.fecha = CURRENT_DATE"
            params_rep = []

        if corte:
            date_filter += " AND rj.corte = %s"
            params_rep.append(corte)

        # Todas las centrales autorizadas
        cur.execute("""
            SELECT id, nombre_central, tipo, municipio, estado,
                   latitud, longitud, estatus, visible_pwa
            FROM catalogo_centrales
            WHERE estatus = 'autorizado'
            ORDER BY estado, nombre_central
        """)
        centrales = [dict(r) for r in cur.fetchall()]

        # Reportes del día
        cur.execute(f"""
            SELECT rj.central_id, rj.corte, rj.captura_tardia,
                   rj.hora_captura,
                   pj1.precio AS primera, pj1.sin_dato AS sin_dato_primera,
                   pj2.precio AS segunda, pj2.sin_dato AS sin_dato_segunda,
                   pj3.precio AS tercera, pj3.sin_dato AS sin_dato_tercera
            FROM reportes_jitomate rj
            LEFT JOIN precios_jitomate_calidad pj1 ON pj1.reporte_jitomate_id = rj.id AND pj1.calidad = 'primera'
            LEFT JOIN precios_jitomate_calidad pj2 ON pj2.reporte_jitomate_id = rj.id AND pj2.calidad = 'segunda'
            LEFT JOIN precios_jitomate_calidad pj3 ON pj3.reporte_jitomate_id = rj.id AND pj3.calidad = 'tercera'
            WHERE 1=1 {date_filter}
        """, params_rep)

        reportes_map = {}
        for r in cur.fetchall():
            d = dict(r)
            d["primera"] = float(d["primera"]) if d["primera"] else None
            d["segunda"] = float(d["segunda"]) if d["segunda"] else None
            d["tercera"] = float(d["tercera"]) if d["tercera"] else None
            d["hora_captura"] = d["hora_captura"].isoformat() if d["hora_captura"] else None
            reportes_map[d["central_id"]] = d

        # Propuestas pendientes
        cur.execute("""
            SELECT id, nombre_central, tipo, municipio, estado,
                   latitud, longitud, estatus
            FROM propuestas_centrales WHERE estatus = 'pendiente'
        """)
        propuestas = [dict(r) for r in cur.fetchall()]

        # Alertas activas
        cur.execute("""
            SELECT central_id, tipo, descripcion, variacion_porcentaje
            FROM alertas_jitomate WHERE estatus = 'activa'
        """)
        alertas = {}
        for r in cur.fetchall():
            d = dict(r)
            d["variacion_porcentaje"] = float(d["variacion_porcentaje"]) if d["variacion_porcentaje"] else None
            alertas.setdefault(d["central_id"], []).append(d)

    # Enriquecer centrales
    for c in centrales:
        rep = reportes_map.get(c["id"])
        c["tiene_reporte"] = rep is not None
        c["reporte"] = rep
        c["alertas"] = alertas.get(c["id"], [])

    return {"centrales": centrales, "propuestas": propuestas}


# ═══════════════════════════════════════════════════════════════════
# ALERTAS
# ═══════════════════════════════════════════════════════════════════

@router.get("/alertas")
def admin_alertas(token: str, estatus: Optional[str] = Query("activa")):
    """Lista alertas de jitomate."""
    require_admin(token)
    with get_db() as conn:
        cur = conn.cursor()
        q = """SELECT a.*, cc.nombre_central, cc.estado, cc.municipio
               FROM alertas_jitomate a
               JOIN catalogo_centrales cc ON cc.id = a.central_id"""
        params = []
        if estatus:
            q += " WHERE a.estatus = %s"
            params.append(estatus)
        q += " ORDER BY a.created_at DESC LIMIT 200"
        cur.execute(q, params)
        rows = []
        for r in cur.fetchall():
            d = dict(r)
            d["fecha_alerta"] = d["fecha_alerta"].isoformat() if d["fecha_alerta"] else None
            d["precio_anterior"] = float(d["precio_anterior"]) if d["precio_anterior"] else None
            d["precio_actual"] = float(d["precio_actual"]) if d["precio_actual"] else None
            d["variacion_porcentaje"] = float(d["variacion_porcentaje"]) if d["variacion_porcentaje"] else None
            rows.append(d)
        return rows
