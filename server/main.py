from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from modules.operadoras.route import routes as operadoras_routes

app = FastAPI()
app.include_router(operadoras_routes, prefix="/api", tags=["Operadoras"])

origins = "http://localhost:5173/"
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def healt():
    return {"status":"ok"}
