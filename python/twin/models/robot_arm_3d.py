import numpy as np
import math
from dataclasses import dataclass
from typing import Optional, Dict, Tuple

@dataclass
class Arm3DParams:
    l1: float = 1.5  # Length of upper arm
    l2: float = 1.5  # Length of forearm
    # Base height offset (Unity: 0.2 (Base) + 0.4 (Turret offset) = 0.6)
    base_h: float = 0.6 

def inverse_kinematics(target: np.ndarray, p: Arm3DParams) -> np.ndarray:
    """
    Geometric IK for a 3-DOF Arm (Waist, Shoulder, Elbow).
    Target: [x, y, z]
    Returns: [q1, q2, q3] (radians)
    """
    x, y, z = target
    
    # 1. Waist Angle (q1) - Rotation around Y
    # target in horizontal plane
    q1 = math.atan2(x, z) # Assuming Z is forward in Unity, X is right
    
    # 2. Planar problem for Shoulder/Elbow
    # Project target onto the plane defined by q1
    # r is horizontal distance to target
    r = math.sqrt(x**2 + z**2)
    
    # Height relative to shoulder axis
    h = y - p.base_h
    
    # Distance from shoulder to target
    d_sq = r**2 + h**2
    d = math.sqrt(d_sq)
    
    # Clamp reach
    max_reach = p.l1 + p.l2
    if d > max_reach * 0.99:
        d = max_reach * 0.99
        d_sq = d**2
        
    # Law of Cosines for Elbow (q3)
    # c3 = (d^2 - l1^2 - l2^2) / (2 * l1 * l2)
    # We want "elbow up" usually, or "elbow down".
    # Angle *at* the elbow inside the triangle
    cos_angle_elbow = (p.l1**2 + p.l2**2 - d_sq) / (2 * p.l1 * p.l2)
    # Safety clamp
    cos_angle_elbow = max(-1.0, min(1.0, cos_angle_elbow))
    angle_elbow_internal = math.acos(cos_angle_elbow)
    
    # q3 (deviation from straight line). 
    # If arm is straight, q3=0. internal=180.
    # Standard convention: q3=0 is bent 90? Let's use:
    # q3 = 0 means fully extended? No, let's say q3 is angle relative to link 1.
    q3 = -(math.pi - angle_elbow_internal) # Elbow flexes "up/in"
    
    # Law of Cosines for Shoulder (q2)
    # Angle between horizontal (r-axis) and l1
    # alpha = atan2(h, r)
    # beta = angle inside triangle at shoulder
    # cos_beta = (l1^2 + d^2 - l2^2) / (2 * l1 * d)
    alpha = math.atan2(h, r)
    cos_beta = (p.l1**2 + d_sq - p.l2**2) / (2 * p.l1 * d)
    cos_beta = max(-1.0, min(1.0, cos_beta))
    beta = math.acos(cos_beta)
    
    q2 = alpha + beta # Shoulder up
    
    return np.array([q1, q2, q3])

def forward_kinematics(q: np.ndarray, p: Arm3DParams) -> np.ndarray:
    """Returns [x, y, z] of end effector."""
    q1, q2, q3 = q
    
    # Planar components (in the vertical plane rotated by q1)
    # Shoulder is at (0, base_h, 0) relative to q1 plane origin
    # r is horizontal dist from axis
    # y is vertical
    
    # Link 1 tip (relative to shoulder)
    r1 = p.l1 * math.cos(q2)
    y1 = p.l1 * math.sin(q2)
    
    # Link 2 tip (relative to Link 1 tip)
    # angle is q2 + q3
    r2 = p.l2 * math.cos(q2 + q3)
    y2 = p.l2 * math.sin(q2 + q3)
    
    r_total = r1 + r2
    y_total = p.base_h + y1 + y2
    
    # Rotate by q1
    x = r_total * math.sin(q1)
    z = r_total * math.cos(q1)
    
    return np.array([x, y_total, z])
