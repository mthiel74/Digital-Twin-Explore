using System;

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
    public float[] joints; // [q1, q2]
    public float gripper;  // 0.0 (Open) to 1.0 (Closed)
    public string meta;
}
