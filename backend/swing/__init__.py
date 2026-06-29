"""Real biomechanical swing analysis (MediaPipe pose -> features -> diagnosis).

Public entry point: `from swing import analyze_swing_real`.
Importing this package may fail if mediapipe/opencv are unavailable — callers
should catch that and fall back to the mock analyzer.
"""
from .analyzer import analyze_swing_real

__all__ = ["analyze_swing_real"]
