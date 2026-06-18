import requests
import logging
from typing import Dict, Any, Optional

# --- ENTERPRISE LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
# Ensure these match your FastAPI running instance
BASE_URL = "http://127.0.0.1:8000/api/v1"
HEALTH_URL = "http://127.0.0.1:8000/health"

def predict_churn(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Sends customer data to the FastAPI ML Inference Engine.
    Returns the JSON response (prediction results) or None on failure.
    """
    try:
        logger.info(f"Sending inference request to {BASE_URL}/churn/predict")
        
        response = requests.post(
            f"{BASE_URL}/churn/predict", 
            json=payload, 
            timeout=12  # Slightly longer timeout for ML models
        )
        
        # Log status for debugging
        if response.status_code == 200:
            logger.info("Prediction successful.")
            return response.json()
        
        elif response.status_code == 422:
            logger.error(f"Validation Error (422): Check input fields. {response.text}")
        elif response.status_code == 500:
            logger.error(f"Server Error (500): ML Model or Backend crashed. {response.text}")
        else:
            logger.error(f"Unexpected Error ({response.status_code}): {response.text}")
            
        return None

    except requests.exceptions.Timeout:
        logger.error("Request Timeout: The ML model is taking too long to respond.")
        return None
    except requests.exceptions.ConnectionError:
        logger.error("Connection Error: FastAPI backend appears to be offline.")
        return None
    except Exception as e:
        logger.error(f"Inference Exception: {str(e)}")
        return None

def fetch_health() -> Dict[str, Any]:
    """
    Queries the system health status. 
    Provides a standardized fallback object to prevent Streamlit crashes.
    """
    fallback_offline = {
        "status": "offline", 
        "components": {"database": "down", "redis": "down"}
    }
    
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        
        logger.warning(f"Health check returned degraded status: {response.status_code}")
        return {
            "status": "degraded", 
            "components": {"database": "unknown", "redis": "unknown"}
        }

    except requests.exceptions.RequestException:
        # Silently handle offline status for health checks to keep UI clean
        return fallback_offline
    except Exception as e:
        logger.error(f"Health check exception: {str(e)}")
        return fallback_offline