1. Project Title
* A clear, descriptive title.
* Example: `Door Sound Activated YouTube Closer & Desktop Switcher`
2. Description
* A brief overview of what the project does.
* Example: "This Python script listens for specific door sounds (like creaks or slams) using a machine learning model. Upon detection, it specifically closes any open YouTube tab in a chosen browser (on macOS) and then switches to the next virtual desktop."
* Mention its purpose or your motivation if you like.
3. Features
* Bullet list of key functionalities:
    * Real-time audio listening.
    * Door sound detection using the YAMNet pre-trained model.
    * Targets and closes specific YouTube tabs (macOS via AppleScript).
    * Switches to the next virtual desktop (macOS via AppleScript).
    * Configurable target sounds, confidence threshold, and target browser.
4. Platform
* **Primarily designed for macOS.**
* Explain that core functionalities like specific browser tab control and desktop switching are implemented using AppleScript, making them macOS-specific.
* Mention that the sound detection part is cross-platform, but the action part would need to be adapted for Windows/Linux.
5. Prerequisites
* **macOS:** (Specify version if known, e.g., Sequoia, Sonoma, Ventura)
* **Python:** Version 3.11 (as this was found to be compatible with TensorFlow for your M2 Mac).
* **Homebrew:** (Recommended for installing Python 3.11 on macOS if not already available).
* **`curl`:** Used by the script to download the YAMNet class map CSV if not present. (Usually pre-installed on macOS).
* **Python Libraries:** List them. It's best to also include a `requirements.txt` file in your repository (see step 6c).
    * `tensorflow` (or `tensorflow-macos` for Apple Silicon)
    * `tensorflow-metal` (for Apple Silicon GPU support)
    * `tensorflow_hub`
    * `numpy`
    * `sounddevice`
    * `librosa`
    * `pyautogui` (though its role on Mac for desktop switching was replaced, it might still be in the imports or for other OS placeholders)
    * `pandas`
6. Setup & Installation
* **a. Clone the Repository:**
    ```bash
    git clone [URL_OF_YOUR_GITHUB_REPO]
    cd [YOUR_PROJECT_FOLDER_NAME]
    ```
* **b. Create and Activate Virtual Environment (Recommended for macOS with Python 3.11):**
    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    ```
* **c. Install Dependencies:**
    * Advise to upgrade pip first:
        ```bash
        pip install --upgrade pip
        ```
    * Then install packages. You can list them individually or (better) tell users to install from a `requirements.txt` file.
        * **To create `requirements.txt`:** While your `venv` is active and all packages are installed, run:
            ```bash
            pip freeze > requirements.txt
            ```
            Then commit this file to your repository.
        * **Installation instruction for users:**
            ```bash
            pip install -r requirements.txt
            ```
* **d. macOS Permissions (Crucial):**
    * **Microphone Access:** System Settings > Privacy & Security > Microphone. Ensure your Terminal app (or VS Code, if running Python directly through it) has permission.
    * **Automation Access:** System Settings > Privacy & Security > Automation. Your Terminal app (or VS Code) will need permission to control:
        * Your target browser (e.g., "Google Chrome", "Safari").
        * "System Events" (for the AppleScript desktop switching).
        * (Potentially "Finder" if you were to add scripts that interact with it).
        * *These permission dialogs usually pop up on the first attempt to automate an application.*
    * **Accessibility Access (Optional but good for `pyautogui` if used more broadly):** System Settings > Privacy & Security > Accessibility. Ensure your Terminal app (or VS Code) is listed and checked.
    * **Mission Control Shortcuts:** System Settings > Keyboard > Keyboard Shortcuts > Mission Control. Ensure "Move right a space" is enabled and set to `^→` (Control-Right Arrow) or the desired shortcut.
7. Configuration
* Explain that users can modify these variables at the top of your Python script (`main.py`):
    * `TARGET_SOUND_NAMES = ["Creak", "Squeak", "Door", "Wood"]`: List of YAMNet sound classes to trigger actions.
    * `CONFIDENCE_THRESHOLD = 0.15`: The minimum score for a sound to be considered detected (0.0 to 1.0).
    * `BROWSER_TO_TARGET = "Google Chrome"`: Can be changed to `"Safari"` or other scriptable browsers (though the AppleScript might need tweaks for others).
8. Usage
* How to run the script:
    ```bash
    python main.py 
    ```
    (Assuming the virtual environment is active).
* What to expect: The script will start listening for sounds. Console output will show detected sounds and actions.
* Remind that the YAMNet model (a few MB) and the class map CSV will be downloaded on the first run.
9. How It Works (Optional - good for understanding)
* Briefly explain the pipeline:
    * `sounddevice` captures audio.
    * YAMNet (loaded via `tensorflow_hub`) processes audio chunks and classifies sounds.
    * If a target sound exceeds the confidence threshold:
        * An AppleScript (run via `subprocess`) targets the specified browser to find and close YouTube tabs.
        * Another AppleScript (run via `subprocess`) triggers the "move right a space" Mission Control shortcut.
10. Troubleshooting (Optional)
* **TensorFlow Installation Issues:** Briefly mention the Python version sensitivity (e.g., Python 3.13 issues, recommending 3.11 for M1/M2/M3 Macs with `tensorflow-macos`).
* **No Sound Detected:** Suggest checking microphone input, permissions, `TARGET_SOUND_NAMES`, and adjusting `CONFIDENCE_THRESHOLD`.
* **Actions Not Happening:** Emphasize checking macOS Automation permissions.
* **"osascript not found" or AppleScript errors:** Ensure macOS is the operating system.
* **"curl not found":** (Unlikely on Mac, but good to note if the script relies on it for the CSV).
11. To-Do / Future Improvements (Optional)
* Ideas for extending the project, e.g.:
    * Support for other operating systems (Windows, Linux) for specific actions.
    * GUI interface instead of command-line.
    * More advanced sound model training/fine-tuning for specific door sounds.
    * Configurable actions beyond closing YouTube and switching desktops.
12. License
* State the license under which you are releasing the code. If you don't choose one, it's typically "All rights reserved." For open source, common choices are MIT, Apache 2.0, or GPL.
* Example: `This project is licensed under the MIT License - see the LICENSE.md file for details.` (You'd then create a `LICENSE.md` file).
13. Acknowledgements (Optional)
* Thank or mention key libraries or resources:
    * Google for YAMNet and TensorFlow.
    * The developers of the Python libraries used.
