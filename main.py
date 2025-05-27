# Prompts:
# go to microsoft edge. Then click the profile on the top right. then click profile 2. type 20 random things. The things can not relate to each other.
# go to linkedin. Log in using x_name and x_password. If it asks for verification code, open a new tab and go to gmail. Click log in and put in x_name and x_password. Then open the first email and copy the numbers. Then go back to the linkedin verification tab and put that code in.
# promt= go to xbox cloud gaming website. then click log in. then click login with a different account. then enter x_name and x_password. Go to fortnite on xbox cloud gaming website. then click log in. then click login with a different account. then enter x_name and x_password

import os
import subprocess
import asyncio
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, SecretStr
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig, Controller

# Load environment variables
load_dotenv()

# Validate required credentials
x_name = os.getenv('X_NAME')
x_password = os.getenv('X_PASSWORD')
gemini_api_key = os.getenv('GEMINI_API_KEY')

if not x_name or not x_password:
    raise ValueError("❌ Missing required environment variables: X_NAME and/or X_PASSWORD")
if not gemini_api_key:
    raise ValueError("❌ Missing required environment variable: GEMINI_API_KEY")

# Data models
class Post(BaseModel):
    caption: str
    url: str

class Posts(BaseModel):
    posts: List[Post]

# Controller for result parsing
controller = Controller(output_model=Posts)

# Launch Microsoft Edge in remote debug mode
subprocess.Popen([
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "--remote-debugging-port=9222",
    "--user-data-dir=C:/tmp/edge-profile"
])

# Set up the browser with correct path
browser = Browser(
    config=BrowserConfig(
        chrome_instance_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    )
)

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash',
    api_key=SecretStr(gemini_api_key)
)

async def main():
    task = input("Enter your task: ")

    sensitive_data = {
        'x_name': x_name,
        'x_password': x_password
    }

    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        sensitive_data=sensitive_data,
        controller=controller
    )

    result = await agent.run()
    data = result.final_result()

    if data is not None:
        try:
            parsed: Posts = Posts.model_validate(data)
            print(parsed)
        except Exception as e:
            print(f"⚠️ Error parsing response data: {e}")
    else:
        print("❌ Error: No data returned to parse.")

    await browser.close()

# Run the main function
asyncio.run(main())


#go to https://mathspace.co/work/CurriculumCustomWorkout-15927529/Problem-1184889796?state=problem. then solve the problem but dont enter the answer. after you finish solving the problem, click the next problem. Keep doing this untill you finish problem 10. You have the select the prob
#lem number at the top right to go to the next problem  
