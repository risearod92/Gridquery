from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text

# Import your two new infrastructure files!
import database
import models

# ==========================================
# 1. INITIALIZATION & DATABASE SYNC
# ==========================================
# This tells SQLAlchemy to look at models.py and build the shelves in Postgres
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="GridQuery Backend",
    description="Core API engine for geospatial energy asset routing",
    version="0.1.0"
)

# ==========================================
# 2. DATA BLUEPRINTS (PYDANTIC MODELS)
# ==========================================
class SubstationAsset(BaseModel):
    name: str
    capacity_mw: int
    state: str
    is_active: bool = True

# To send data OUT of the API, we need to tell Pydantic to expect a database ID,
# and we need to tell it to play nicely with SQLAlchemy ORM objects.
class SubstationResponse(SubstationAsset):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Notice: The db_mock_storage list is COMPLETELY GONE.

# ==========================================
# 4. GET ROUTES (READ OPERATIONS)
# ==========================================

@app.get("/")
def read_root():
    return {"status": "ok", "service": "GridQuery API Engine"}

@app.get("/health")
def health_check(db: Session = Depends(database.get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")

# Notice the injection: db: Session = Depends(database.get_db)
@app.get("/substations", response_model=List[SubstationResponse])
def get_all_substations(db: Session = Depends(database.get_db)):
    assets = db.query(models.DBSubstationAsset).all()
    return assets

@app.get("/substations/{asset_id}", response_model=SubstationResponse)
def get_single_substation(asset_id: int, db: Session = Depends(database.get_db)):
    asset = db.query(models.DBSubstationAsset).filter(models.DBSubstationAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found in Postgres.")
    return asset

# ==========================================
# 5. DATA MUTATION ROUTES (CREATE, UPDATE, DELETE)
# ==========================================

@app.post("/substations", response_model=SubstationResponse, status_code=status.HTTP_201_CREATED)
def create_substation(payload: SubstationAsset, db: Session = Depends(database.get_db)):
    # 1. Convert Pydantic payload to dict
    # 2. Unpack into the SQLAlchemy model
    new_asset = models.DBSubstationAsset(**payload.model_dump())
    
    # 3. Write to Postgres
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset) # Grabs the auto-generated ID from Postgres
    
    return new_asset

@app.put("/substations/{asset_id}", response_model=SubstationResponse)
def update_substation(asset_id: int, payload: SubstationAsset, db: Session = Depends(database.get_db)):
    # Find the existing row
    db_asset = db.query(models.DBSubstationAsset).filter(models.DBSubstationAsset.id == asset_id).first()
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found.")
    
    # Update the row's attributes
    db_asset.name = payload.name
    db_asset.capacity_mw = payload.capacity_mw
    db_asset.state = payload.state
    db_asset.is_active = payload.is_active
    
    # Save the changes
    db.commit()
    db.refresh(db_asset)
    return db_asset

@app.delete("/substations/{asset_id}")
def delete_substation(asset_id: int, db: Session = Depends(database.get_db)):
    # Find the existing row
    db_asset = db.query(models.DBSubstationAsset).filter(models.DBSubstationAsset.id == asset_id).first()
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found.")
    
    # Destroy it
    db.delete(db_asset)
    db.commit()
    return {"message": f"Asset {asset_id} permanently deleted from Postgres."}