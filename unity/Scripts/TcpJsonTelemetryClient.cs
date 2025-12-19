using System;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class TcpJsonTelemetryClient : MonoBehaviour
{
    [Header("TCP server (Python)")]
    public string host = "127.0.0.1";
    public int port = 5555;

    [Header("Target to animate")]
    public Transform target;
    public float positionScale = 2.0f;

    [Header("Visualization")]
    public bool visualizeVelocity = true;
    public float maxVelocity = 1.5f; // Velocity at which color is fully red/blue
    public Transform uncertaintyGhost; // Assign a semi-transparent sphere here
    public float uncertaintyScale = 5.0f;

    [Header("Debug")]
    public bool logMessages = false;

    private TcpClient _client;
    private NetworkStream _stream;
    private Thread _thread;
    private volatile bool _running;

    private readonly object _lock = new object();
    private Telemetry _latest = null;

    void Start()
    {
        if (target == null) target = this.transform;
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
                _latest = null; // consume
            }
        }

        if (copy != null)
        {
            // 1. Position
            var p = target.position;
            p.x = copy.x1 * positionScale;
            target.position = p;

            // 2. Velocity Color (Blue = -Max, Red = +Max, Green/White = 0?)
            // Let's do simple Blue (slow) to Red (fast) based on magnitude, 
            // OR Blue (negative) to Red (positive). Let's do Neg->Pos.
            if (visualizeVelocity)
            {
                var rend = target.GetComponent<Renderer>();
                if (rend != null)
                {
                    float t = Mathf.InverseLerp(-maxVelocity, maxVelocity, copy.x2);
                    rend.material.color = Color.Lerp(Color.blue, Color.red, t);
                }
            }

            // 3. Uncertainty Ghost
            if (uncertaintyGhost != null)
            {
                uncertaintyGhost.position = p;
                // Scale based on uncertainty (trace of P)
                // We add a base size so it doesn't disappear completely
                float s = copy.unc * uncertaintyScale;
                uncertaintyGhost.localScale = Vector3.one * s;
            }

            if (logMessages)
            {
                Debug.Log($"t={copy.t:F3} x1={copy.x1:F3} unc={copy.unc:F3}");
            }
        }
    }

    private void Worker()
    {
        // Re-connection logic
        while (_running)
        {
            try
            {
                _client = new TcpClient();
                _client.NoDelay = true;
                // Timeout if connection fails so we can retry
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
                // Connection error, wait and retry
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