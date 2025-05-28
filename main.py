# Prompts:
# go to microsoft edge. Then click the profile on the top right. then click profile 2. type 20 random things. The things can not relate to each other.
# go to linkedin. Log in using x_name and x_password. If it asks for verification code, open a new tab and go to gmail. Click log in and put in x_name and x_password. Then open the first email and copy the numbers. Then go back to the linkedin verification tab and put that code in.
# promt= go to xbox cloud gaming website. then click log in. then click login with a different account. then enter x_name and x_password. Go to fortnite on xbox cloud gaming website. then click log in. then click login with a different account. then enter x_name and x_password

import os
import subprocess
import asyncio
import sys # Added import
import time # Added import
from typing import List, Deque
from dotenv import load_dotenv
from pydantic import BaseModel, SecretStr
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig, Controller
from collections import deque

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

# State variables
paused = False
task_queue: Deque[str] = deque()
# A flag to signal the keyboard listener to exit
exit_flag = asyncio.Event()

# Data models
class Post(BaseModel):
    caption: str
    url: str

class Posts(BaseModel):
    posts: List[Post]

# Controller for result parsing
controller = Controller(output_model=Posts)

# Launch Microsoft Edge in remote debug mode only once
try:
    subprocess.Popen([
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "--remote-debugging-port=9222",
        "--user-data-dir=C:/tmp/edge-profile"
    ])
except FileNotFoundError:
    print("⚠️ Microsoft Edge not found. Please check the path.")
    # Decide if you want to exit or let it potentially fail later
    # For now, let's print a warning and continue, browser init will fail

# Set up the browser with correct path
browser = Browser(
    config=BrowserConfig(
        chrome_instance_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    )
)

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash', # Consider 'gemini-pro' for potentially better results
    api_key=SecretStr(gemini_api_key)
)

def keyboard_listener():
    global paused
    global task_queue
    print("DEBUG: keyboard_listener function entered (in thread).") # Ensure this is the first line
    print("Keyboard listener started. Press 'r' to pause/resume. Type 'exit' or 'quit' to stop.")
    while not exit_flag.is_set():
        try:
            # This is a blocking call, run in a separate thread by asyncio.to_thread
            command = input() 
            if exit_flag.is_set(): # Check flag immediately after input returns
                break

            if command.lower() == 'r':
                paused = not paused
                if paused:
                    print("Paused. Press 'r' to resume or enter a new task:")
                else:
                    print("Resumed.")
            elif paused:
                if command.lower() in ['exit', 'quit']:
                    print("DEBUG: keyboard_listener - 'exit'/'quit' detected while paused.")
                    exit_flag.set()
                    break
                task_queue.append(command)
                print(f"Task '{command}' added to queue. Paused. Press 'r' to resume or enter a new task:")
            elif command.lower() in ['exit', 'quit']:
                print("DEBUG: keyboard_listener - 'exit'/'quit' detected while running.")
                exit_flag.set()
                break
            else:
                # If not paused and not a special command, what should it do?
                # Option 1: Ignore (current behavior of the snippet)
                # Option 2: Add to task_queue directly (could be surprising)
                # Option 3: Print a help message
                print("DEBUG: Input received while not paused and not a special command. Ignoring. Type 'r' to pause first if you want to add tasks.")

        except EOFError:
            print("DEBUG: keyboard_listener - EOFError encountered with input(). Will wait and try again.")
            try:
                # Try to ensure stdin is clear or give it a moment
                # This is speculative, behavior of input() after EOF can be tricky
                time.sleep(2) 
            except Exception as e_sleep: # Catch if time.sleep is interrupted
                 print(f"DEBUG: keyboard_listener - sleep after EOF was interrupted: {e_sleep}")
                 if not exit_flag.is_set(): # If something else didn't already signal exit
                     exit_flag.set() # Safer to exit if sleep is broken
                 break # Exit listener loop
            print("DEBUG: keyboard_listener - Retrying input() after EOF.")
            continue # Continue to the next iteration of the while loop, to try input() again
        except Exception as e: # Catch any other unexpected errors in the listener
            if not exit_flag.is_set():
                print(f"DEBUG: keyboard_listener - Unexpected error: {e}, stopping listener.")
                # Consider if exit_flag.set() is always appropriate here
            # For now, let's break the loop on any error to be safe
            break 
    print("DEBUG: Keyboard listener stopped.")


