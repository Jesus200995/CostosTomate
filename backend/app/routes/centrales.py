from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.schemas import (
    CentralOut, CentralCreate, CaptoristasCentralOut,
    PropuestaCentralCreate, PropuestaCentralOut
)
from app.database import get_db
from app.auth import get_current_user_id

router = APIRouter()


# ── Estados y municipios disponibles en centrales ──

@router.get("/estados-disponibles")
def list_estados_disponibles(user_id: str = Depends(get_current_user_id)):
    """Devuelve estados distintos con centrales autorizadas y visibles en PWA."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT DISTINCT estado FROM catalogo_centrales
               WHERE estatus = 'autorizado' AND visible_pwa = TRUE AND estado IS NOT NULL
               ORDER BY estado"""
        )
        return [r["estado"] for r in cur.fetchall()]


@router.get("/municipios-disponibles")
def list_municipios_disponibles(estado: str, user_id: str = Depends(get_current_user_id)):
    """Devuelve municipios distintos para un estado dado con centrales autorizadas."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT DISTINCT municipio FROM catalogo_centrales
               WHERE estatus = 'autorizado' AND visible_pwa = TRUE
                 AND estado = %s AND municipio IS NOT NULL
               ORDER BY municipio""",
            (estado,),
        )
        return [r["municipio"] for r in cur.fetchall()]


# ── Catálogo de centrales (público/auth) ──

@router.get("/", response_model=List[CentralOut])
def list_centrales(
    estado: Optional[str] = Query(None),
    municipio: Optional[str] = Query(None),
    nombre: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id),
):
    with get_db() as conn:
        cur = conn.cursor()
        conditions = ["estatus = 'autorizado'", "visible_pwa = TRUE"]
        params: list = []
        if estado:
            conditions.append("estado = %s")
            params.append(estado)
        if municipio:
            conditions.append("municipio = %s")
            params.append(municipio)
        if nombre:
            conditions.append("UPPER(nombre_central) LIKE %s")
            params.append(f"%{nombre.upper()}%")
        where = " AND ".join(conditions)
        cur.execute(
            f"""SELECT id, nombre_central, tipo, municipio, estado,
                       latitud, longitud, estatus, visible_pwa, created_at
                FROM catalogo_centrales WHERE {where}
                ORDER BY estado, municipio, nombre_central""",
            params,
        )
        return [dict(r) for r in cur.fetchall()]


@router.get("/todas", response_model=List[CentralOut])
def list_centrales_todas_offline(user_id: str = Depends(get_current_user_id)):
    """Devuelve todas las centrales autorizadas y visibles para cache offline."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, nombre_central, tipo, municipio, estado,
                      latitud, longitud, estatus, visible_pwa, created_at
               FROM catalogo_centrales
               WHERE estatus = 'autorizado' AND visible_pwa = TRUE
               ORDER BY estado, municipio, nombre_central"""
        )
        return [dict(r) for r in cur.fetchall()]


@router.get("/{central_id}", response_model=CentralOut)
def get_central(central_id: int, user_id: str = Depends(get_current_user_id)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, nombre_central, tipo, municipio, estado,
                      latitud, longitud, estatus, visible_pwa, created_at
               FROM catalogo_centrales WHERE id = %s AND estatus = 'autorizado' AND visible_pwa = TRUE""",
            (central_id,),
        )
        row = cur.fetchone()
    if not row:
        raise HTTPException(404, "Central no encontrada")
    return dict(row)


# ── Mis Centrales (capturista) ──

@router.get("/capturista/mis-centrales", response_model=List[CaptoristasCentralOut])
def list_mis_centrales(user_id: str = Depends(get_current_user_id)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT cc.id, cc.central_id, cc.es_favorita, cc.created_at,
                      c.nombre_central, c.tipo, c.municipio, c.estado,
                      c.latitud, c.longitud
               FROM capturista_centrales cc
               JOIN catalogo_centrales c ON c.id = cc.central_id
               WHERE cc.usuario_id = %s::uuid
               ORDER BY cc.es_favorita DESC, c.nombre_central""",
            (user_id,),
        )
        return [dict(r) for r in cur.fetchall()]


