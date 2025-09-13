import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import List, Dict

# --- Configuration ---
CSV_PATH = 'df_labeled_cleaned.csv'

# Nutrient and sustainability columns
NUTRIENT_COLS = [
    'Calories_kcal', 'Total_Fat_g', 'Sodium_mg', 'Total_Carbohydrate_g',
    'Dietary_Fiber_g', 'Protein_g', 'Calcium_mg', 'Iron_mg', 'Potassium_mg'
]
SUSTAINABILITY_COLS = [
    'Land_Use_Score', 'Nitrogen_Score', 'Water_Use_Score', 'GHG_Emissions_Score'
]

def find_replacements(
    food_name: str,
    criteria: List[str],
    top_n: int = 5,
    same_category: bool = False
) -> Dict:
    """
    Find sustainable replacements for a given food.

    Args:
        food_name: Exact USDA_Food_Name in the CSV.
        criteria: List of sustainability columns to improve.
        top_n: Number of recommendations to return.
        same_category: If True, restrict to same Food_Category.

    Returns:
        A dict with 'target' and 'recommendations' or 'error'.
    """
    # --- Load and prepare data ---
    df = pd.read_csv(CSV_PATH)

    # Ensure numeric
    for col in NUTRIENT_COLS + SUSTAINABILITY_COLS:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Build scaler on nutrient space for similarity calculations
    scaler = StandardScaler().fit(df[NUTRIENT_COLS].values)

    # 1. Locate target food
    target_rows = df[df['USDA_Food_Name'] == food_name]
    if target_rows.empty:
        return {'error': f'Food "{food_name}" not found.'}
    target = target_rows.iloc[0]
    cluster_id = target['Cluster']

    # 2. Gather cluster members excluding target
    candidates = df[
        (df['Cluster'] == cluster_id) &
        (df.index != target.name)
    ].copy()

    # 3. Optional same category filter
    if same_category:
        candidates = candidates[candidates['Food_Category'] == target['Food_Category']]
        if candidates.empty:
            return {'error': 'No same-category foods in target cluster.'}

    # 4. Validate criteria
    valid = [c for c in criteria if c in SUSTAINABILITY_COLS]
    if not valid:
        return {'error': f'Invalid criteria. Valid options: {SUSTAINABILITY_COLS}'}

    # 5. Filter for better sustainability
    for crit in valid:
        candidates = candidates[candidates[crit] > target[crit]]
    if candidates.empty:
        return {'error': 'No better sustainable alternatives found in same cluster.'}

    # 6. Compute nutrient distance
    target_vec = scaler.transform([target[NUTRIENT_COLS].values])
    cand_vecs = scaler.transform(candidates[NUTRIENT_COLS].values)
    distances = np.linalg.norm(cand_vecs - target_vec, axis=1)
    candidates['nutrient_distance'] = distances

    # 7. Compute sustainability improvements
    improvements = []
    for _, row in candidates.iterrows():
        vals = [(row[crit] - target[crit]) / target[crit] * 100 for crit in valid]
        improvements.append(np.mean(vals))
    candidates['sustainability_improvement'] = improvements

    # 8. Rank by combined score (prioritize improvement, penalize distance)
    candidates['combined_score'] = (
        candidates['sustainability_improvement'] / 10 - candidates['nutrient_distance']
    )

    best = candidates.nlargest(top_n, 'combined_score')

    # 9. Format results
    max_dist = best['nutrient_distance'].max()

    # sort such that most similar is first
    best = best.sort_values('nutrient_distance')

    recommendations = []
    for _, r in best.iterrows():
        similarity = max(0, (1 - r['nutrient_distance'] / max_dist) * 100)
        rec = {
            'name': r['USDA_Food_Name'],
            'nutrient_similarity': round(similarity, 1),
            'co2': float(r['GHG_Emissions_Score']),
            'land': float(r['Land_Use_Score']),
            'water': float(r['Water_Use_Score']),
            'fertilizer': float(r['Nitrogen_Score'])
        }
        recommendations.append(rec)

    return recommendations
