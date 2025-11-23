using System;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

public class ServerScript : MonoBehaviour
{
    TcpClient client;
    NetworkStream stream;

    void Start()
    {
        ConnectToPython();
    }

    void OnApplicationQuit()
    {
        stream?.Close();
        client?.Close();
    }

    void ConnectToPython()
    {
        try
        {
            client = new TcpClient("127.0.0.1", 65432);
            stream = client.GetStream();
            Debug.Log("🟢 Connected to Python server!");
        }
        catch (Exception e)
        {
            Debug.LogError("❌ Could not connect to Python: " + e.Message);
        }
    }

    public void SendUserInput(string text)
    {
        if (client == null || !client.Connected)
        {
            Debug.LogWarning("⚠️ Not connected to Python.");
            return;
        }

        byte[] data = Encoding.UTF8.GetBytes(text);
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