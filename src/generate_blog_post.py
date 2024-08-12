import os
import json
import requests
import anthropic
import fal_client
from dotenv import load_dotenv
from datetime import datetime
from PIL import Image
from io import BytesIO

# Load environment variables
load_dotenv()

# call fal to generate a photo
FAL_KEY = os.getenv("FAL_KEY")

def generate_blog_photo(prompt):
    base_uri = 'https://fal.run'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Key {os.environ['FAL_API_ID']}:{os.environ['FAL_API_SECRET']}"
    }
    data = {
        "prompt": prompt
    }
    
    response = requests.post(f"{base_uri}/fal-ai/fast-lightning-sdxl", json=data, headers=headers)
    
    if response.ok:
        return response.json()['images'][0]['url']
    else:
        print(headers)
        return None

CLAUDE_KEY = os.getenv("CLAUDE_KEY")
client = anthropic.Anthropic(api_key=CLAUDE_KEY)

def generate_blog_post(prompt):
  json_example = {"blog_title": "Martian Fuel Shortages Cause Strain on Planet's Economy", "blog_content": "<insert markdown content here>", "blog_photo_prompt": "Martian fuel shortage, mars landscape, space theme"}
  message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1024,
        messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": f"Write a blog post about the following topic: {prompt}. Write it from the viewpoint of RedSoil Agritech, a martian company that specializes in Martian Agriculture. Make sure that is in Markdown format. Please return JSON back for your response. The JSON should look like this: {{ json_example }}. For the blog_photo_prompt, please give back 2-4 sentences that include descriptive visual words like: Vibrant, dark, beautiful. You can also include descriptions of people, places, or objects. Make sure the blog_photo_prompt is related to the article. For example, if the article or prompt is about green glowing cows, make sure that is in the blog_photo_prompt. Please do not return anything else, just the JSON. Only return the keys blog_title, blog_content, and blog_photo_prompt. Only return syntactically correct JSON."}
            ],
        }
      ],
  )
    
  blog_post = message.content[0].text
  blog_post_json = json.loads(blog_post)
  print(f"Generate new article with title: {blog_post_json['blog_title']}")
  print(f"Generate new article with contents: {blog_post_json['blog_content']}")
  print(f"Generate new article with blog_photo_prompt: {blog_post_json['blog_photo_prompt']}")
  # create an image with fal via blog_photo_prompt
  # return back the title and content separately
  return blog_post_json["blog_title"], blog_post_json["blog_content"], blog_post_json["blog_photo_prompt"]

def save_blog_post(title, content, image_url):
    date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date}-{title.lower().replace(' ', '-')}.md"
    posts_dir = os.path.join(os.getcwd(), "_posts")
    filepath = os.path.join(posts_dir, filename)
    
    
    # Download the image
    image_filename = f"{date}-{title.lower().replace(' ', '-')}.jpg"
    images_dir = os.path.join(os.getcwd(), "assets", "images")
    image_filepath = os.path.join(images_dir, image_filename)
    
    # Ensure assets/images directory exists
    os.makedirs(images_dir, exist_ok=True)
    
    if image_url:
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            img.save(image_filepath)
            print(f"Image saved as {image_filepath}")
        except requests.RequestException as e:
            print(f"Failed to download image: {e}")
            image_filename = None
    else:
        image_filename = None

    date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S-07:00")
    with open(filepath, "w") as f:
        f.write("---\n")
        f.write(f"layout: post\n")
        f.write(f"title: \"{title}\"\n")
        f.write(f"date: {date}\n")
        f.write(f"author: Kirk Zirconium\n")
        if image_filename:
            f.write(f"image: /assets/images/{image_filename}\n")
        f.write("---\n\n")
        if image_filename:
            f.write(f"![{title}](/assets/images/{image_filename})\n\n")
        f.write(content)
    
    print(f"Blog post saved as {filepath}")

def main():
    # eventually, we want to just generate prompts on our own
    # on a cron job.
    prompt = input("Enter a prompt for the blog post: ")
    print("Generating blog post...")
    # blog_content = generate_blog_post(prompt)
    blog_title, blog_content, blog_photo_prompt = generate_blog_post(prompt)
    image_url = generate_blog_photo(blog_photo_prompt)
    if image_url:
        save_blog_post(blog_title, blog_content, image_url)
    else:
        print("Failed to generate image. Saving blog post without image.")
        save_blog_post(blog_title, blog_content, None)


if __name__ == "__main__":
    main()