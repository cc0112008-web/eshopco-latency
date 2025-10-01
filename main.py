from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from typing import List
import statistics
import os

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

class LatencyRequest(BaseModel):
    regions: List[str]
    threshold_ms: int

class RegionMetrics(BaseModel):
    region: str
    avg_latency: float
    p95_latency: float
    avg_uptime: float
    breaches: int

# Load your actual latency data
def load_latency_data():
    try:
        with open('q-vercel-latency.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading latency data: {e}")
        return []

latency_data = load_latency_data()

@app.post("/api/latency-metrics", response_model=List[RegionMetrics])
async def get_latency_metrics(request: LatencyRequest):
    results = []
    
    for region in request.regions:
        # Filter data for the current region
        region_data = [item for item in latency_data if item.get('region') == region]
        
        if not region_data:
            # Return zero metrics if no data for region
            results.append(RegionMetrics(
                region=region,
                avg_latency=0.0,
                p95_latency=0.0,
                avg_uptime=0.0,
                breaches=0
            ))
            continue
            
        # Extract latency values and uptime from your specific data structure
        latencies = [item['latency_ms'] for item in region_data]
        uptimes = [item['uptime_pct'] / 100.0 for item in region_data]  # Convert percentage to decimal
        
        # Calculate metrics
        avg_latency = statistics.mean(latencies)
        
        # Calculate 95th percentile
        if latencies:
            sorted_latencies = sorted(latencies)
            index_95 = int(0.95 * len(sorted_latencies))
            p95_latency = sorted_latencies[index_95]
        else:
            p95_latency = 0.0
            
        avg_uptime = statistics.mean(uptimes)
        breaches = sum(1 for latency in latencies if latency > request.threshold_ms)
        
        results.append(RegionMetrics(
            region=region,
            avg_latency=round(avg_latency, 2),
            p95_latency=round(p95_latency, 2),
            avg_uptime=round(avg_uptime, 4),
            breaches=breaches
        ))
    
    return results

@app.get("/")
async def root():
    return {"message": "eShopCo Latency Metrics API - POST to /api/latency-metrics"}

# For Vercel serverless compatibility
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
