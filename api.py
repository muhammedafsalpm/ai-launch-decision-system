#!/usr/bin/env python3
"""
War Room Multi-Agent System - REST API
Production-ready FastAPI implementation
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from agents.orchestrator import Orchestrator

load_dotenv()

# Validate configuration
if not os.getenv("LLM_PROVIDER"):
    print("ERROR: LLM_PROVIDER not set in .env file")
    sys.exit(1)

app = FastAPI(
    title="War Room Multi-Agent System",
    description="AI-powered product launch decision system",
    version="1.0.0"
)

# ============== Pydantic Models ==============

class MetricDayInput(BaseModel):
    """Single day of metrics"""
    day: int = Field(..., description="Day number (1-14)")
    dau: float = Field(..., description="Daily Active Users")
    error_rate: float = Field(..., description="Error rate (0-1)")
    latency_p95: float = Field(..., description="95th percentile latency in ms")
    adoption_rate: float = Field(..., description="Feature adoption rate (0-1)")
    crash_rate: float = Field(..., description="Crash rate (0-1)")
    support_tickets: int = Field(..., description="Number of support tickets")

class MetricsInput(BaseModel):
    """Complete metrics dataset"""
    feature: str = Field(..., description="Feature name")
    launch_day: int = Field(..., description="Day of launch (1-14)")
    days: List[MetricDayInput] = Field(..., min_items=7, max_items=14)

class FeedbackInput(BaseModel):
    """Single user feedback entry"""
    text: str = Field(..., min_length=3, max_length=500)
    sentiment: str = Field(..., pattern="^(positive|negative|neutral)$")
    date: str = Field(..., pattern="^\\d{4}-\\d{2}-\\d{2}$")

class WarRoomRequest(BaseModel):
    """Complete war room analysis request"""
    metrics: MetricsInput
    feedback: List[FeedbackInput] = Field(..., min_items=20, max_items=50)
    release_notes: str = Field(..., min_length=10)
    
    class Config:
        json_schema_extra = {
            "example": {
                "metrics": {
                    "feature": "AI Recommendations Widget",
                    "launch_day": 8,
                    "days": [
                        {"day": 1, "dau": 12400, "error_rate": 0.008, "latency_p95": 120, 
                         "adoption_rate": 0.0, "crash_rate": 0.001, "support_tickets": 12}
                    ]
                },
                "feedback": [
                    {"text": "App keeps crashing", "sentiment": "negative", "date": "2026-04-09"}
                ],
                "release_notes": "Release v3.2.0 - AI Recommendations Widget..."
            }
        }

class RiskItem(BaseModel):
    """Risk register entry"""
    risk: str
    mitigation: str

class ActionItem(BaseModel):
    """Action plan entry"""
    action: str
    owner: str
    timeline: str

class CommunicationPlan(BaseModel):
    """Communication plan"""
    internal: str
    external: str

class WarRoomResponse(BaseModel):
    """Complete war room analysis response"""
    request_id: str = Field(..., description="Unique request identifier")
    generated_at: str = Field(..., description="ISO timestamp")
    llm_provider: str = Field(..., description="LLM provider used")
    model: str = Field(..., description="Model name")
    decision: str = Field(..., pattern="^(Proceed|Pause|Roll Back)$")
    rationale: str
    risk_register: List[RiskItem]
    action_plan: List[ActionItem]
    communication_plan: CommunicationPlan
    confidence_score: float = Field(..., ge=0, le=1)
    confidence_increase_condition: str
    agent_traces: Optional[List[str]] = Field(default=None, description="Execution traces")

# ============== API Endpoints ==============

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "service": "War Room Multi-Agent System",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "analyze": "/analyze (POST)",
            "health": "/health (GET)",
            "docs": "/docs (GET)"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "llm_provider": os.getenv("LLM_PROVIDER"),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze", response_model=WarRoomResponse)
async def analyze_launch(request: WarRoomRequest):
    """
    Analyze product launch metrics and feedback to produce a go/no-go decision.
    
    The war room simulates a cross-functional team meeting with:
    - Data Analyst: Analyzes metrics and detects anomalies
    - Marketing Agent: Assesses user sentiment
    - PM Agent: Evaluates success criteria
    - Risk Agent: Challenges assumptions
    
    Returns a structured decision with rationale and action plan.
    """
    
    try:
        # Convert Pydantic models to dictionaries
        metrics_dict = {
            "feature": request.metrics.feature,
            "launch_day": request.metrics.launch_day,
            "days": [day.model_dump() for day in request.metrics.days]
        }
        
        feedback_list = [f.model_dump() for f in request.feedback]
        
        # Initialize orchestrator
        orchestrator = Orchestrator()
        
        # Run analysis
        result = orchestrator.run(metrics_dict, feedback_list, request.release_notes)
        
        # Add metadata
        import uuid
        result["request_id"] = str(uuid.uuid4())
        result["generated_at"] = datetime.now().isoformat()
        result["llm_provider"] = os.getenv("LLM_PROVIDER")
        
        if os.getenv("LLM_PROVIDER") == "openai":
            result["model"] = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        else:
            result["model"] = os.getenv("OLLAMA_MODEL", "phi")
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/upload")
async def analyze_from_files(
    metrics_file: UploadFile = File(..., description="metrics.json file"),
    feedback_file: UploadFile = File(..., description="feedback.json file"),
    release_notes_file: UploadFile = File(..., description="release_notes.txt file")
):
    """
    Alternative endpoint that accepts file uploads instead of JSON body.
    Useful for testing with existing data files.
    """
    
    try:
        # Read and parse metrics
        metrics_content = await metrics_file.read()
        metrics_dict = json.loads(metrics_content)
        
        # Read and parse feedback
        feedback_content = await feedback_file.read()
        feedback_list = json.loads(feedback_content)
        
        # Read release notes
        release_notes = (await release_notes_file.read()).decode("utf-8")
        
        # Initialize orchestrator
        orchestrator = Orchestrator()
        
        # Run analysis
        result = orchestrator.run(metrics_dict, feedback_list, release_notes)
        
        # Add metadata
        import uuid
        result["request_id"] = str(uuid.uuid4())
        result["generated_at"] = datetime.now().isoformat()
        result["llm_provider"] = os.getenv("LLM_PROVIDER")
        
        if os.getenv("LLM_PROVIDER") == "openai":
            result["model"] = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        else:
            result["model"] = os.getenv("OLLAMA_MODEL", "phi")
        
        return JSONResponse(content=result)
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# ============== Startup Event ==============

@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    print("=" * 60)
    print("🚀 WAR ROOM MULTI-AGENT API STARTING")
    print("=" * 60)
    print(f"LLM Provider: {os.getenv('LLM_PROVIDER', 'not set').upper()}")
    print(f"Docs available at: http://127.0.0.1:8000/docs")
    print("=" * 60)

# ============== Main Entry Point ==============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
