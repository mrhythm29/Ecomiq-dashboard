from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.data_engine import DataEngine

app = FastAPI(title="E-Commerce Customer Intelligence Dashboard")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engine
engine = DataEngine()

# APIs
@app.get("/api/kpis")
def get_kpis():
    return engine.get_kpis()

@app.get("/api/revenue-trend")
def get_revenue_trend(filter: str = '30D'):
    return engine.get_revenue_trend(filter_type=filter)

@app.get("/api/segments")
def get_segments():
    return engine.get_audience_segments()

@app.get("/api/insights")
def get_insights():
    return engine.get_insights()

@app.get("/api/top-products")
def get_top_products():
    return engine.get_top_products()

# Static frontend serve
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')

app.mount("/css", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")

@app.get("/")
def read_index():
    return FileResponse(os.path.join(frontend_dir, 'index.html'))