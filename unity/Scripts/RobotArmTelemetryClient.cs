using System;
using System.Collections.Generic;
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
    public Transform joint1; // Base/Shoulder
    public Transform joint2; // Elbow
    
    [Header("Configuration")]
    public Vector3 axis1 = Vector3.forward; // Rotate around Z for 2D planar
    public Vector3 axis2 = Vector3.forward;
    public float offset1Degrees = 0f;
    public float offset2Degrees = 0f;

    private TcpClient _client;
    private NetworkStream _stream;
    private Thread _thread;
    private volatile bool _running;
    private readonly object _lock = new object();
    private Telemetry _latest = null;

    void Start()
    {
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

        if (copy != null && copy.joints != null && copy.joints.Length >= 2)
        {
            // Apply rotations
            // Note: Ensure your Unity hierarchy is correct (Joint2 is child of Joint1's visual end, etc.)
            if (joint1 != null)
            {
                float angle = copy.joints[0] * Mathf.Rad2Deg + offset1Degrees;
                joint1.localRotation = Quaternion.AngleAxis(angle, axis1);
            }
            
            if (joint2 != null)
            {
                float angle = copy.joints[1] * Mathf.Rad2Deg + offset2Degrees;
                joint2.localRotation = Quaternion.AngleAxis(angle, axis2);
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
                            // Ignore malformed
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
