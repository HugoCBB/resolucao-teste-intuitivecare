from fastapi import FastAPI
from modules.operadoras.route import routes as operadoras_routes

app = FastAPI()
app.include_router(operadoras_routes, prefix="/api", tags=["Operadoras"])


@app.get("/")
async def healt():
    return {"status":"ok"}
