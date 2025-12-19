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
            // Minimal visual: map x1 to x-position.
            var p = target.position;
            p.x = copy.x1 * positionScale;
            target.position = p;

            if (logMessages)
            {
                Debug.Log($"t={copy.t:F3} x1={copy.x1:F3} x2={copy.x2:F3} x3={copy.x3:F3} meta={copy.meta}");
            }
        }
    }

    private void Worker()
    {
        try
        {
            _client = new TcpClient();
            _client.NoDelay = true;
            _client.Connect(host, port);
            _stream = _client.GetStream();

            var buffer = new byte[8192];
            var sb = new StringBuilder();

            while (_running)
            {
                if (!_stream.DataAvailable)
                {
                    Thread.Sleep(5);
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
                        // Ignore malformed lines
                    }
                }
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"TCP telemetry client error: {e.Message}");
        }
        finally
        {
            try { _stream?.Close(); } catch { }
            try { _client?.Close(); } catch { }
        }
    }
}
