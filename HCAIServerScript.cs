using System;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class HCAIServerScript : MonoBehaviour
{
    private TcpClient client;
    private NetworkStream stream;

    public string host = "127.0.0.1";
    public int port = 25001;
    
    void Start()
    {
        ConnectToPython();
    }

    void ConnectToPython()
    {
        try
        {
            client = new TcpClient(host, port);
            stream = client.GetStream();
            Debug.Log("🟢 Connected to Python server!");
        }
        catch (Exception e)
        {
            Debug.LogError("❌ Could not connect to Python: " + e.Message);
        }
    }

    void OnApplicationQuit()
    {
        stream?.Close();
        client?.Close();
    }

    public void SendUserInput(string text)
    {
        if (client == null || !client.Connected)
        {
            Debug.LogWarning("⚠️ Not connected to Python.");
            return;
        }

        byte[] data = Encoding.UTF8.GetBytes(text + "\n");
        stream.Write(data, 0, data.Length);

        // Receive response
        byte[] buffer = new byte[1024];
        int length = stream.Read(buffer, 0, buffer.Length);

        string response = Encoding.UTF8.GetString(buffer, 0, length);
        Debug.Log("📥 Python responded: " + response);

        // Split into gameplay + text parts
        string[] parts = response.Split('|');
        string command = parts[0];
        string santaText = parts.Length > 1 ? parts[1] : "";

        // For now, just log it
        Debug.Log("🎮 Command: " + command);
        Debug.Log("🎅 Santa says: " + santaText);

        // TODO: later -> call prefab spawn code
        // TODO: later -> update UI TextMeshPro
    }
}
