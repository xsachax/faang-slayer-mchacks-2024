using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

public class UI_Manager : MonoBehaviour
{
    [SerializeField] GameObject[] pages;
    private string selectedCompany = "";
    private int amountOfQuestions = 0;
    private string chosenInterviewer = "";
    
    [SerializeField] Slider slider;

    private Management gameManager;

    [SerializeField] private GameObject setupCanvas;
    [SerializeField] private GameObject resetCanvas;
    
    [SerializeField] private GameObject quitCanvas;
    
    void Start()
    {
        gameManager = GameObject.Find("GameManager").GetComponent<Management>();
    }
    
    public void GoToPage(int index)
    {
        for(int i = 0; i < pages.Length; i++)
        {
            if(i == index)
            {
                pages[i].SetActive(true);
            }
            else
            {
                pages[i].SetActive(false);
            }
        }
    }
    
    public void SetCompany(string company)
    {
        selectedCompany = company;
    }
    
    public void OnSliderChange()
    {
        amountOfQuestions = (int)slider.value;
    }
    
    public void SetInterviewer(string interviewer)
    {
        chosenInterviewer = interviewer;
    }
    
    public void ConfirmSelections()
    {
        Debug.Log("Company: " + selectedCompany);
        Debug.Log("Amount of Questions: " + amountOfQuestions);
        Debug.Log("Interviewer: " + chosenInterviewer);
        
        gameManager.StartInterview(selectedCompany, amountOfQuestions, chosenInterviewer);
        setupCanvas.SetActive(false);
        resetCanvas.SetActive(true);
        quitCanvas.SetActive(false);
        GoToPage(0);
    }
    
    public void ResetUI()
    {
        setupCanvas.SetActive(true);
        resetCanvas.SetActive(false);
        quitCanvas.SetActive(true);
 
    }
}
