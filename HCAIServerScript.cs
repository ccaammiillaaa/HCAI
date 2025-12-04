using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using UnityEngine;


public class HCAIServerScript : MonoBehaviour //defines Unity scrpipt class, inherits from MonoBehaviour
{
    TcpListener server = null; //wait for client to connect
    TcpClient client = null; //represents the connected device
    NetworkStream stream = null; //used to read/write massages
    Thread Thread; //runs the server in the background

    public int connectionPort = 25001;
    public string myLLM_Answer = "0"; //strin to hold the LLM answer, latest received message
    
    // Queue for thread-safe communication
    private Queue<int> objectIdQueue = new Queue<int>();
    private object queueLock = new object();

    private void Start() 
    {
        Thread = new Thread(new ThreadStart(SetupServer));
        Thread.Start(); 
        ObjectManager.Instance.ShowObject(0);
        
        // Wait one frame to ensure ObjectManager.Awake() has run
        //StartCoroutine(DelayedStart());
    }

    private void Update() //Unity calls every frame, here it is empty - should this be changed?
    {
        // Process queued object IDs on the main thread
        lock (queueLock)
        {
            while (objectIdQueue.Count > 0)
            {
                int objectId = objectIdQueue.Dequeue();
                ObjectManager.Instance.ShowObject(objectId);
                Debug.Log("Showing object ID: " + objectId);
            }
        }
    }

    // ADD THESE TWO METHODS HERE - for recording button
    public void OnRecordButtonPressed()
    {
        SendMessageToClient("speechstart");
        Debug.Log("🎤 Recording started...");
        
        // Wait 5 seconds, then tell Python to stop and transcribe
        StartCoroutine(StopRecordingAfterDelay(5f));
    }

    private IEnumerator StopRecordingAfterDelay(float delay)
    {
        yield return new WaitForSeconds(delay);
        SendMessageToClient("speechstop");
        Debug.Log("⏹️ Recording stopped, waiting for classification...");
    }

    private void SetupServer() //method that contains server logic, it will run on the thread created earlier
    {
        try
        {
            //create the server
            server = new TcpListener(IPAddress.Any, connectionPort);
            server.Start();

            byte[] buffer = new byte[2048]; //creates a byte array of size 2048 to hold incoming data
            string data = null; //string to hold decoded text, starts as null

            while (true) //loop to continuously listen for client connections
            {
                Debug.Log("Waiting for connection..."); //to indicate server is waiting
                client = server.AcceptTcpClient();
                Debug.Log("Connected!"); //indicates a client has connected

                data = null; //reset data to null
                stream = client.GetStream();

                int i; //variable to hold number of bytes read
                while ((i = stream.Read(buffer, 0, buffer.Length)) != 0)
                {
                    data = Encoding.UTF8.GetString(buffer, 0, i);
                    Debug.Log("Received: " + data);
                    myLLM_Answer = data;
                    
                    // Map category string to object ID
                    int objectId = MapCategoryToId(data);
                    
                    // Queue the object ID to be processed on main thread
                    lock (queueLock)
                    {
                        objectIdQueue.Enqueue(objectId);
                    }
                }
                client.Close();
                 Debug.Log("client closed!");
            }
        }
        catch (SocketException e)
        {
            Debug.Log("SocketException: " + e);
        }
        finally
        {
            server.Stop();
        }
    }

    public void SendMessageToClient(string message)
    {
        byte[] msg = Encoding.UTF8.GetBytes(message);
        stream.Write(msg, 0, msg.Length);
        Debug.Log("Sent: " + message);
    }

    private void OnApplicationQuit()
    {
        try
        {
            if (stream != null && client != null && client.Connected)
            {
                SendMessageToClient("stop");
            }
        }
        catch (Exception e)
        {
            Debug.Log("Error during quit: " + e.Message);
        }
        finally
        {
            stream?.Close();
            client?.Close();
            server?.Stop();
            Thread?.Abort();
            Debug.Log("onApplicationQuit executed");
        }
    }

    // Add this new method
    private int MapCategoryToId(string category)
    {
        category = category.Trim(); // Remove whitespace
        
        if (category.Contains("Train"))
            return 1;
        else if (category.Contains("Teddy Bear"))
            return 2;
        else if (category.Contains("Robot"))
            return 3;
        else if (category.Contains("Could not understand"))
            return 0; // Hide all objects
        else
            return 0; // Default: hide all
    }
}


// using System;
// using System.Net.Sockets;
// using System.Text;
// using System.Threading;
// using UnityEngine;

// public class HCAIServerScript : MonoBehaviour
// {
//     private TcpClient client;
//     private NetworkStream stream;

//     public string host = "127.0.0.1";
//     public int port = 25001;
    
//     void Start()
//     {
//         ConnectToPython();
//     }

//     void ConnectToPython()
//     {
//         try
//         {
//             client = new TcpClient(host, port);
//             stream = client.GetStream();
//             Debug.Log("🟢 Connected to Python server!");
//         }
//         catch (Exception e)
//         {
//             Debug.LogError("❌ Could not connect to Python: " + e.Message);
//         }
//     }

//     void OnApplicationQuit()
//     {
//         stream?.Close();
//         client?.Close();
//     }

//     public void SendUserInput(string text)
//     {
//         if (client == null || !client.Connected)
//         {
//             Debug.LogWarning("⚠️ Not connected to Python.");
//             return;
//         }

//         byte[] data = Encoding.UTF8.GetBytes(text + "\n");
//         stream.Write(data, 0, data.Length);

//         // Receive response
//         byte[] buffer = new byte[1024];
//         int length = stream.Read(buffer, 0, buffer.Length);

//         string response = Encoding.UTF8.GetString(buffer, 0, length);
//         Debug.Log("📥 Python responded: " + response);

//         // Split into gameplay + text parts
//         string[] parts = response.Split('|');
//         string command = parts[0];
//         string santaText = parts.Length > 1 ? parts[1] : "";

//         // For now, just log it
//         Debug.Log("🎮 Command: " + command);
//         Debug.Log("🎅 Santa says: " + santaText);

//         // TODO: later -> call prefab spawn code
//         // TODO: later -> update UI TextMeshPro
//     }
// }

//dummy test
//IEnumerator DelayedStart()
//    {
//        yield return null; // Wait one frame
//        StartCoroutine(TestObjectLoop());
//    }

//    IEnumerator TestObjectLoop()
//    {
//        Debug.Log("Starting test loop...");
//
//        for (int i = 0; i < 10; i++)
//        {
  //          int fakeMessage = (i % 3) + 1;  // 1,2,3 repeating
//
  //          Debug.Log("TEST: Simulating LLM answer: " + fakeMessage);
//
  //          ObjectManager.Instance.ShowObject(fakeMessage);
//
  //          yield return new WaitForSeconds(1f);
    //    }
//
  //      Debug.Log("Test loop complete!");
    //}