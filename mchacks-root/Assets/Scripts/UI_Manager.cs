using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

public class UI_Manager : MonoBehaviour
{
    [SerializeField] GameObject[] setupPages;
    public string selectedCompany = "";
    public int amountOfQuestions = 0;
    public string chosenInterviewer = "";
    
    [SerializeField] Slider slider;

    private Management gameManager;

    [SerializeField] private GameObject setupCanvas;
    [SerializeField] private GameObject resetCanvas;
    
    [SerializeField] private GameObject quitCanvas;
    
    [SerializeField] private GameObject recordCanvas;
    
    [SerializeField] private GameObject resultsCanvas;
    
    private List<string> resultTitles = new List<string>();
    private List<int> resultScores = new List<int>();
    private List<string> resultDescriptions = new List<string>();
    
    private GameObject[] resultTitlesText;
    private GameObject[] resultScoresText;
    
    private Slider resultSlider;
    private GameObject[] resultDescriptionsText;
    
    public Color selectedColor;
    public Color unselectedColor;
    [SerializeField] private GameObject[] resultButtons;
    
    
    
    void Start()
    {
        gameManager = GameObject.Find("GameManager").GetComponent<Management>();
    }
    
    public void GoToPage(int index)
    {
        for(int i = 0; i < setupPages.Length; i++)
        {
            if(i == index)
            {
                setupPages[i].SetActive(true);
            }
            else
            {
                setupPages[i].SetActive(false);
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
    
    public async void ConfirmSelections()
    {
        Debug.Log("Company: " + selectedCompany);
        Debug.Log("Amount of Questions: " + amountOfQuestions);
        Debug.Log("Interviewer: " + chosenInterviewer);
        
        gameManager.StartInterview(selectedCompany, amountOfQuestions, chosenInterviewer);
        setupCanvas.SetActive(false);
        resetCanvas.SetActive(true);
        recordCanvas.SetActive(true);
        quitCanvas.SetActive(false);
        GoToPage(0);
    }
    
    public void ResetUI()
    {
        setupCanvas.SetActive(true);
        resetCanvas.SetActive(false);
        quitCanvas.SetActive(true);
        recordCanvas.SetActive(false);
 
    }

    public void GoToResultsTab(int index)
    {
        for(int i = 0; i < resultButtons.Length; i++)
        {
            if(i == index)
            {
                resultButtons[i].gameObject.GetComponent<Image>().color = selectedColor;
                resultTitlesText[i].GetComponent<Text>().text = resultTitles[i];
                resultScoresText[i].GetComponent<Text>().text = resultScores[i].ToString();
                resultSlider.value = resultScores[i];
                resultDescriptionsText[i].GetComponent<Text>().text = resultDescriptions[i];
            }
            else
            {
                resultButtons[i].gameObject.GetComponent<Image>().color = unselectedColor;
            }
        }
    }
}
