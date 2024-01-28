using UnityEngine;
using System.Collections;
using System.IO;
using System;
using OpenAI;
public class AudioRecord : MonoBehaviour
{
    AudioClip myAudioClip;

    public string output;
    private int i = 0;
    
    private int questionNumber = 0;
    
    private OpenAIApi openai = new OpenAIApi();

    public void StartRecording()
    {
        myAudioClip = Microphone.Start(null, false, 10, 44100);
    }
    
    public async void StopRecording()
    {
        byte[] data = SavWav.Save("interview_answer" + i, myAudioClip);
        i++;
        Microphone.End(null); 
        
        var req = new CreateAudioTranscriptionsRequest
        {
            FileData = new FileData() {Data = data, Name = "audio.wav"},
            // File = Application.persistentDataPath + "/" + fileName,
            Model = "whisper-1",
            Language = "en"
        };
        var res = await openai.CreateAudioTranscription(req);
        
        output = res.Text;
        Debug.Log(output);
    }
    
    public void PlayAudio()
    {
        AudioSource audio = GetComponent<AudioSource>();
        audio.clip = myAudioClip;
        audio.Play();
    }
    
    public string GetOutput()
    {
        return output;
    }
}