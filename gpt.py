import requests
from transformers import AutoTokenizer
import json
import logging
from config import URL, HEADERS
filename = 'user.json'

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)


def read_users():
    try:
        with open(filename, 'r') as f:
            users = json.load(f)
    except:
        users = {}
    return users


def write_users(users):
    with open(filename, 'w') as f:
        json.dump(users, f)


users = read_users()

gpt = {
    'system_content': "Ты помощник по программирования "
                      "на языке программирования python",
    'URL': URL,
    'HEADERS': HEADERS,
    'MAX_TOKENS': 600,
    'assistant_content': 'Продолжи объяснение: '
}


def count_tokens(prompt):
    tokenizer = AutoTokenizer.from_pretrained(
        "mistralai/Mistral-7B-Instruct-v0.1")
    return len(tokenizer.encode(prompt))


def process_resp(response, message):
    if response.status_code != 200:
        clear_history(message)
        return False, logging.debug(f'Error {response.status_code}')

    try:
        resp = response.json()
    except:
        clear_history(message)
        return False, logging.debug("Error receiving JSON")

    if "error" in resp or 'choices' not in resp:
        clear_history(message)
        return False, logging.debug(f"Error in JSON")

    result = resp['choices'][0]['message']['content']

    save_history(result, message)
    return True, gpt['assistant_content'], result


def make_prompt(prompt, message):
    json = {
        "messages": [
            {"role": "system", "content": gpt['system_content']},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": users[message.chat.id]
            ['assistant_content']},
        ],
        "temperature": 0.7,
        "max_tokens": gpt['MAX_TOKENS'],
    }
    return json


def send_request(json):
    request = requests.post(url=gpt['URL'], headers=gpt['HEADERS'], json=json)
    return request


def save_history(result, message):
    users[message.chat.id]['assistant_content'] += result
    write_users(users)


def clear_history(message):
    users[message.chat.id]['assistant_content'] = \
        gpt['assistant_content']
    write_users(users)

