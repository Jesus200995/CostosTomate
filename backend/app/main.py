from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, catalogos, centrales, jitomate, admin_auth
from app.config import settings

app = FastAPI(title="COSTOS Tomate API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
        "http://localhost:5174",
        "http://localhost:5175",
        "https://costos.sembrandodatos.com",
        "https://apicostos.sembrandodatos.com",
        "https://admincostos.sembrandodatos.com",
        "https://jitomate.sembrandodatos.com",
        "https://apijitomate.sembrandodatos.com",
        "https://monitoreo.geodatos.com.mx",
        "https://adminmonitoreo.geodatos.com.mx",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(catalogos.router, prefix="/api/catalogos", tags=["catalogos"])
app.include_router(centrales.router, prefix="/api/centrales", tags=["centrales"])
app.include_router(jitomate.router, prefix="/api/jitomate", tags=["jitomate"])
app.include_router(admin_auth.router, prefix="/api/admin", tags=["admin"])


@app.get("/api/health")
def health():
    from datetime import datetime, timezone
    return {"status": "ok", "version": "2.0.0", "sistema": "cosostomate", "timestamp": datetime.now(timezone.utc).isoformat()}
