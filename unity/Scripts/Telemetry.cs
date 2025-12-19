using System;
using UnityEngine; // For Vector3/Quaternion if possible? 
// Actually standard System classes don't have Vector3 easily serializable by Unity JSON without tricks.
// We'll stick to simple arrays or floats for compatibility.

[Serializable]
public class Telemetry
{
    public float t;
    public float x1;
    public float x2;
    public float x3;
    public float y1;
    public float y2;
    public float unc;
    public float[] joints; // [q1, q2, q3]
    public float gripper;  // 0.0 (Open) to 1.0 (Closed)
    
    // Box / Cargo Info
    public float[] boxPos; // [x, y, z]
    public float[] boxRot; // [x, y, z, w]
    
    public string meta;
}