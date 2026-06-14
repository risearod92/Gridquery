from fastapi import FastAPI

# 1. Initialize the FastAPI application instance
app = FastAPI(
    title="GridQuery Backend",
    description="Core API engine for geospatial energy asset routing",
    version="0.1.0"
)

# 2. Define a root endpoint (GET request to "/")
@app.get("/")
def read_root():
    """
    Health check endpoint to verify the API is alive and responsive.
    """
    return {
        "status": "healthy",
        "service": "GridQuery API Engine",
        "database_connected": False  # We will wire this up to Postgres in Week 1
    }

# 3. Define an endpoint with path and query parameters
@app.get("/substations/{substation_id}")
def get_substation_metrics(substation_id: int, q: str = None):
    """
    Mock endpoint simulating a lookup of an energy substation asset.
    """
    return {
        "substation_id": substation_id,
        "query_filter": q,
        "voltage_kv": 500,
        "grid_region": "PJM"
    }