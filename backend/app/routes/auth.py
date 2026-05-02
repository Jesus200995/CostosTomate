from fastapi import APIRouter, HTTPException, Depends
from app.schemas import RegisterRequest, LoginRequest, UpdateProfileRequest, UserPublic, AuthResponse
from app.database import get_db
from app.auth import hash_password, verify_password, create_token, get_current_user_id

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(data: RegisterRequest):
    if len(data.name.strip()) < 2:
        raise HTTPException(400, "El nombre debe tener al menos 2 caracteres")
    if len(data.password) < 6:
        raise HTTPException(400, "La contraseña debe tener al menos 6 caracteres")
    if not data.consent:
        raise HTTPException(400, "Debes aceptar el aviso de privacidad")
    if data.tipo_capturista not in ("REPRESENTANTE_CAC", "COM_COMERCIALIZACION", "OFICINAS"):
        raise HTTPException(400, "Tipo de capturista inválido")
    curp = data.curp.upper().strip()
    if len(curp) != 18:
        raise HTTPException(400, "La CURP debe tener exactamente 18 caracteres")
    if data.telefono and len(data.telefono.strip()) > 10:
        raise HTTPException(400, "El teléfono debe tener máximo 10 dígitos")

    with get_db() as conn:
        cur = conn.cursor()

        cur.execute("SELECT id FROM users WHERE email = %s", (data.email.lower().strip(),))
        if cur.fetchone():
            raise HTTPException(409, "Este correo ya está registrado")

        cur.execute("SELECT id FROM users WHERE curp = %s", (curp,))
        if cur.fetchone():
            raise HTTPException(409, "Esta CURP ya está registrada")

        hashed = hash_password(data.password)
        cur.execute(
            """INSERT INTO users (name, email, password, curp, tipo_capturista, estado, municipio,
               localidad, telefono, consent, cac_id, cac_nombre, territorio, ruta,
               rol_comision, correo_institucional, rol_interno)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
               RETURNING id, name, email, avatar, created_at, curp, tipo_capturista, estado,
               municipio, localidad, telefono, consent, cac_id, cac_nombre, territorio, ruta,
               rol_comision, correo_institucional, rol_interno""",
            (
                data.name.strip().upper(),
                data.email.lower().strip(),
                hashed,
                curp,
                data.tipo_capturista,
                data.estado,
                data.municipio,
                data.localidad.strip().upper() if data.localidad else None,
                data.telefono.strip() if data.telefono else None,
                data.consent,
                data.cac_id.strip().upper() if data.cac_id else None,
                data.cac_nombre.strip().upper() if data.cac_nombre else None,
                data.territorio or None,
                data.ruta.strip().upper() if data.ruta else None,
                data.rol_comision or None,
                data.correo_institucional or None,
                data.rol_interno or None,
            ),
        )
        row = cur.fetchone()

    user = UserPublic(
        id=str(row["id"]),
        name=row["name"],
        email=row["email"],
        avatar=row["avatar"],
        createdAt=row["created_at"].isoformat(),
        curp=row["curp"],
        tipo_capturista=row["tipo_capturista"],
        estado=row["estado"],
        municipio=row["municipio"],
        localidad=row["localidad"],
        telefono=row["telefono"],
        consent=row["consent"] or False,
        cac_id=row["cac_id"],
        cac_nombre=row["cac_nombre"],
        territorio=row["territorio"],
        ruta=row["ruta"],
        rol_comision=row["rol_comision"],
        correo_institucional=row["correo_institucional"],
        rol_interno=row["rol_interno"],
    )
    token = create_token(user.id)
    return AuthResponse(user=user, token=token)


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, name, email, password, avatar, created_at, curp, tipo_capturista,
               estado, municipio, localidad, telefono, consent, cac_id, cac_nombre,
               territorio, ruta, rol_comision, correo_institucional, rol_interno
               FROM users WHERE email = %s""",
            (data.email.lower().strip(),),
        )
        row = cur.fetchone()

    if not row or not verify_password(data.password, row["password"]):
        raise HTTPException(401, "Credenciales incorrectas")

    user = UserPublic(
        id=str(row["id"]),
        name=row["name"],
        email=row["email"],
        avatar=row["avatar"],
        createdAt=row["created_at"].isoformat(),
        curp=row["curp"],
        tipo_capturista=row["tipo_capturista"],
        estado=row["estado"],
        municipio=row["municipio"],
        localidad=row["localidad"],
        telefono=row["telefono"],
        consent=row["consent"] or False,
        cac_id=row["cac_id"],
        cac_nombre=row["cac_nombre"],
        territorio=row["territorio"],
        ruta=row["ruta"],
        rol_comision=row["rol_comision"],
        correo_institucional=row["correo_institucional"],
        rol_interno=row["rol_interno"],
    )
    token = create_token(user.id)
    return AuthResponse(user=user, token=token)


@router.get("/profile", response_model=UserPublic)
def profile(user_id: str = Depends(get_current_user_id)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, name, email, avatar, created_at, curp, tipo_capturista,
               estado, municipio, localidad, telefono, consent, cac_id, cac_nombre,
               territorio, ruta, rol_comision, correo_institucional, rol_interno
               FROM users WHERE id = %s::uuid""",
            (user_id,),
        )
        row = cur.fetchone()

    if not row:
        raise HTTPException(404, "Usuario no encontrado")

    return UserPublic(
        id=str(row["id"]),
        name=row["name"],
        email=row["email"],
        avatar=row["avatar"],
        createdAt=row["created_at"].isoformat(),
        curp=row["curp"],
        tipo_capturista=row["tipo_capturista"],
        estado=row["estado"],
        municipio=row["municipio"],
        localidad=row["localidad"],
        telefono=row["telefono"],
        consent=row["consent"] or False,
        cac_id=row["cac_id"],
        cac_nombre=row["cac_nombre"],
        territorio=row["territorio"],
        ruta=row["ruta"],
        rol_comision=row["rol_comision"],
        correo_institucional=row["correo_institucional"],
        rol_interno=row["rol_interno"],
    )


