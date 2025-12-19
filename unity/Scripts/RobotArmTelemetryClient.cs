using System;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class RobotArmTelemetryClient : MonoBehaviour
{
    [Header("TCP Connection")]
    public string host = "127.0.0.1";
    public int port = 5555;

    [Header("Arm Joints")]
    public Transform joint1; // Base Turret (Rotates Y)
    public Transform joint2; // Shoulder (Rotates X)
    public Transform joint3; // Elbow (Rotates X)
    
    [Header("Configuration")]
    // Defaults for 3D arm
    public Vector3 axis1 = Vector3.up; 
    public Vector3 axis2 = Vector3.right;
    public Vector3 axis3 = Vector3.right;
    
    public float offset1Degrees = 0f;
    public float offset2Degrees = 0f;
    public float offset3Degrees = 0f;

    [Header("Gripper")]
    public Transform finger1;
    public Transform finger2;
    public float gripperOpenOffset = 0.08f;
    public float gripperClosedOffset = 0.02f;
    
    [Header("Cargo")]
    public Transform cargo;

    private TcpClient _client;
    private NetworkStream _stream;
    private Thread _thread;
    private volatile bool _running;
    private readonly object _lock = new object();
    private Telemetry _latest = null;

    void Start()
    {
        if (cargo == null) {
             GameObject c = GameObject.Find("CargoBox");
             if (c != null) cargo = c.transform;
        }
        
        _running = true;
        _thread = new Thread(Worker);
        _thread.IsBackground = true;
        _thread.Start();
    }

    void OnDestroy()
    {
        _running = false;
        try { _stream?.Close(); } catch { }
        try { _client?.Close(); } catch { }
        try { _thread?.Join(500); } catch { }
    }

    void Update()
    {
        Telemetry copy = null;
        lock (_lock)
        {
            if (_latest != null)
            {
                copy = _latest;
                _latest = null;
            }
        }

        if (copy != null)
        {
            // Joints
            if (copy.joints != null)
            {
                if (joint1 != null && copy.joints.Length >= 1)
                    joint1.localRotation = Quaternion.AngleAxis(copy.joints[0] * Mathf.Rad2Deg + offset1Degrees, axis1);
                
                if (joint2 != null && copy.joints.Length >= 2)
                    joint2.localRotation = Quaternion.AngleAxis(copy.joints[1] * Mathf.Rad2Deg + offset2Degrees, axis2);
                    
                if (joint3 != null && copy.joints.Length >= 3)
                    joint3.localRotation = Quaternion.AngleAxis(copy.joints[2] * Mathf.Rad2Deg + offset3Degrees, axis3);
            }
            
            // Gripper
            if (finger1 != null && finger2 != null)
            {
                float t = Mathf.Clamp01(copy.gripper);
                float pos = Mathf.Lerp(gripperOpenOffset, gripperClosedOffset, t);
                
                // Assuming Fingers move along X
                finger1.localPosition = new Vector3(pos, 0, 0);
                finger2.localPosition = new Vector3(-pos, 0, 0);
            }
            
            // Cargo
            if (cargo != null && copy.boxPos != null && copy.boxPos.Length >= 3)
            {
                cargo.position = new Vector3(copy.boxPos[0], copy.boxPos[1], copy.boxPos[2]);
                if (copy.boxRot != null && copy.boxRot.Length >= 4)
                {
                    cargo.rotation = new Quaternion(copy.boxRot[0], copy.boxRot[1], copy.boxRot[2], copy.boxRot[3]);
                }
            }
        }
    }

    private void Worker()
    {
        while (_running)
        {
            try
            {
                _client = new TcpClient();
                _client.NoDelay = true;
                var result = _client.BeginConnect(host, port, null, null);
                var success = result.AsyncWaitHandle.WaitOne(TimeSpan.FromSeconds(1));

                if (!success)
                {
                    _client.Close();
                    Thread.Sleep(1000);
                    continue;
                }
                _client.EndConnect(result);
                _stream = _client.GetStream();

                var buffer = new byte[8192];
                var sb = new StringBuilder();

                while (_running && _client.Connected)
                {
                    if (!_stream.DataAvailable)
                    {
                        Thread.Sleep(1);
                        continue;
                    }

                    int n = _stream.Read(buffer, 0, buffer.Length);
                    if (n <= 0) break;

                    sb.Append(Encoding.UTF8.GetString(buffer, 0, n));

                    while (true)
                    {
                        var s = sb.ToString();
                        int idx = s.IndexOf('\n');
                        if (idx < 0) break;

                        string line = s.Substring(0, idx).Trim();
                        sb.Remove(0, idx + 1);

                        if (line.Length == 0) continue;

                        try
                        {
                            var msg = JsonUtility.FromJson<Telemetry>(line);
                            lock (_lock) { _latest = msg; }
                        }
                        catch (Exception)
                        {
                            // Ignore
                        }
                    }
                }
            }
            catch (Exception)
            {
                Thread.Sleep(1000);
            }
            finally
            {
                try { _stream?.Close(); } catch { }
                try { _client?.Close(); } catch { }
            }
        }
    }
}