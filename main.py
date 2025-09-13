from typing import Optional
from fastapi import FastAPI
from utils import find_replacements
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add this block before your routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://thisorthatfood.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    
    # this is a bit clunky lol, should prolly use a map but i dont got time
    criteria = []
    if co2:
        criteria.append('GHG_Emissions_Score')
    if land:
        criteria.append('Land_Use_Score')
    if water:
        criteria.append('Water_Use_Score')
    if fertilizer:
        criteria.append('Nitrogen_Score')

    if not criteria:
        # set all to true if none specified
        criteria = [
            'GHG_Emissions_Score',
            'Land_Use_Score',
            'Water_Use_Score',
            'Nitrogen_Score'
        ]


    alternatives = find_replacements(food_item, criteria)
    return alternatives
