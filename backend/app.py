from openai import OpenAI
from flask import Flask
from flask import request
from dotenv import load_dotenv
from time import time
from secrets import token_hex
from math import floor
import boto3
import json
import os
load_dotenv()

app = Flask(__name__)
openai_client = OpenAI()

GPT_MODEL = "gpt-3.5-turbo"
STT_MODEL = "whisper-1"
TTS_MODEL = "tts-1"

S3_CLIENT = boto3.client(
    service_name='s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1'
)

def answer_correct(given_answer: str, correct_answer: str) -> bool:
    setup_prompt = f"Given the correct answer to a question, you are clearly stating whether or not a given arbitrary answer is correct. Here is the correct answer: {correct_answer}. Using JSON, state whether or not the answer is correct with the following format: {{\"correct\": true}} if correct, and {{\"correct\": false}} if incorrect."

    completion = openai_client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {
                "role": "system", 
                "content": setup_prompt
            },
            {
                "role": "user", 
                "content": given_answer
            }
        ]
    )
    gpt_answer = json.loads(completion.choices[0].message.content)
    return gpt_answer.get('correct')

def compute_answer_grade(question: str, correct_answer: str, answer: str, right_wrong_answer: bool, answer_is_correct: bool) -> float:
    setup_prompt = f"Imagine the following question was asked in a FAANG interview: {question}. Given the answer to that question, give me a percentage grade (out of 100) for specifically the quality of the answer. The grade can be a float if need be. " + (("Then edit the grade based on the fact that candidate answered the question {0}. ".format("correctly" if answer_is_correct else f"wrong. Here was the correct answer to the question: {correct_answer}. ")) if right_wrong_answer else "") + "Your answer must be in this specific JSON format: {\"grade\": <GRADE PERCENTAGE NUMBER>, \"justification\": \"<JUSTIFICATION>\"}."
    
    completion = openai_client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {
                "role": "system", 
                "content": setup_prompt
            },
            {
                "role": "user", 
                "content": answer
            }
        ]
    )
    gpt_answer = json.loads(completion.choices[0].message.content)
    return gpt_answer

def generate_interview_questions(company: str, amount: int) -> 'list[object]':
    setup_prompt = f"Given one of the following companies, generate a given amount of non-coding interview questions: Facebook, Apple, Amazon, Netflix, Google. If the given company name is \"all\", select every company previously listed when generating the interview questions. The input will be in the following format: <COMPANY NAME>,<AMOUNT OF QUESTIONS>. Please output the questions in the following JSON format: [{{\"question\": \"<OUTPUTTED QUESTION 1>\"}}, {{\"question\": \"<OUTPUTTED QUESTION 2>\"}}, {{\"question\": \"<OUTPUTTED QUESTION 3>\"}}, ..., {{\"question\": \"<OUTPUTTED QUESTION N>\"}}]"

    completion = openai_client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {
                "role": "system", 
                "content": setup_prompt
            },
            {
                "role": "user", 
                "content": f'{company},{amount}'
            }
        ]
    )
    gpt_answer = json.loads(completion.choices[0].message.content)
    return gpt_answer

def speech_to_text(mp3_path: str) -> str:
    with open(mp3_path, mode='rb') as mp3:
        transcript = openai_client.audio.transcriptions.create(
            model=STT_MODEL, 
            file=mp3,
            response_format='text'
        )
    os.remove(mp3_path) # remove the temporary answer MP3
    return transcript

def text_to_speech(text: str) -> str:
    speech = openai_client.audio.speech.create(
        model=TTS_MODEL,
        voice="echo",
        input=text
    )

    dialogue_mp3_filename = f'dialogue-{floor(time())}-{token_hex(4)}.mp3'
    output_mp3_path = os.path.join('tmp-audio/', dialogue_mp3_filename)
    speech.write_to_file(output_mp3_path)

    with open(output_mp3_path, mode='rb') as dialogue:
        S3_CLIENT.upload_fileobj(dialogue, os.getenv('S3_BUCKET_NAME'), dialogue_mp3_filename)
    os.remove(output_mp3_path)

    return dialogue_mp3_filename

def pull_answer_mp3(mp3_r2_path: str) -> str:
    filename = mp3_r2_path.split('/')[-1]
    with open(f'tmp-audio/{filename}', mode='wb') as tmp_mp3:
        mp3_data = S3_CLIENT.get_object(Bucket=os.getenv('S3_BUCKET_NAME'), Key=mp3_r2_path)
        tmp_mp3.write(mp3_data['Body'].read())
        S3_CLIENT.delete_object(Bucket=os.getenv('S3_BUCKET_NAME'), Key=mp3_r2_path)

    return os.path.join('tmp-audio/', filename)

@app.route('/process-answer', methods=["POST"])
def process_answer() -> object:
    # returns a grade (percentage) for your answer
    body = request.get_json()
    answer_audio_r2_path = body.get('answer_audio_r2_path')
    right_wrong_answer = body.get('right_wrong_answer')
    correct_answer = body.get('correct_answer')
    question = body.get('question')
    
    answer_mp3_path = pull_answer_mp3(answer_audio_r2_path)
    answer_text = speech_to_text(answer_mp3_path)

    answer_is_correct = None
    if right_wrong_answer:
        answer_is_correct = answer_correct(answer_text, correct_answer)
    
    grade_obj = compute_answer_grade(question, correct_answer, answer_text, right_wrong_answer, answer_is_correct)
    return grade_obj, 200


@app.route('/generate-questions', methods=["POST"])
def generate_questions() -> object:
    body = request.get_json()
    company = body.get('company')
    amount = body.get('amount')
    questions = generate_interview_questions(company, amount)

    question_mp3s = []
    for question_obj in questions:
        current_mp3 = {}
        mp3_s3_filename = text_to_speech(question_obj.get('question'))
        current_mp3['mp3_filename'] = mp3_s3_filename
        current_mp3['question_text'] = question_obj.get('question')
        question_mp3s.append(current_mp3)

    return question_mp3s, 200

if __name__ == '__main__':
    app.run(debug=False)