async def main():
    global paused
    global task_queue

    print("Starting main application...")
    # Start keyboard listener in a separate thread
    # asyncio.to_thread requires Python 3.9+
    print("DEBUG: About to start keyboard_listener thread...")
    listener_task = None # Initialize listener_task to None
    try:
        # listener_task = asyncio.to_thread(keyboard_listener) # This was the old line
        listener_task = await asyncio.to_thread(keyboard_listener) # Corrected: added await
        print(f"DEBUG: keyboard_listener thread execution awaited. Listener task object: {listener_task}")
        
        # New lines to add:
        print("DEBUG: Flushing stdout and sleeping briefly before PRE_MAIN_LOOP print...")
        sys.stdout.flush()
        time.sleep(0.1) # Brief pause to allow flush and any pending I/O
    except BaseException as be: # Catch more fundamental exceptions, including SystemExit, KeyboardInterrupt
        print(f"DEBUG: FAILED to start/await keyboard listener (caught BaseException): {type(be).__name__} - {be}")
        print(f"Failed to start keyboard listener: {be}. Manual pause/task adding will not work.")
        # Optionally, exit if listener is critical
        if listener_task is None: # If it was never assigned due to early BaseException from await
             print("DEBUG: listener_task was None when BaseException was caught.")
        # It's generally good practice to re-raise KeyboardInterrupt or SystemExit if you don't intend to suppress them
        if isinstance(be, KeyboardInterrupt) or isinstance(be, SystemExit):
            print("DEBUG: Re-raising KeyboardInterrupt or SystemExit caught from listener await.")
            raise
        # return

    current_task = None
    sensitive_data = {
        'x_name': x_name,
        'x_password': x_password
    }

    try:
        print(f"DEBUG PRE_MAIN_LOOP: About to enter main loop. exit_flag.is_set() = {exit_flag.is_set()}")
        while not exit_flag.is_set():
            print(f"DEBUG MAIN_LOOP: Top, paused={paused}, current_task='{current_task}', queue_len={len(task_queue)}")
            if paused:
                if not listener_task.done(): # Keep listener alive by yielding
                    await asyncio.sleep(0.1)
                continue

            if current_task is None:
                print(f"DEBUG MAIN_LOOP: current_task is None. Checking task_queue (len={len(task_queue)}).")
                if task_queue:
                    current_task = task_queue.popleft()
                    print(f"DEBUG MAIN_LOOP: Dequeued task: '{current_task}'.")
                    print(f"Processing task from queue: {current_task}") # Existing print
                else:
                    print("DEBUG MAIN_LOOP: task_queue is empty. No new task to process.") # New print
                    # Prompt for a new task only if no task is active and queue is empty
                    # This part is tricky with the separate input thread.
                    # For now, let's rely on the keyboard_listener to add tasks
                    # or the initial prompt if the listener hasn't fully taken over.
                    # Consider how to gracefully get the first task if the listener is slow to start.
                    # One simple way: if no task, and queue empty, and not paused, prompt.
                    # However, the listener also prompts. This needs careful handling.
                    # Let's assume the listener handles all new task inputs for now.
                    # If no task, and queue empty, we just wait for tasks to be added.
                    if not exit_flag.is_set() and not paused: # Only prompt if not exiting and not paused
                        # This input might conflict with the listener's input if not careful
                        # A robust solution might involve an async queue for commands from listener to main
                        # For now, let's make main loop not prompt, relying on listener or initial tasks.
                        # To get an initial task, we can check task_queue or current_task
                        # This part of the logic is tricky with the current setup.
                        # Let's simplify: if no current_task and task_queue is empty, wait.
                        # The user will be prompted by the keyboard_listener if paused,
                        # or they can type a task if the listener is waiting for input.
                        pass # Rely on keyboard listener to add tasks or for pre-queued tasks.


            if current_task:
                if current_task.lower() in ['exit', 'quit']:
                    print("Exit command received in main loop. Shutting down...")
                    exit_flag.set()
                    break
                
                print(f"Running task: {current_task}")
                agent = Agent(
                    task=current_task,
                    llm=llm,
                    browser=browser,
                    sensitive_data=sensitive_data,
                    controller=controller
                )
                try:
                    result = await agent.run() # This is the main work
                    print(f"DEBUG: Agent run completed for task: {current_task}")
                    data = result.final_result()

                    if data is not None:
                        try:
                            parsed: Posts = Posts.model_validate(data)
                            print("Parsed Result:", parsed)
                        except Exception as e:
                            print(f"⚠️ Error parsing response data: {e}")
                            print(f"Raw data: {data}")
                    else:
                        print("ℹ️ Task completed, but no parsable data returned by agent.")
                except Exception as e:
                    print(f"DEBUG: Error during agent.run() for task '{current_task}': {e}")
                    print(f"❌ Error running agent for task '{current_task}': {e}")
                
                current_task = None # Reset current_task after processing or error
            
            print(f"DEBUG MAIN_LOOP: End of loop iteration. current_task='{current_task}'.")
            await asyncio.sleep(0.1) # Yield control regularly

    finally:
        print("Main loop ended. Cleaning up...")
        exit_flag.set() # Ensure listener knows to exit

        if 'listener_task' in locals() and listener_task is not None and not listener_task.done():
            print("Waiting for keyboard listener to stop...")
            # We can't directly await listener_task.join() in an async function
            # but setting exit_flag and giving it a moment should be enough.
            # For forceful shutdown, one might cancel it, but input() is blocking.
            # The listener is designed to check exit_flag after input() returns.
            # To make it stop faster, one might need to send a dummy input.
            await asyncio.sleep(0.5) # Give listener a chance to see the flag

        print("Closing browser...")
        await browser.close()
        print("Cleanup complete.")

# Run the main function
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCaught KeyboardInterrupt, initiating shutdown...")
        # This will set the flag, and the finally block in main should handle cleanup.
        exit_flag.set() 
        # A small delay to allow cleanup to try and run.
        # Note: asyncio.run() might have already exited its loop.
        # Consider if browser.close() needs to be called here too if main's finally doesn't run.
        # For now, assuming main's finally block will handle it if asyncio.run was active.
    finally:
        # This is a fallback if asyncio.run() itself is interrupted harshly.
        # We need to ensure browser is closed.
        # However, browser.close() is async, can't call from sync finally easily.
        # The design relies on main()'s finally block.
        # If the program is force-killed, OS handles resource cleanup.
        print("Program exited.")


#go to https://mathspace.co/work/CurriculumCustomWorkout-15927529/Problem-1184889796?state=problem. then solve the problem but dont enter the answer. after you finish solving the problem, click the next problem. Keep doing this untill you finish problem 10. You have the select the prob
#lem number at the top right to go to the next problem  
