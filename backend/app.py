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
import base64
load_dotenv()

app = Flask(__name__)
openai_client = OpenAI()

GPT_MODEL = "gpt-3.5-turbo"
STT_MODEL = "whisper-1"
TTS_MODEL = "tts-1"

def compute_answer_grade(question: str, answer: str) -> float:
    setup_prompt = f"Imagine the following question was asked in a FAANG interview: {question}. Given the answer to that question, give me a percentage grade (out of 100) for specifically the quality of the answer. The grade can be a float if need be. Your answer must be in this specific JSON format: {{\"grade\": <GRADE PERCENTAGE NUMBER>, \"justification\": \"<JUSTIFICATION>\"}}."
    
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

def generate_answer_response(answer: str, question: str) -> str:
    setup_prompt = f"Assuming you are an interviewer at a FAANG company, create a response to the given answer of the following question: {question}. Respond in the following format: {{\"response\": \"<RESPONSE>\"}}"

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

def text_to_speech(text: str) -> str:
    speech = openai_client.audio.speech.create(
        model=TTS_MODEL,
        voice="echo",
        input=text
    )

    dialogue_mp3_filename = f'dialogue-{floor(time())}-{token_hex(4)}.mp3'
    output_mp3_path = os.path.join('tmp-audio/', dialogue_mp3_filename)
    speech.write_to_file(output_mp3_path)

    b64_encoded_mp3 = None
    with open(output_mp3_path, mode='rb') as mp3:
        b64_encoded_mp3 = base64.b64encode(mp3.read()).decode()

    os.remove(output_mp3_path)

    return b64_encoded_mp3

@app.route('/process-answer', methods=["POST"])
def process_answer() -> object:
    # returns a grade (percentage) for your answer
    body = request.get_json()
    question = body.get('question')
    answer_text = body.get('answer_text')
    
    grade_obj = compute_answer_grade(question, answer_text)
    return grade_obj, 200

@app.route('/answer', methods=["POST"])
def respond() -> object:
    body = request.get_json()
    answer = body.get('answer')
    question = body.get('question')
    response = generate_answer_response(answer, question)
    return response, 200

@app.route('/generate-questions', methods=["POST"])
def generate_questions() -> object:
    body = request.get_json()
    company = body.get('company')
    amount = body.get('amount')
    questions = generate_interview_questions(company, amount)

    question_mp3s = []
    for question_obj in questions:
        current_mp3 = {}
        mp3_b64 = text_to_speech(question_obj.get('question'))
        current_mp3['mp3_b64'] = mp3_b64
        current_mp3['question_text'] = question_obj.get('question')
        question_mp3s.append(current_mp3)

    return question_mp3s, 200

if __name__ == '__main__':
    app.run(debug=False)
