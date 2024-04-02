import os
import requests
from dotenv import load_dotenv
import json

def main():
	load_dotenv()
	api_key = os.getenv('GOOGLE_API_KEY')

	prompt = input("Please type a prompt: ")
	print("Generating...")

	headers = {
		'Content-Type': 'application/json'
	}

	data = {
		'contents': [
			{
				'parts': [
					{'text': prompt}
				]
			}
		]
	}

	url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}'

	response = requests.post(url, headers=headers, json=data)
	print(response.text)  # Print the raw response

	try:
		response_data = response.json()
		if 'candidates' in response_data:
			for candidate in response_data['candidates']:
				if 'content' in candidate and 'parts' in candidate['content']:
					for part in candidate['content']['parts']:
						if 'text' in part:
							print(part['text'].replace('\\n', '\n'))
		else:
			print("Failed to generate text.")
	except Exception as e:
		print(f"Error parsing JSON response: {e}")

if __name__ == '__main__':
	main()