@router.put("/profile", response_model=UserPublic)
def update_profile(data: UpdateProfileRequest, user_id: str = Depends(get_current_user_id)):
    if len(data.name.strip()) < 2:
        raise HTTPException(400, "El nombre debe tener al menos 2 caracteres")
    curp = data.curp.upper().strip()
    if len(curp) != 18:
        raise HTTPException(400, "La CURP debe tener exactamente 18 caracteres")
    if data.telefono and len(data.telefono.strip()) > 10:
        raise HTTPException(400, "El teléfono debe tener máximo 10 dígitos")
    if data.tipo_capturista not in ("REPRESENTANTE_CAC", "COM_COMERCIALIZACION", "OFICINAS"):
        raise HTTPException(400, "Tipo de capturista inválido")

    with get_db() as conn:
        cur = conn.cursor()

        cur.execute("SELECT id FROM users WHERE curp = %s AND id != %s::uuid", (curp, user_id))
        if cur.fetchone():
            raise HTTPException(409, "Esta CURP ya está registrada por otro usuario")

        cur.execute(
            """UPDATE users SET name=%s, curp=%s, tipo_capturista=%s, estado=%s, municipio=%s,
               localidad=%s, telefono=%s, cac_id=%s, cac_nombre=%s, territorio=%s, ruta=%s,
               rol_comision=%s, correo_institucional=%s, rol_interno=%s
               WHERE id=%s::uuid
               RETURNING id, name, email, avatar, created_at, curp, tipo_capturista, estado,
               municipio, localidad, telefono, consent, cac_id, cac_nombre, territorio, ruta,
               rol_comision, correo_institucional, rol_interno""",
            (
                data.name.strip().upper(),
                curp,
                data.tipo_capturista,
                data.estado,
                data.municipio,
                data.localidad.strip().upper() if data.localidad else None,
                data.telefono.strip() if data.telefono else None,
                data.cac_id.strip().upper() if data.cac_id else None,
                data.cac_nombre.strip().upper() if data.cac_nombre else None,
                data.territorio or None,
                data.ruta.strip().upper() if data.ruta else None,
                data.rol_comision or None,
                data.correo_institucional or None,
                data.rol_interno or None,
                user_id,
            ),
        )
        row = cur.fetchone()

    if not row:
        raise HTTPException(404, "Usuario no encontrado")

    return UserPublic(
        id=str(row["id"]),
        name=row["name"],
        email=row["email"],
        avatar=row["avatar"],
        createdAt=row["created_at"].isoformat(),
        curp=row["curp"],
        tipo_capturista=row["tipo_capturista"],
        estado=row["estado"],
        municipio=row["municipio"],
        localidad=row["localidad"],
        telefono=row["telefono"],
        consent=row["consent"] or False,
        cac_id=row["cac_id"],
        cac_nombre=row["cac_nombre"],
        territorio=row["territorio"],
        ruta=row["ruta"],
        rol_comision=row["rol_comision"],
        correo_institucional=row["correo_institucional"],
        rol_interno=row["rol_interno"],
    )
