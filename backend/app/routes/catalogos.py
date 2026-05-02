from fastapi import APIRouter, Query
from typing import List
from app.schemas import EstadoOut, MunicipioOut
from app.database import get_db

router = APIRouter()


@router.get("/estados", response_model=List[EstadoOut])
def list_estados():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT cve_ent, nom_ent FROM estados ORDER BY nom_ent")
        rows = cur.fetchall()
    return [EstadoOut(cve_ent=r["cve_ent"], nom_ent=r["nom_ent"]) for r in rows]


@router.get("/municipios", response_model=List[MunicipioOut])
def list_municipios(cve_ent: str = Query(..., description="Clave de entidad")):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT clave_mun, nomgeo, cve_ent, territorio FROM municipios WHERE cve_ent = %s ORDER BY nomgeo",
            (cve_ent,),
        )
        rows = cur.fetchall()
    return [MunicipioOut(clave_mun=r["clave_mun"], nomgeo=r["nomgeo"], cve_ent=r["cve_ent"], territorio=r["territorio"]) for r in rows]
