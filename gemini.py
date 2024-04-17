import os
import requests
from dotenv import load_dotenv
import json
import argparse
import openai
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
from pathlib import Path

FONT_PATH = "Arial.ttf"	 # Assuming Arial.ttf is in the same directory

def generate_image(prompt, api_key):
	openai.api_key = api_key
	response = openai.images.generate(
		prompt=prompt,
		n=1,
		size="1024x1024",
		response_format="url",
		model="dall-e-3",
	)
	image_url = response.data[0].url
	image_response = requests.get(image_url)
	image_bytes = image_response.content
	image = Image.open(BytesIO(image_bytes))

	images_dir = Path('Images')
	images_dir.mkdir(exist_ok=True)

	filename = images_dir / 'generated_image_1.png'
	counter = 1
	while filename.exists():
		counter += 1
		filename = images_dir / f'generated_image_{counter}.png'

	image.save(filename)
	add_text_overlay(image, prompt) 
	image.show()
	print(f"Image saved as {filename}")

def add_text_overlay(image, prompt, text_color=(255, 255, 255)):
	width, height = image.size
	overlay_height = int(height * 0.1)	
	overlay = Image.new('RGBA', (width, overlay_height), (0, 0, 0, 128)) 
	draw = ImageDraw.Draw(overlay)

	script_dir = os.path.dirname(__file__) 
	absolute_font_path = os.path.join(script_dir, FONT_PATH)

	if not os.path.isfile(absolute_font_path):
		print("Error: Arial.ttf not found.")
		return	

	max_text_width = width * 0.8 

	capitalized_prompt = prompt.title().strip() 
	if not capitalized_prompt:	
		capitalized_prompt = "(No Text Entered)" 

	# Word Wrapping Logic 
	lines = [] 
	current_line = ""

	# Initial font size
	font_size = 36	

	while True:	 # Loop to find the optimal font size
		lines = []	# Reset lines for each font size iteration
		current_line = ""
		for word in capitalized_prompt.split():
			test_line = current_line + " " + word
			test_width = draw.textlength(test_line, font=ImageFont.truetype(absolute_font_path, font_size)) 
			if test_width > max_text_width:
				lines.append(current_line.strip())
				current_line = word
			else:  
				current_line = test_line
		lines.append(current_line.strip()) 

		# If text fits within overlay, we have the right font size
		if len(lines) * font_size <= overlay_height: 
			break

		# Otherwise, reduce font size
		font_size -= 4	

	# Draw the wrapped text (with the final font size)
	y = (overlay_height - len(lines) * font_size) // 2 

	for line in lines:
		text_width = draw.textlength(line, font=ImageFont.truetype(absolute_font_path, font_size))
		x = int((width - text_width) / 2)  
		draw.text((x, y), line, fill=text_color, font=ImageFont.truetype(absolute_font_path, font_size))
		y += font_size

	image.paste(overlay, (0, height - overlay_height), overlay) 

def generate_text(prompt, api_key):
	print("Text generation functionality not yet implemented.") 

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
