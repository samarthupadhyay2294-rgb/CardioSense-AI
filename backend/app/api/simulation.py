from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ecg_simulation import ecg_simulator
from app.services.ecg_service import compute_signal_quality, compute_ecg_statistics
from app.ml.predictor import predictor
import numpy as np

router = APIRouter(tags=["simulation"])


class SimulationParams(BaseModel):
    abnormality: str = "normal"
    heart_rate: float = 70.0
    noise_level: float = 0.0
    baseline_wander: bool = False
    duration: float = 10.0


@router.post("/api/simulation/generate")
async def generate_ecg(params: SimulationParams):
    """
    Generate simulated ECG signal.
    
    NOTE: Generated signals are for educational/research purposes only.
    They are NOT real patient recordings and should NOT be used for clinical diagnosis.
    """
    try:
        signal = ecg_simulator.generate_custom_ecg(params.dict())
        
        # Convert to serializable format
        signal_data = signal.tolist()
        
        return {
            "success": True,
            "signal": signal_data,
            "parameters": params.dict(),
            "metadata": {
                "sampling_rate": ecg_simulator.sampling_rate,
                "duration": ecg_simulator.duration,
                "num_leads": 12,
                "num_samples": signal.shape[1],
                "lead_names": ecg_simulator.lead_names,
                "disclaimer": "This is a simulated ECG signal for educational/research purposes only. Not a real patient recording."
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/api/simulation/generate-and-analyze")
async def generate_and_analyze(params: SimulationParams):
    """
    Generate simulated ECG and analyze it through the existing pipeline.
    
    NOTE: This is for educational/research purposes only.
    AI predictions should not replace qualified medical interpretation.
    """
    try:
        signal = ecg_simulator.generate_custom_ecg(params.dict())
        
        # Process through existing pipeline
        prediction = predictor.predict(signal)
        signal_quality = compute_signal_quality(signal)
        ecg_statistics = compute_ecg_statistics(signal)
        
        # Downsample signal for display
        from app.services.ecg_service import downsample_signal
        signal_data = downsample_signal(signal, target_points=500)
        
        return {
            "success": True,
            "prediction": prediction,
            "signal_quality": signal_quality,
            "ecg_statistics": ecg_statistics,
            "signal_data": signal_data,
            "parameters": params.dict(),
            "metadata": {
                "sampling_rate": ecg_simulator.sampling_rate,
                "duration": ecg_simulator.duration,
                "num_leads": 12,
                "num_samples": signal.shape[1],
                "lead_names": ecg_simulator.lead_names,
                "disclaimer": "This is a simulated ECG signal for educational/research purposes only. Not a real patient recording."
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")