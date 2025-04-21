from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from modules.fuzzy.evaluation import run_test_cases
from modules.cluster.evaluation import hierarchical_clustering
from modules.pso.optimization import pso
from modules.utils import generate_random_test_cases, consolidate_results
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Traffic Sensor Analysis API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TestCase(BaseModel):
    vpm: float
    spd: float
    den: float
    expected: Optional[str] = None


def run_pipeline(test_data: List[dict]):
    fuzzy = run_test_cases(test_data)
    clusters, sensors = hierarchical_clustering(fuzzy)
    result = pso(clusters)
    final_df = consolidate_results(sensors, result)
    return final_df.to_dict(orient="records")


@app.post("/evaluate")
def evaluate_json(test_cases: List[TestCase]):
    test_data = [item.dict() for item in test_cases]
    results = run_pipeline(test_data)
    return {"result": results}


@app.post("/evaluate/{sensors}")
def evaluate_random(sensors: int):
    if sensors <= 0:
        raise HTTPException(
            status_code=400, detail="'sensors' must be a positive integer."
        )

    test_data = generate_random_test_cases(sensors)
    results = run_pipeline(test_data)
    return {"result": results}
