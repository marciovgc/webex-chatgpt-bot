from flask import Flask, request, json
import requests
from openai import OpenAI
client = OpenAI()
import os

# Set up OpenAI API credentials
client.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
port = 5005
base_url = 'https://webexapis.com/v1/'
api_key = os.getenv("OPENAI_WEBEX_BOT_TOKEN")
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

@app.route('/', methods=['POST'])
def index():
    data = request.get_json()
    print(json.dumps(data,indent=4))
    bot_id = requests.get(f'{base_url}/people/me', headers=headers).json().get('id')
    if bot_id == data.get('data').get('personId'):
        return 'Message from self ignored'
    else:
        message_id = data.get('data').get('id')
        message_url = f'{base_url}/messages/{message_id}'
        message_text = requests.get(message_url, headers=headers).json().get('text')
        print(message_text)

        room_id = data.get('data').get('roomId')
        # Generate text using GPT-3.5
        response = client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = [
                {
                    "role": "user", 
                    "content": message_text
                 }
                 ],
            temperature = 1,
            n = 1,
            max_tokens = 70   
        )
        
        reply = response.choices[0].message.content
        # Print the generated text
        print(reply)

        my_msg_data = {
            "roomId": room_id,
            "text": reply,
            }
        post_message_url = f'{base_url}/messages'
        post_message_data = requests.post(post_message_url,headers=headers,data=json.dumps(my_msg_data))

    return data

app.run(host="0.0.0.0", port=port, debug=True)
