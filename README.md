# Automated Browser Task Agent

This script uses AI to control a web browser and perform tasks based on user prompts. It features a pause/resume capability and allows for adding new tasks dynamically.

## Setup

1.  **Environment Variables:**
    This project requires certain API keys and credentials to be set up in an `.env` file in the root of the project directory. Create a file named `.env` and add the following variables:

    ```
    GEMINI_API_KEY=your_gemini_api_key_here
    X_NAME=your_x_login_name_here
    X_PASSWORD=your_x_login_password_here
    ```

    Replace the placeholder values with your actual credentials. The `GEMINI_API_KEY` is for accessing the Google Gemini language model. `X_NAME` and `X_PASSWORD` are example credential names used by the script for tasks requiring logins; you might need to adjust these based on the specific tasks you automate.

2.  **Dependencies:**
    The script uses several Python libraries. Ensure you have Python installed. The core dependencies are:
    *   `python-dotenv`
    *   `langchain-google-genai`
    *   `pydantic`
    *   The `browser_use` library (and its dependencies, like `playwright`).

    It's recommended to install these in a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install python-dotenv langchain-google-genai pydantic browser-use
    # You might also need to install browser binaries for Playwright if not already present:
    playwright install
    ```
    (Note: The `browser_use` library might have its own specific installation instructions for Playwright if it bundles it.)

3.  **Microsoft Edge:**
    The script is currently configured to use Microsoft Edge and expects it to be available at `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`. It launches Edge in remote debugging mode.

## How to Run

Once the setup is complete, run the script from your terminal:

```bash
python main.py
```

The script will initialize and then wait for your input. Initially, it will prompt "Enter your task: " if no tasks are queued.

## Key Features

*   **Task Input:** Enter a descriptive prompt for the task you want the agent to perform.
*   **Pause/Resume:**
    *   Press the 'r' key (followed by Enter) at any time to pause the current operation or task processing.
    *   A "Paused. Press 'r' to resume or enter a new task:" message will appear.
    *   To resume, press 'r' (followed by Enter) again. A "Resumed." message will appear.
*   **Adding Tasks While Paused:**
    *   When the script is paused, instead of pressing 'r' to resume, you can type a new task prompt and press Enter.
    *   This new task will be added to a queue.
    *   The script will remain paused, allowing you to add more tasks.
    *   When you resume, tasks from the queue will be processed in the order they were added, after the currently interrupted task (if any) is completed.
*   **Exiting the Script:**
    *   To shut down the script gracefully, type `exit` or `quit` (followed by Enter) when prompted for input (either during pause or when it's asking for a new task).
    *   This will close the browser and terminate the script. You can also use Ctrl+C.
