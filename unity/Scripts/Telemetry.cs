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
    public float[] joints; // Joint angles [q1, q2, ...]
    public string meta;
}
