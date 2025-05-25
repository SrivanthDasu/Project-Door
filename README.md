# Project-Door: Sound Activated YouTube Closer & Desktop Switcher

## Description
This Python script listens for specific door sounds (like creaks or slams) using a machine learning model (YAMNet). Upon detection, it's designed to specifically close any open YouTube tab in a chosen browser (on macOS) and then switch to the next virtual desktop. This project was created to automate a specific workflow based on an auditory cue.

## Features
* Real-time audio listening via microphone.
* Door sound detection using the YAMNet pre-trained audio event classification model.
* Targets and closes specific YouTube tabs on macOS using AppleScript.
* Switches to the next virtual desktop on macOS using AppleScript.
* Configurable target sound names (from YAMNet's class list).
* Configurable confidence threshold for sound detection.
* Configurable target browser (Google Chrome or Safari on macOS).

## Platform
* **Primarily designed and tested for macOS.**
* The core functionalities of specific browser tab control and desktop switching are implemented using AppleScript, making them macOS-specific.
* The sound detection component is generally cross-platform, but the action components would require significant adaptation for Windows or Linux.

## Prerequisites
* **macOS:** (e.g., Sequoia, Sonoma, Ventura, Monterey)
* **Python:** Version 3.11 (recommended for TensorFlow compatibility on Apple Silicon Macs).
* **Homebrew:** (Recommended for installing Python 3.11 on macOS if not already available via other means).
* **`curl`:** Used by the script to download the YAMNet class map CSV if not present (usually pre-installed on macOS).
* **Python Libraries:** See `requirements.txt` (you'll create this in the setup). Key libraries include:
    * `tensorflow-macos` (for Apple Silicon Macs)
    * `tensorflow-metal` (for Apple Silicon GPU support)
    * `tensorflow_hub`
    * `numpy`
    * `sounddevice`
    * `librosa`
    * `pyautogui` (though its role for desktop switching on Mac has been superseded by AppleScript in this version)
    * `pandas`

## Setup & Installation

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/SrivanthDasu/Project-Door.git](https://github.com/SrivanthDasu/Project-Door.git)
    cd Project-Door
    ```

2.  **Create and Activate Virtual Environment (Recommended for macOS with Python 3.11):**
    * Ensure Python 3.11 is installed. If not, you can install it via [python.org](https://www.python.org/downloads/macos/) or Homebrew (`brew install python@3.11`).
    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    ```
    *(Your prompt should now start with `(venv)`)*

3.  **Install Dependencies:**
    * First, upgrade pip:
        ```bash
        pip install --upgrade pip
        ```
    * **Create `requirements.txt` (If you haven't already):** After manually installing all packages successfully in your `venv` as per previous discussions (including `tensorflow-macos`, `tensorflow-metal`, and then the rest), generate the file:
        ```bash
        pip freeze > requirements.txt
        ```
        Commit this `requirements.txt` file to your repository.
    * **Install from `requirements.txt` (for users cloning your repo):**
        ```bash
        pip install -r requirements.txt
        ```
        *(If `requirements.txt` is not yet available, users would install manually:
        `pip install tensorflow-macos tensorflow-metal tensorflow_hub numpy sounddevice librosa pyautogui pandas`)*

4.  **macOS Permissions (Crucial - Grant these when prompted or pre-emptively):**
    * **Microphone Access:**
        * Go to: System Settings > Privacy & Security > Microphone.
        * Ensure your Terminal app (e.g., `Terminal.app`, `iTerm.app`) or your code editor (e.g., VS Code, if it's running Python directly) has permission.
    * **Automation Access:**
        * Go to: System Settings > Privacy & Security > Automation.
        * Your Terminal app (or code editor) will need permission to control:
            * Your target browser (e.g., "Google Chrome", "Safari").
            * "System Events" (for AppleScript-based keystrokes and desktop switching).
        * *These permission dialogs usually pop up on the first attempt the script makes to automate an application.*
    * **Accessibility Access (Good to check):**
        * Go to: System Settings > Privacy & Security > Accessibility.
        * Ensure your Terminal app (or code editor) is listed and checked. This is often needed for `pyautogui` and some system interactions.
    * **Mission Control Keyboard Shortcuts:**
        * Go to: System Settings > Keyboard > Keyboard Shortcuts > Mission Control.
        * Ensure "Move right a space" (or similar wording for switching to the next desktop) is **enabled** and set to `^→` (Control-Right Arrow) or your preferred shortcut if you modify the script.

## Configuration
The following variables can be modified at the top of the `main.py` script:

* `TARGET_SOUND_NAMES = ["Creak", "Squeak", "Door", "Wood"]`
    * A list of sound class names from YAMNet that should trigger the actions.
* `CONFIDENCE_THRESHOLD = 0.15`
    * The minimum score (from 0.0 to 1.0) a sound needs to achieve from YAMNet to be considered a valid detection. Adjust based on sensitivity needs.
* `BROWSER_TO_TARGET = "Google Chrome"`
    * Set this to the name of the browser you want to control. Currently supported via AppleScript: `"Google Chrome"` or `"Safari"`.

## Usage
1.  Ensure your virtual environment is activated:
    ```bash
    source venv/bin/activate
    ```
2.  Run the script from your project directory:
    ```bash
    python main.py
    ```
3.  The script will print status messages, including loaded configuration, YAMNet model loading (which downloads the model on the first run), and detected sounds.
4.  To stop the script, press `Ctrl+C` in the terminal.

## How It Works (Brief Overview)
1.  **Audio Input:** `sounddevice` library captures audio from the default microphone.
2.  **Sound Classification:** Audio chunks are fed into the YAMNet model (loaded via `tensorflow_hub`), which identifies various sound events.
3.  **Detection & Trigger:** If a sound from `TARGET_SOUND_NAMES` is detected with a score meeting or exceeding `CONFIDENCE_THRESHOLD`:
    * **YouTube Tab Closing (macOS):** An AppleScript is dynamically generated and executed via `subprocess`. This script instructs `BROWSER_TO_TARGET` to find any tab with a YouTube URL, activate it, and close it using a simulated `Command+W`.
    * **Desktop Switching (macOS):** Another AppleScript is executed, telling "System Events" to simulate the `Control+Right Arrow` key combination to trigger Mission Control's "move right a space" action.

## Troubleshooting
* **`ModuleNotFoundError: No module named 'tensorflow'`:** Ensure you have activated the correct virtual environment (`venv`) where TensorFlow (specifically `tensorflow-macos` for Apple Silicon) was installed. Ensure you used a compatible Python version (e.g., 3.11) for the venv.
* **No Sound Detected / Too Sensitive:**
    * Check microphone input and system permissions.
    * Observe the console output to see what sounds YAMNet *is* detecting and their scores.
    * Adjust `TARGET_SOUND_NAMES` to include the relevant YAMNet classes for your door sound.
    * Fine-tune `CONFIDENCE_THRESHOLD` (lower for more sensitivity, higher for less).
* **Actions (Tab Closing/Desktop Switch) Not Happening on macOS:**
    * **Permissions are key!** Double-check Automation permissions for your Terminal/editor to control the browser and System Events.
    * Verify the `BROWSER_TO_TARGET` name matches your installed browser exactly.
    * Ensure Mission Control keyboard shortcuts are enabled and correctly set for desktop switching.
* **AppleScript Errors / `osascript` not found:** This script is heavily reliant on AppleScript for its actions on macOS. Ensure you are on macOS. Check the console for error messages from AppleScript.
* **`curl: command not found` (during `yamnet_class_map.csv` download):** `curl` is usually present on macOS. If not, you may need to install it (e.g., via Homebrew) or download the `yamnet_class_map.csv` file manually and place it in the script's directory.

## To-Do / Future Improvements
* [ ] Add support for Windows/Linux for specific tab closing and desktop switching.
* [ ] Create a simple GUI for configuration and status.
* [ ] Allow more advanced sound model fine-tuning for specific door sounds.
* [ ] Make actions more configurable (e.g., target different websites, perform different keyboard shortcuts).

## License
*This project is currently unlicensed. You are free to use, modify, and distribute it, but without any warranty. If you wish to formally license it, consider a permissive license like MIT.*

*(You can replace the above with your preferred license. For example, if you choose MIT License, you would create a `LICENSE.md` file with the MIT License text and change the line above to: `This project is licensed under the MIT License - see the LICENSE.md file for details`)*

## Acknowledgements
* Thanks to the developers of TensorFlow, YAMNet, and the various Python libraries that make this project possible.
