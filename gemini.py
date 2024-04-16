import os
import requests
from dotenv import load_dotenv
import json
import argparse
import openai
from PIL import Image
from io import BytesIO
import base64
from pathlib import Path

def generate_image(prompt, api_key):
	openai.api_key = api_key  # Set the OpenAI API key
	response = openai.images.generate(
		prompt=prompt,
		n=1,
		size="1024x1024",
		response_format="url",
		model="dall-e-2",
	)
	image_url = response.data[0].url
	image_response = requests.get(image_url)
	image_bytes = image_response.content
	image = Image.open(BytesIO(image_bytes))

	# Create the Images directory if it doesn't exist
	images_dir = Path('Images')
	images_dir.mkdir(exist_ok=True)

	# Find the next available filename
	filename = images_dir / 'generated_image_1.png'
	counter = 1
	while filename.exists():
		counter += 1
		filename = images_dir / f'generated_image_{counter}.png'

	# Save and show the image
	image.save(filename)
	image.show()
	print(f"Image saved as {filename}")



def generate_text(prompt, api_key):
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

def main(image_mode):
	load_dotenv()
	google_api_key = os.getenv('GOOGLE_API_KEY')
	openai_api_key = os.getenv('OPENAI_API_KEY')

	prompt = input("Please type a prompt: ")
	print("Generating...")

	if image_mode:
		generate_image(prompt, openai_api_key)
	else:
		generate_text(prompt, google_api_key)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Generate content using Google Gemini or OpenAI DALL-E.')
	parser.add_argument('-image', action='store_true', help='Generate an image using OpenAI DALL-E')
	args = parser.parse_args()
	main(args.image)
