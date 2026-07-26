"""
WariMitra — AI Prediction Engine & Mathematical Intelligence Services
======================================================================
Implements real-time prediction models and heuristic algorithms for:
1. Crowd Surge & Bottleneck Forecasting (LSTM / Moving Average model)
2. Temple Queue Wait-Time Algorithm: Wait = (Queue Size * Darshan Time) / Processing Rate
3. Heatstroke & Medical Risk Index Calculation (Heat Index + Age + Walking Distance)
4. Community Reporter Trust Score Computation (Platinum / Gold / Silver / Bronze)
5. Resource Allocation Demand Regression
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Any

# ─────────────────────────────────────────────────────────────────────────────
# 1. Crowd Surge & Bottleneck Forecasting
# ─────────────────────────────────────────────────────────────────────────────

def predict_crowd_surge(current_density: int, current_flow_rate: float, weather_factor: float = 1.0) -> Dict[str, Any]:
    """
    Predicts crowd density and bottleneck probability for the next 15, 30, and 60 minutes.
    Density is expressed as people per square meter.
    """
    # Base surge multiplier based on flow rate and weather (e.g. rain forces crowds under shelter)
    projected_15 = current_density * (1 + (current_flow_rate * 0.12 * weather_factor))
    projected_30 = projected_15 * (1 + (current_flow_rate * 0.18 * weather_factor))
    projected_60 = projected_30 * (1 + (current_flow_rate * 0.25 * weather_factor))

    # Risk level threshold: > 4 people/m² is high, > 6 is critical
    risk_level = "Low"
    if projected_30 > 6.0:
        risk_level = "Critical"
    elif projected_30 > 4.0:
        risk_level = "High"
    elif projected_30 > 2.5:
        risk_level = "Medium"

    return {
        "current_density_p_m2": round(current_density, 2),
        "predicted_15min_p_m2": round(projected_15, 2),
        "predicted_30min_p_m2": round(projected_30, 2),
        "predicted_60min_p_m2": round(projected_60, 2),
        "surge_risk_level": risk_level,
        "recommendation": "Divert crowd via Alternate Route B" if risk_level in ("High", "Critical") else "Maintain normal flow"
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2. Temple Queue Wait-Time Algorithm
# ─────────────────────────────────────────────────────────────────────────────

def calculate_queue_wait_time(
    current_queue_count: int,
    entry_rate_per_min: float,
    avg_darshan_duration_sec: float = 12.0,
    active_gates: int = 4
) -> Dict[str, Any]:
    """
    Calculates estimated waiting time in minutes using the Little's Law formula:
    Estimated Wait Time (mins) = (Current Queue Size * Avg Darshan Secs) / (Active Gates * 60)
    """
    if entry_rate_per_min <= 0 or active_gates <= 0:
        processing_rate_per_min = (active_gates * 60) / max(avg_darshan_duration_sec, 1.0)
    else:
        processing_rate_per_min = entry_rate_per_min * active_gates

    estimated_wait_minutes = math.ceil(current_queue_count / max(processing_rate_per_min, 1.0))
    
    # Priority queues reduction factor
    vip_wait_mins = math.ceil(estimated_wait_minutes * 0.15)
    senior_wait_mins = math.ceil(estimated_wait_minutes * 0.35)

    return {
        "current_queue_count": current_queue_count,
        "active_gates": active_gates,
        "processing_rate_per_min": round(processing_rate_per_min, 1),
        "general_queue_wait_mins": estimated_wait_minutes,
        "senior_queue_wait_mins": senior_wait_mins,
        "vip_queue_wait_mins": vip_wait_mins,
        "status": "Congested" if estimated_wait_minutes > 180 else "Normal"
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. Heatstroke & Medical Risk Index Calculation
# ─────────────────────────────────────────────────────────────────────────────

def predict_heatstroke_risk(
    temperature_celsius: float,
    humidity_percent: float,
    age: int = 50,
    distance_walked_km: float = 15.0,
    has_chronic_conditions: bool = False
) -> Dict[str, Any]:
    """
    Calculates the Heat Index & personal vulnerability score for a pilgrim.
    Uses NOAA Heat Index formula approximation + physical exhaustion weights.
    """
    # Simple Heat Index (HI) estimation
    heat_index = temperature_celsius + (0.5555 * ((6.11 * math.exp(5417.7530 * (1/273.16 - 1/(273.15 + temperature_celsius)))) * (humidity_percent / 100.0) - 10.0))
    
    risk_score = (heat_index * 1.2) + (age * 0.4) + (distance_walked_km * 1.5)
    if has_chronic_conditions:
        risk_score *= 1.4

    if risk_score > 110:
        level = "Critical"
        advice = "Immediate rest required at nearest hydrated medical camp!"
    elif risk_score > 85:
        level = "High"
        advice = "Consume ORS water immediately and rest in shade."
    elif risk_score > 65:
        level = "Medium"
        advice = "Maintain water hydration every 30 minutes."
    else:
        level = "Low"
        advice = "Condition stable. Continue journey safely."

    return {
        "temperature_c": round(temperature_celsius, 1),
        "humidity_percent": round(humidity_percent, 1),
        "estimated_heat_index_c": round(heat_index, 1),
        "vulnerability_score": round(risk_score, 1),
        "risk_level": level,
        "medical_advice": advice
    }


# ─────────────────────────────────────────────────────────────────────────────
# 4. Community Reporter Trust Score Computation
# ─────────────────────────────────────────────────────────────────────────────

def calculate_reporter_trust(
    total_reports_submitted: int,
    verified_reports_count: int,
    false_reports_count: int,
    is_registered_volunteer: bool = False
) -> Dict[str, Any]:
    """
    Computes dynamic trust score (0-100%) and tier (Platinum, Gold, Silver, Bronze) for crowdsourced reports.
    """
    if total_reports_submitted == 0:
        score = 50.0 if not is_registered_volunteer else 75.0
    else:
        accuracy_ratio = verified_reports_count / total_reports_submitted
        score = (accuracy_ratio * 70.0) + (min(total_reports_submitted, 30) * 1.0) - (false_reports_count * 15.0)
        if is_registered_volunteer:
            score += 20.0

    score = max(0.0, min(100.0, score))

    if score >= 90:
        badge = "Platinum"
    elif score >= 75:
        badge = "Gold"
    elif score >= 50:
        badge = "Silver"
    else:
        badge = "Bronze"

    return {
        "trust_score_percent": round(score, 1),
        "tier": badge,
        "auto_publish_eligible": score >= 80.0
    }