@router.post("/capturista/mis-centrales", response_model=CaptoristasCentralOut, status_code=201)
def add_mi_central(data: CentralCreate, user_id: str = Depends(get_current_user_id)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, nombre_central, tipo, municipio, estado, latitud, longitud FROM catalogo_centrales WHERE id = %s AND estatus = 'autorizado' AND visible_pwa = TRUE",
            (data.central_id,),
        )
        c = cur.fetchone()
        if not c:
            raise HTTPException(404, "Central no encontrada o no disponible")

        cur.execute(
            "SELECT id FROM capturista_centrales WHERE usuario_id = %s::uuid AND central_id = %s",
            (user_id, data.central_id),
        )
        if cur.fetchone():
            raise HTTPException(409, "Ya tienes esta central agregada")

        cur.execute(
            """INSERT INTO capturista_centrales (usuario_id, central_id, es_favorita)
               VALUES (%s::uuid, %s, %s)
               RETURNING id, created_at""",
            (user_id, data.central_id, data.es_favorita),
        )
        r = cur.fetchone()

    return CaptoristasCentralOut(
        id=r["id"],
        central_id=c["id"],
        es_favorita=data.es_favorita,
        created_at=r["created_at"],
        nombre_central=c["nombre_central"],
        tipo=c["tipo"],
        municipio=c["municipio"],
        estado=c["estado"],
        latitud=c["latitud"],
        longitud=c["longitud"],
    )


@router.delete("/capturista/mis-centrales/{relacion_id}", status_code=204)
def delete_mi_central(relacion_id: int, user_id: str = Depends(get_current_user_id)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM capturista_centrales WHERE id = %s AND usuario_id = %s::uuid",
            (relacion_id, user_id),
        )
        if cur.rowcount == 0:
            raise HTTPException(404, "Central no encontrada en tus centrales")


# ── Propuestas de nuevas centrales ──

@router.post("/propuestas", response_model=PropuestaCentralOut, status_code=201)
def proponer_central(data: PropuestaCentralCreate, user_id: str = Depends(get_current_user_id)):
    if len(data.nombre_central.strip()) < 4:
        raise HTTPException(400, "El nombre debe tener al menos 4 caracteres")
    if not (-90 <= data.latitud <= 90) or not (-180 <= data.longitud <= 180):
        raise HTTPException(400, "Coordenadas fuera de rango")
    if data.latitud == 0 and data.longitud == 0:
        raise HTTPException(400, "Coordenadas inválidas (0,0)")

    with get_db() as conn:
        cur = conn.cursor()

        cur.execute(
            """SELECT id, estatus, created_at FROM propuestas_centrales
               WHERE usuario_id = %s::uuid
                 AND nombre_central = %s
                 AND estado = %s
                 AND municipio = %s
                 AND ABS(latitud - %s) < 0.001
                 AND ABS(longitud - %s) < 0.001
               ORDER BY created_at DESC LIMIT 1""",
            (user_id, data.nombre_central.strip(), data.estado, data.municipio, data.latitud, data.longitud),
        )
        existing = cur.fetchone()
        if existing:
            return PropuestaCentralOut(
                id=existing["id"],
                nombre_central=data.nombre_central.strip(),
                tipo=data.tipo,
                municipio=data.municipio,
                estado=data.estado,
                latitud=data.latitud,
                longitud=data.longitud,
                estatus=existing["estatus"],
                created_at=existing["created_at"],
            )

        cur.execute(
            """INSERT INTO propuestas_centrales
                   (usuario_id, nombre_central, tipo, municipio, estado, latitud, longitud)
               VALUES (%s::uuid, %s, %s, %s, %s, %s, %s)
               RETURNING id, estatus, created_at""",
            (user_id, data.nombre_central.strip(), data.tipo, data.municipio, data.estado, data.latitud, data.longitud),
        )
        r = cur.fetchone()

    return PropuestaCentralOut(
        id=r["id"],
        nombre_central=data.nombre_central.strip(),
        tipo=data.tipo,
        municipio=data.municipio,
        estado=data.estado,
        latitud=data.latitud,
        longitud=data.longitud,
        estatus=r["estatus"],
        created_at=r["created_at"],
    )


@router.get("/capturista/propuestas", response_model=List[PropuestaCentralOut])
def list_propuestas(user_id: str = Depends(get_current_user_id)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, nombre_central, tipo, municipio, estado, latitud, longitud,
                      estatus, motivo_rechazo, created_at
               FROM propuestas_centrales WHERE usuario_id = %s::uuid
               ORDER BY created_at DESC""",
            (user_id,),
        )
        rows = cur.fetchall()
    return [
        PropuestaCentralOut(
            id=r["id"],
            nombre_central=r["nombre_central"],
            tipo=r["tipo"],
            municipio=r["municipio"],
            estado=r["estado"],
            latitud=float(r["latitud"]) if r["latitud"] else None,
            longitud=float(r["longitud"]) if r["longitud"] else None,
            estatus=r["estatus"],
            motivo_rechazo=r["motivo_rechazo"],
            created_at=r["created_at"],
        )
        for r in rows
    ]
