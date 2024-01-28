using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

public class Management : MonoBehaviour
{
    [SerializeField] public GameObject chairPosition;
    [SerializeField] public GameObject player;

    [SerializeField] public UI_Manager uiManager;
    
    
    public void StartInterview(string company, int amountOfQuestions, string interviewer)
    {
        Debug.Log("Begin Interview");
    }

    public void FinishInterview()
    {
        uiManager.ResetUI();
        player.transform.position = new Vector3(0,0,0);

        
    }
    
    public void QuitGame()
    {
        Application.Quit();
    }
}
