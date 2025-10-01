from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import statistics

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
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

# Your data embedded directly in code
latency_data = [
  {"region": "apac", "service": "support", "latency_ms": 205.28, "uptime_pct": 97.728, "timestamp": 20250301},
  {"region": "apac", "service": "recommendations", "latency_ms": 192.72, "uptime_pct": 99.33, "timestamp": 20250302},
  {"region": "apac", "service": "payments", "latency_ms": 193.06, "uptime_pct": 99.034, "timestamp": 20250303},
  {"region": "apac", "service": "support", "latency_ms": 194.72, "uptime_pct": 97.832, "timestamp": 20250304},
  {"region": "apac", "service": "catalog", "latency_ms": 143.34, "uptime_pct": 98.547, "timestamp": 20250305},
  {"region": "apac", "service": "recommendations", "latency_ms": 175.38, "uptime_pct": 99.071, "timestamp": 20250306},
  {"region": "apac", "service": "payments", "latency_ms": 171.28, "uptime_pct": 98.904, "timestamp": 20250307},
  {"region": "apac", "service": "support", "latency_ms": 202.82, "uptime_pct": 98.884, "timestamp": 20250308},
  {"region": "apac", "service": "recommendations", "latency_ms": 178.75, "uptime_pct": 99.354, "timestamp": 20250309},
  {"region": "apac", "service": "analytics", "latency_ms": 158.79, "uptime_pct": 97.735, "timestamp": 20250310},
  {"region": "apac", "service": "checkout", "latency_ms": 173.59, "uptime_pct": 97.213, "timestamp": 20250311},
  {"region": "apac", "service": "recommendations", "latency_ms": 102.16, "uptime_pct": 97.528, "timestamp": 20250312},
  {"region": "emea", "service": "support", "latency_ms": 185.03, "uptime_pct": 97.358, "timestamp": 20250301},
  {"region": "emea", "service": "payments", "latency_ms": 200.37, "uptime_pct": 98.099, "timestamp": 20250302},
  {"region": "emea", "service": "payments", "latency_ms": 121.09, "uptime_pct": 97.85, "timestamp": 20250303},
  {"region": "emea", "service": "support", "latency_ms": 158.6, "uptime_pct": 98.375, "timestamp": 20250304},
  {"region": "emea", "service": "checkout", "latency_ms": 155.96, "uptime_pct": 97.514, "timestamp": 20250305},
  {"region": "emea", "service": "recommendations", "latency_ms": 181.19, "uptime_pct": 97.329, "timestamp": 20250306},
  {"region": "emea", "service": "analytics", "latency_ms": 167.06, "uptime_pct": 99.362, "timestamp": 20250307},
  {"region": "emea", "service": "analytics", "latency_ms": 229.65, "uptime_pct": 98.047, "timestamp": 20250308},
  {"region": "emea", "service": "checkout", "latency_ms": 162.78, "uptime_pct": 98.987, "timestamp": 20250309},
  {"region": "emea", "service": "support", "latency_ms": 166.91, "uptime_pct": 97.377, "timestamp": 20250310},
  {"region": "emea", "service": "support", "latency_ms": 209.73, "uptime_pct": 97.117, "timestamp": 20250311},
  {"region": "emea", "service": "analytics", "latency_ms": 178.05, "uptime_pct": 97.424, "timestamp": 20250312},
  {"region": "amer", "service": "checkout", "latency_ms": 203.9, "uptime_pct": 97.484, "timestamp": 20250301},
  {"region": "amer", "service": "catalog", "latency_ms": 180.81, "uptime_pct": 97.406, "timestamp": 20250302},
  {"region": "amer", "service": "recommendations", "latency_ms": 181.85, "uptime_pct": 98.429, "timestamp": 20250303},
  {"region": "amer", "service": "support", "latency_ms": 136.86, "uptime_pct": 97.443, "timestamp": 20250304},
  {"region": "amer", "service": "support", "latency_ms": 162.03, "uptime_pct": 97.452, "timestamp": 20250305},
  {"region": "amer", "service": "checkout", "latency_ms": 108.18, "uptime_pct": 97.499, "timestamp": 20250306},
  {"region": "amer", "service": "checkout", "latency_ms": 216.32, "uptime_pct": 98.823, "timestamp": 20250307},
  {"region": "amer", "service": "checkout", "latency_ms": 193.06, "uptime_pct": 97.988, "timestamp": 20250308},
  {"region": "amer", "service": "payments", "latency_ms": 125.48, "uptime_pct": 98.258, "timestamp": 20250309},
  {"region": "amer", "service": "analytics", "latency_ms": 144.75, "uptime_pct": 99.364, "timestamp": 20250310},
  {"region": "amer", "service": "catalog", "latency_ms": 183.25, "uptime_pct": 97.326, "timestamp": 20250311},
  {"region": "amer", "service": "payments", "latency_ms": 129.79, "uptime_pct": 99.186, "timestamp": 20250312}
]

@app.post("/api/latency-metrics")
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
            
        # Extract latency values and uptime
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

@app.get("/health")
async def health():
    return {"status": "healthy", "data_points": len(latency_data)}

# Handle OPTIONS requests for CORS preflight
@app.options("/api/latency-metrics")
async def options_latency_metrics():
    return {"message": "OK"}
