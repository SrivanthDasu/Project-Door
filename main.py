import sounddevice as sd
import numpy as np
# import librosa # Not strictly needed for this version's input handling
import tensorflow as tf
import tensorflow_hub as hub
import pandas as pd
import pyautogui # Still used for other OS, or if AppleScript fails as a concept
import time
import platform
import os
import subprocess # For running AppleScript

# --- Configuration ---
# You can adjust these!
TARGET_SOUND_NAMES = ["Creak", "Squeak", "Door", "Wood"] # Sounds YAMNet should react to
CONFIDENCE_THRESHOLD = 0.1  # Minimum confidence score (0.0 to 1.0) to trigger - User updated
BROWSER_TO_TARGET = "Google Chrome"  # <<<< IMPORTANT: Set this to "Google Chrome" or "Safari"

MODEL_SAMPLE_RATE = 16000   # YAMNet expects 16kHz audio
CHUNK_DURATION_S = 0.975    # YAMNet's frame size is 0.975s
CHUNK_SAMPLES = int(MODEL_SAMPLE_RATE * CHUNK_DURATION_S)
STREAM_BUFFER_SECONDS = 3 # How many seconds of audio to keep in a rolling buffer

# --- Global Variables for Model and Class Names ---
yamnet_model = None
yamnet_class_names = None

def load_yamnet_model_and_classes():
    global yamnet_model, yamnet_class_names
    if yamnet_model is not None and yamnet_class_names is not None:
        return True

    print("Loading YAMNet model from TensorFlow Hub...")
    try:
        yamnet_model = hub.load('https://tfhub.dev/google/yamnet/1')
        print("YAMNet model loaded successfully.")
        
        script_dir = os.path.dirname(__file__)
        if not script_dir:
            script_dir = os.getcwd() 
        class_map_path = os.path.join(script_dir, "yamnet_class_map.csv")
        
        if not os.path.exists(class_map_path):
            print(f"yamnet_class_map.csv not found in script directory. Attempting to download...")
            class_map_url = "https://raw.githubusercontent.com/tensorflow/models/master/research/audioset/yamnet/yamnet_class_map.csv"
            try:
                subprocess.run(["curl", "-s", "-o", class_map_path, class_map_url], check=True)
                print("Successfully downloaded yamnet_class_map.csv.")
            except FileNotFoundError: 
                 print("Error: 'curl' command not found. Cannot download class map automatically.")
                 print(f"Please download it manually from {class_map_url} and place it in {script_dir}")
                 return False
            except subprocess.CalledProcessError as e: 
                print(f"Could not download class map using curl (return code {e.returncode}): {e.stderr}")
                print(f"Please download it manually from {class_map_url} and place it in {script_dir}")
                return False
            except Exception as e: 
                print(f"An unexpected error occurred during class map download: {e}")
                return False

        class_map_df = pd.read_csv(class_map_path)
        yamnet_class_names = class_map_df['display_name'].tolist()
        print("YAMNet class names loaded.")
        return True
        
    except Exception as e:
        print(f"Error loading YAMNet model or class map: {e}")
        print("Please ensure you have an internet connection for the first model download,")
        print("and that TensorFlow and TensorFlow Hub are installed correctly.")
        return False

