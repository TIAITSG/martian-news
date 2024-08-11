import os
import requests
import anthropic
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

CLAUDE_KEY = os.getenv("CLAUDE_KEY")
client = anthropic.Anthropic(api_key=CLAUDE_KEY)

def generate_blog_post(prompt):
  message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1024,
        messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": f"Write a blog post about the following topic: {prompt} Write it from the viewpoint of RedSoil Agritech, a martian company that specializes in Martian Agriculture. Make sure that is in Markdown format. Do not return anything else, just the content of the blog post."}
            ],
        }
      ],
  )
    
  blog_post = message.content[0].text
  # import pdb; pdb.set_trace()
  return blog_post
  # return response.json()["content"][0]["text"]

def save_blog_post(content, title):
    # ---
    # layout: post
    # title:  "Martian Agricultural Breakthroughs: Growing Food on the Red Planet"
    # date:   2024-08-10
    # author: "Kirk Zirconium"
    # ---
    date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S-07:00")
    filename = f"{date}-{title.lower().replace(' ', '-')}.md"
    filepath = os.path.join("_posts", filename)
    
    with open(filepath, "w") as f:
        f.write("---\n")
        f.write(f"layout: post\n")
        f.write(f"title: \"{title}\"\n")
        f.write(f"date: {date}\n")
        f.write(f"author: Kirk Zirconium\n")
        f.write("---\n\n")
        f.write(content)
    
    print(f"Blog post saved as {filepath}")

def main():
    prompt = input("Enter a prompt for the blog post: ")
    title = input("Enter a title for the blog post: ")
    
    print("Generating blog post...")
    blog_content = generate_blog_post(prompt)
    
    save_blog_post(blog_content, title)

if __name__ == "__main__":
    main()
