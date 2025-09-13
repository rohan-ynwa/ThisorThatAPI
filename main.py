from typing import Optional
from fastapi import FastAPI
from utils import get_best_alternative
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

    alternatives = get_best_alternative(food_item, criteria={
        'GHG_Emissions_Score': co2,
        'Land_Use_Score': land,
        'Water_Use_Score': water,
        'Nitrogen_Score': fertilizer
    })
    return alternatives
