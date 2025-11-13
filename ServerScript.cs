using System;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

public class ServerScript : MonoBehaviour
{
    void Start()
    {
        // ping test
        PingPythonServer();
    }

    void PingPythonServer()
    {
        try
        {
            //connect to the Python server
            using (TcpClient client = new TcpClient("127.0.0.1", 5000))
            {
                NetworkStream stream = client.GetStream();

                //send simple ping message
                string message = "Hello from Unity!";
                byte[] data = Encoding.UTF8.GetBytes(message);
                stream.Write(data, 0, data.Length);
                Debug.Log("Sent to Python server: " + message);

                //wait for response
                byte[] buffer = new byte[1024];
                int bytes = stream.Read(buffer, 0, buffer.Length);
                string response = Encoding.UTF8.GetString(buffer, 0, bytes);

                Debug.Log("Received from Python server: " + response);

                stream.Close();
            }
        }
        catch (Exception e)
        {
            Debug.LogError("Error communicating with Python server: " + e.Message);
        }
    }    
}