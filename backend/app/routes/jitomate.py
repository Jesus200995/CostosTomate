from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timezone, time
from app.schemas import (
    ReporteJitomateCreate, ReporteJitomateOut, ReporteJitomateDetalleOut,
    HistorialJitomateItem
)
from app.database import get_db
from app.auth import get_current_user_id

router = APIRouter()

# Horario de corte: matutino hasta 11:00, mediodía a partir de 11:00
HORA_LIMITE_MATUTINO = time(11, 0)
HORA_LIMITE_MEDIODIA = time(17, 0)


def _es_captura_tardia(corte: str, hora_captura: datetime) -> bool:
    h = hora_captura.time()
    if corte == "matutino":
        return h > HORA_LIMITE_MATUTINO
    if corte == "mediodia":
        return h > HORA_LIMITE_MEDIODIA
    return False


@router.post("/reportes", response_model=ReporteJitomateOut, status_code=201)
def create_reporte_jitomate(data: ReporteJitomateCreate, user_id: str = Depends(get_current_user_id)):
    # Validaciones
    if data.corte not in ("matutino", "mediodia"):
        raise HTTPException(400, "Corte inválido: debe ser 'matutino' o 'mediodia'")

    DISPONIBILIDADES_VALIDAS = {"alta", "media", "baja", "no_hay"}
    precios_validos = 0
    for precio_item in data.precios:
        if precio_item.calidad not in ("primera", "segunda", "tercera"):
            raise HTTPException(400, f"Calidad inválida: {precio_item.calidad}")

        # Normalizar disponibilidad: si no viene, inferir de sin_dato
        if precio_item.disponibilidad is None:
            precio_item.disponibilidad = "no_hay" if precio_item.sin_dato else "alta"
        elif precio_item.disponibilidad not in DISPONIBILIDADES_VALIDAS:
            raise HTTPException(400, f"Disponibilidad inválida: {precio_item.disponibilidad}")

        es_no_hay = precio_item.disponibilidad == "no_hay"
        # Si no_hay, forzar sin_dato y precio NULL
        if es_no_hay:
            precio_item.sin_dato = True
            precio_item.precio = None
        else:
            precio_item.sin_dato = False
            if precio_item.precio is None or precio_item.precio < 0:
                raise HTTPException(400, f"Precio inválido para calidad {precio_item.calidad} con disponibilidad {precio_item.disponibilidad}")
            precios_validos += 1

    if len(data.precios) != 3:
        raise HTTPException(400, "Debe ingresar exactamente 3 calidades (primera, segunda, tercera)")

    calidades_ingresadas = {p.calidad for p in data.precios}
    if calidades_ingresadas != {"primera", "segunda", "tercera"}:
        raise HTTPException(400, "Debe ingresar primera, segunda y tercera calidad")

    hora_captura = datetime.now(timezone.utc)
    tardia = _es_captura_tardia(data.corte, hora_captura)

    with get_db() as conn:
        cur = conn.cursor()

        # Verificar central autorizada y visible
        cur.execute(
            "SELECT id, nombre_central FROM catalogo_centrales WHERE id = %s AND estatus = 'autorizado' AND visible_pwa = TRUE",
            (data.central_id,),
        )
        central = cur.fetchone()
        if not central:
            raise HTTPException(404, "Central no autorizada o no visible")

        # Verificar que no existe reporte duplicado
        cur.execute(
            "SELECT id FROM reportes_jitomate WHERE central_id = %s AND fecha = %s AND corte = %s",
            (data.central_id, data.fecha, data.corte),
        )
        if cur.fetchone():
            raise HTTPException(409, f"Ya existe un reporte para esta central en fecha {data.fecha} corte {data.corte}")

        # Crear reporte cabecera
        cur.execute(
            """INSERT INTO reportes_jitomate
                   (central_id, usuario_id, fecha, corte, hora_captura, captura_tardia, observaciones)
               VALUES (%s, %s::uuid, %s, %s, %s, %s, %s)
               RETURNING id, fecha, corte, hora_captura, captura_tardia, created_at""",
            (data.central_id, user_id, data.fecha, data.corte,
             hora_captura, tardia, data.observaciones),
        )
        reporte = cur.fetchone()
        reporte_id = reporte["id"]

        # Insertar precios de las 3 calidades
        for precio_item in data.precios:
            precio_val = None if precio_item.sin_dato else precio_item.precio
            cur.execute(
                """INSERT INTO precios_jitomate_calidad
                       (reporte_jitomate_id, calidad, precio, sin_dato, disponibilidad)
                   VALUES (%s, %s, %s, %s, %s)""",
                (reporte_id, precio_item.calidad, precio_val, precio_item.sin_dato, precio_item.disponibilidad),
            )

    return ReporteJitomateOut(
        id=reporte_id,
        central_id=data.central_id,
        central_nombre=central["nombre_central"],
        usuario_id=user_id,
        fecha=reporte["fecha"],
        corte=reporte["corte"],
        hora_captura=reporte["hora_captura"],
        captura_tardia=reporte["captura_tardia"],
        created_at=reporte["created_at"],
    )


