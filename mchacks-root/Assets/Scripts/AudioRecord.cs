using UnityEngine;
using System.Collections;
using System.IO;
using System;


public class AudioRecord : MonoBehaviour
{
    AudioClip myAudioClip;
    private int i = 0;

    public void StartRecording()
    {
        myAudioClip = Microphone.Start(null, false, 10, 44100);
    }
    
    public void StopRecording()
    {
        SavWav.Save("interview_answer" + i, myAudioClip);
        i++;
        Microphone.End(null); 
        
        Debug.Log(myAudioClip.length);
        Debug.Log(myAudioClip.GetType());

    }
    
    public void PlayAudio()
    {
        AudioSource audio = GetComponent<AudioSource>();
        audio.clip = myAudioClip;
        audio.Play();
    }
    
    
}