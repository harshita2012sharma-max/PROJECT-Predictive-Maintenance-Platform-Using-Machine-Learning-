import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import ALERT_THRESHOLDS

def check_alert(failure_probability, days_remaining):
    """
    Determine alert level based on failure probability and remaining useful life.
    Uses weighted logic: probability is primary indicator, days is secondary.
    
    Returns: "CRITICAL", "HIGH", or "NORMAL"
    """
    
    if (
        failure_probability >= ALERT_THRESHOLDS["critical_prob"]
        and days_remaining <= ALERT_THRESHOLDS["critical_days"]
    ):
        return "CRITICAL"
    
    if failure_probability >= 0.85:
        return "CRITICAL"
    
    if failure_probability >= ALERT_THRESHOLDS["high_prob"]:
        return "HIGH"
    
    if days_remaining <= ALERT_THRESHOLDS["high_days"] and failure_probability >= 0.25:
        return "HIGH"
    
    
    return "NORMAL"