@router.get("/reportes", response_model=List[ReporteJitomateOut])
def list_reportes_jitomate(
    central_id: Optional[int] = Query(None),
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id),
):
    with get_db() as conn:
        cur = conn.cursor()
        query = """SELECT r.id, r.central_id, c.nombre_central, r.usuario_id,
                          r.fecha, r.corte, r.hora_captura, r.captura_tardia, r.created_at
                   FROM reportes_jitomate r
                   JOIN catalogo_centrales c ON c.id = r.central_id
                   WHERE r.usuario_id = %s::uuid"""
        params: list = [user_id]

        if central_id:
            query += " AND r.central_id = %s"
            params.append(central_id)
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
        ReporteJitomateOut(
            id=r["id"],
            central_id=r["central_id"],
            central_nombre=r["nombre_central"],
            usuario_id=str(r["usuario_id"]),
            fecha=r["fecha"],
            corte=r["corte"],
            hora_captura=r["hora_captura"],
            captura_tardia=r["captura_tardia"],
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.get("/reportes/{reporte_id}", response_model=ReporteJitomateDetalleOut)
def get_reporte_jitomate(reporte_id: int, user_id: str = Depends(get_current_user_id)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT r.id, r.central_id, c.nombre_central, c.estado, c.municipio,
                      r.usuario_id, r.fecha, r.corte, r.hora_captura,
                      r.captura_tardia, r.observaciones, r.created_at
               FROM reportes_jitomate r
               JOIN catalogo_centrales c ON c.id = r.central_id
               WHERE r.id = %s AND r.usuario_id = %s::uuid""",
            (reporte_id, user_id),
        )
        reporte = cur.fetchone()
        if not reporte:
            raise HTTPException(404, "Reporte no encontrado")

        cur.execute(
            "SELECT calidad, precio, sin_dato, disponibilidad FROM precios_jitomate_calidad WHERE reporte_jitomate_id = %s ORDER BY calidad",
            (reporte_id,),
        )
        precios = cur.fetchall()

    return ReporteJitomateDetalleOut(
        id=reporte["id"],
        central_id=reporte["central_id"],
        central_nombre=reporte["nombre_central"],
        central_estado=reporte["estado"],
        central_municipio=reporte["municipio"],
        usuario_id=str(reporte["usuario_id"]),
        fecha=reporte["fecha"],
        corte=reporte["corte"],
        hora_captura=reporte["hora_captura"],
        captura_tardia=reporte["captura_tardia"],
        observaciones=reporte["observaciones"],
        created_at=reporte["created_at"],
        precios=[
            {
                "calidad": p["calidad"],
                "precio": float(p["precio"]) if p["precio"] else None,
                "sin_dato": p["sin_dato"],
                "disponibilidad": p["disponibilidad"],
            }
            for p in precios
        ],
    )


@router.get("/historial", response_model=List[HistorialJitomateItem])
def historial_jitomate(
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    central_id: Optional[int] = Query(None),
    corte: Optional[str] = Query(None),
    todos: bool = Query(False),
    user_id: str = Depends(get_current_user_id),
):
    with get_db() as conn:
        cur = conn.cursor()
        base = """SELECT r.id, r.central_id, c.nombre_central, c.estado, c.municipio,
                         r.fecha, r.corte, r.captura_tardia, r.created_at,
                         p.calidad, p.precio, p.sin_dato, p.disponibilidad,
                         u.name AS capturista_nombre
                  FROM reportes_jitomate r
                  JOIN catalogo_centrales c ON c.id = r.central_id
                  JOIN precios_jitomate_calidad p ON p.reporte_jitomate_id = r.id
                  JOIN users u ON u.id = r.usuario_id"""
        if todos:
            query = base + " WHERE 1=1"
            params: list = []
        else:
            query = base + " WHERE r.usuario_id = %s::uuid"
            params = [user_id]

        if central_id:
            query += " AND r.central_id = %s"
            params.append(central_id)
        if fecha_desde:
            query += " AND r.fecha >= %s"
            params.append(fecha_desde)
        if fecha_hasta:
            query += " AND r.fecha <= %s"
            params.append(fecha_hasta)
        if corte and corte in ("matutino", "mediodia"):
            query += " AND r.corte = %s"
            params.append(corte)

        query += " ORDER BY r.fecha DESC, r.corte, p.calidad"
        cur.execute(query, params)
        rows = cur.fetchall()

    return [
        HistorialJitomateItem(
            id=r["id"],
            central_id=r["central_id"],
            central_nombre=r["nombre_central"],
            central_estado=r["estado"],
            central_municipio=r["municipio"],
            fecha=r["fecha"],
            corte=r["corte"],
            calidad=r["calidad"],
            precio=float(r["precio"]) if r["precio"] else None,
            sin_dato=r["sin_dato"],
            disponibilidad=r["disponibilidad"],
            captura_tardia=r["captura_tardia"],
            created_at=r["created_at"],
            capturista_nombre=r["capturista_nombre"],
        )
        for r in rows
    ]
