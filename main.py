from typing import Optional
from fastapi import FastAPI
from utils import get_best_alternative

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "ello love"}
    
@app.get("/items/")
async def get_impact(
    food_item: str,
    co2: Optional[bool] = False,
    land: Optional[bool] = False,
    water: Optional[bool] = False,
    fertilizer: Optional[bool] = False,
):
    alternatives = get_best_alternative(food_item, co2, land, water, fertilizer)
    return alternatives
