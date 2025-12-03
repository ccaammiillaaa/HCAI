using UnityEngine;


public class ObjectManager : MonoBehaviour
{
    public static ObjectManager Instance;

    public GameObject train;
    public GameObject teddy;
    public GameObject robot;

    void Awake() => Instance = this;

    public void ShowObject(int id)
    {
        train.SetActive(id == 1);
        teddy.SetActive(id == 2);
        robot.SetActive(id == 3);
    }
}