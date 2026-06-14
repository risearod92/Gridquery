from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List

# ==========================================
# 1. INITIALIZATION & CONFIGURATION
# ==========================================
app = FastAPI(
    title="GridQuery Backend",
    description="Core API engine for geospatial energy asset routing",
    version="0.1.0"
)

# ==========================================
# 2. DATA BLUEPRINTS (PYDANTIC MODELS)
# ==========================================
# These must go near the top so your route functions below can see them!
class SubstationAsset(BaseModel):
    name: str
    capacity_mw: int
    state: str
    is_active: bool = True

# ==========================================
# 3. STORAGE LAYER (MOCK DATABASE)
# ==========================================
db_mock_storage = [
    {"id": 1, "name": "Athens Substation", "capacity_mw": 500, "state": "NY", "is_active": True},
    {"id": 2, "name": "Bowline Substation", "capacity_mw": 1200, "state": "NY", "is_active": True}
]

# ==========================================
# 4. GET ROUTES (READ OPERATIONS)
# ==========================================

@app.get("/")
def read_root():
    return {"status": "healthy", "service": "GridQuery API Engine"}

# Your old path/query tests from Day 1
@app.get("/substations", response_model=List[dict])
def get_all_substations():
    return db_mock_storage

@app.get("/substations/{asset_id}")
def get_single_substation(asset_id: int):
    for asset in db_mock_storage:
        if asset["id"] == asset_id:
            return asset
    raise HTTPException(status_code=404, detail="Asset not found.")

# ==========================================
# 5. DATA MUTATION ROUTES (CREATE, UPDATE, DELETE)
# ==========================================
# Group your new operational tools neatly together at the bottom

@app.post("/substations", status_code=status.HTTP_201_CREATED)
def create_substation(payload: SubstationAsset):
    new_id = len(db_mock_storage) + 1
    new_asset_dict = payload.model_dump()
    new_asset_dict["id"] = new_id
    db_mock_storage.append(new_asset_dict)
    return {"message": "Asset created successfully", "data": new_asset_dict}

@app.put("/substations/{asset_id}")
def update_substation(asset_id: int, payload: SubstationAsset):
    for asset in db_mock_storage:
        if asset["id"] == asset_id:
            asset["name"] = payload.name
            asset["capacity_mw"] = payload.capacity_mw
            asset["state"] = payload.state
            asset["is_active"] = payload.is_active
            return {"message": f"Asset {asset_id} updated", "data": asset}
    raise HTTPException(status_code=404, detail="Asset not found.")

@app.delete("/substations/{asset_id}")
def delete_substation(asset_id: int):
    for index, asset in enumerate(db_mock_storage):
        if asset["id"] == asset_id:
            deleted_asset = db_mock_storage.pop(index)
            return {"message": "Asset deleted", "purged_data": deleted_asset}
    raise HTTPException(status_code=404, detail="Asset not found.")
