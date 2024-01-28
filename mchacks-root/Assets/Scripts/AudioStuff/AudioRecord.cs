using UnityEngine;
using System.Collections;
using System.IO;
using System;
using OpenAI;
public class AudioRecord : MonoBehaviour
{
    AudioClip myAudioClip;

    private string output;
    private int i = 0;
    
    private OpenAIApi openai = new OpenAIApi("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");

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

    public void SubmitAudio()
    {
        //submit
    }
    
    
}