def close_youtube_tab_macos(browser_name="Google Chrome"):
    print(f"Attempting to close YouTube tab in {browser_name}...")
    script = f'''
    on isRunning(appName)
        tell application "System Events" to (name of processes) contains appName
    end isRunning

    if not isRunning("{browser_name}") then
        return "{browser_name} is not running."
    end if

    tell application "{browser_name}"
        set window_list to every window
        if (count of window_list) is 0 then
            return "No windows open in {browser_name}."
        end if
        repeat with current_window in window_list
            try
                set tab_list to every tab of current_window
                repeat with i from 1 to count of tab_list
                    set current_tab to item i of tab_list
                    if URL of current_tab contains "www.youtube.com" then 
                        set active tab index of current_window to i
                        set index of current_window to 1
                        activate
                        delay 0.5
                        tell application "System Events" to keystroke "w" using command down
                        return "YouTube tab closed in {browser_name}"
                    end if
                end repeat
            on error errMsg number errorNum
                -- Can log error: return "Error processing tabs: " & errMsg
            end try
        end repeat
        return "No YouTube tab found in {browser_name}"
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, check=False, timeout=10)
        output = result.stdout.strip()
        if result.returncode == 0:
            print(output)
            if "YouTube tab closed" in output:
                return True
        else:
            print(f"AppleScript error for {browser_name}:")
            if output: print(f"Stdout: {output}")
            if result.stderr: print(f"Stderr: {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        print(f"AppleScript timed out while trying to control {browser_name}.")
    except FileNotFoundError:
        print("Error: 'osascript' command not found. This script relies on AppleScript on macOS.")
    except Exception as e:
        print(f"An unexpected error occurred while running AppleScript for {browser_name}: {e}")
    return False

def switch_to_desktop_2(): # <<<< FUNCTION MODIFIED HERE
    print("Attempting to switch to the next desktop (right)...")
    try:
        time.sleep(0.3) # Slightly increased delay to ensure focus is settled after tab close
        if platform.system() == "Darwin": # macOS
            # Using AppleScript to simulate Ctrl+Right Arrow for Mission Control
            # Key code 124 is Right Arrow.
            applescript_for_desktop_switch = '''
            tell application "System Events"
                key code 124 using {control down}
            end tell
            '''
            subprocess.run(['osascript', '-e', applescript_for_desktop_switch], check=False)
            print("macOS command to switch to desktop to the right sent via AppleScript. Ensure Mission Control shortcuts are enabled.")
        # elif platform.system() == "Windows": # Example for Windows if you were to use it
        #     pyautogui.hotkey('ctrl', 'win', 'right')
        #     print("Windows command to switch to desktop to the right sent.")
        else:
            print(f"Desktop switching for {platform.system()} not explicitly implemented beyond macOS for this action.")
        # print("Desktop switch command potentially sent.") # Kept this for consistency
    except Exception as e:
        print(f"Error switching desktops: {e}")

audio_buffer = np.array([], dtype=np.float32)

def audio_callback(indata, frames, time_info, status):
    global audio_buffer
    if status:
        print(f"Audio Stream Status: {status}", flush=True)
    
    mono_indata = indata.flatten()
    if indata.ndim > 1 and indata.shape[1] > 1:
        mono_indata = np.mean(indata, axis=1)
    
    audio_buffer = np.concatenate((audio_buffer, mono_indata))
    max_buffer_length = MODEL_SAMPLE_RATE * STREAM_BUFFER_SECONDS
    if len(audio_buffer) > max_buffer_length:
        audio_buffer = audio_buffer[-max_buffer_length:]

def process_audio_buffer():
    global audio_buffer, yamnet_model, yamnet_class_names
    if yamnet_model is None or yamnet_class_names is None: return False
    
    detected_target_sound = False
    if len(audio_buffer) >= CHUNK_SAMPLES:
        waveform = audio_buffer[-CHUNK_SAMPLES:].astype(np.float32)
        try:
            scores, _, _ = yamnet_model(waveform) 
            scores = scores.numpy().mean(axis=0)
            top_class_indices = np.argsort(scores)[::-1]

            for i in range(min(10, len(top_class_indices))): 
                class_index = top_class_indices[i]
                class_name = yamnet_class_names[class_index]
                score = scores[class_index]
                if class_name in TARGET_SOUND_NAMES and score >= CONFIDENCE_THRESHOLD:
                    print(f"!!! TARGET SOUND DETECTED: {class_name} (Score: {score:.3f}) !!!", flush=True)
                    detected_target_sound = True
                    break
            
            if detected_target_sound:
                audio_buffer = np.array([], dtype=np.float32) 
                return True
        except Exception as e:
            print(f"Error during YAMNet inference: {e}", flush=True)
            if len(audio_buffer) >= CHUNK_SAMPLES:
                 audio_buffer = audio_buffer[CHUNK_SAMPLES:]
    return False

if __name__ == "__main__":
    if not load_yamnet_model_and_classes():
        print("Exiting due to failure to load YAMNet model or class map.", flush=True)
        exit()

    print("\nStarting door sound listener (YouTube closer mode for macOS)...", flush=True)
    print(f"Target browser for YouTube: {BROWSER_TO_TARGET}", flush=True)
    print(f"Target sounds: {TARGET_SOUND_NAMES}", flush=True)
    print(f"Confidence threshold: {CONFIDENCE_THRESHOLD:.2f}", flush=True) 
    print("Make sure the target browser is running and permissions are granted.", flush=True)
    print("Press Ctrl+C to stop.", flush=True)
    
    try:
        device_info = sd.query_devices(kind='input')
        input_sample_rate = device_info['default_samplerate']
        print(f"Using default input device with sample rate: {input_sample_rate} Hz", flush=True)
    except Exception as e:
        print(f"Could not query audio devices: {e}. Assuming {MODEL_SAMPLE_RATE} Hz for input.", flush=True)
        input_sample_rate = MODEL_SAMPLE_RATE

    stream = None
    try:
        stream = sd.InputStream(
            callback=audio_callback, 
            samplerate=input_sample_rate,
            channels=1, 
            dtype='float32',
            blocksize=int(input_sample_rate * CHUNK_DURATION_S / 2) 
        )
        stream.start()
        print("Audio stream started. Listening...", flush=True)
            
        while True:
            if process_audio_buffer():
                print("Action triggered by sound detection!", flush=True)
                action_successful = False
                if platform.system() == "Darwin":
                    if close_youtube_tab_macos(BROWSER_TO_TARGET):
                        action_successful = True
                    else:
                        print(f"Could not specifically close a YouTube tab in {BROWSER_TO_TARGET}.", flush=True)
                else:
                    print("Specific YouTube tab closing is only implemented for macOS.", flush=True)

                if action_successful:
                    # This function now uses AppleScript for desktop switching on macOS
                    switch_to_desktop_2() 
                    print("Actions completed. Resuming listening in 3 seconds...", flush=True)
                else:
                    print("Primary action (closing tab) failed or not applicable. Resuming listening in 3 seconds...", flush=True)
                
                time.sleep(3) 
                audio_buffer = np.array([], dtype=np.float32) 
            
            time.sleep(CHUNK_DURATION_S / 3)

    except KeyboardInterrupt:
        print("\nStopping listener.", flush=True)
    except Exception as e:
        print(f"An UNEXPECTED ERROR occurred in the main loop: {e}", flush=True)
        import traceback
        traceback.print_exc() 
        if "PortAudio" in str(e) or "jack server" in str(e).lower() or "No Default Input Device" in str(e):
            print("\n--- Audio System Error ---")
            print("1. Check microphone connection & selection (System Settings > Sound > Input).")
            print("2. Check Python/Terminal microphone permissions (System Settings > Privacy & Security > Microphone).")
    finally:
        if stream is not None and stream.active:
            print("Stopping audio stream.", flush=True)
            stream.stop()
            stream.close()
        print("Listener stopped.", flush=True)