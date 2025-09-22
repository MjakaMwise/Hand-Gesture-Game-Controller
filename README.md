# Hand Gesture  Mouse Conrtroller

## Description
Hand-Gesture-Controlled Mouse allows you to control your computer's mouse using hand gestures tracked by your webcam. It uses real-time hand tracking to move the cursor, click, drag, right-click, and scroll based on gestures.

## Features
- Move the cursor using the index finger.
- Left click by bringing the thumb close to the index finger.
- Right click by bringing the thumb close to the middle finger.
- Drag by holding the thumb close to the ring finger.
- Scroll up or down using thumbs-up or thumbs-down gestures.
- Real-time hand tracking using MediaPipe Hands.

## Requirements
- Python 3.x
- Webcam
- Python libraries:
  - `opencv-python`
  - `mediapipe`
  - `pyautogui`

## Installation

### Option 1: Using `requirements.txt`
1. Create a file named `requirements.txt` in your project folder with the following content:
    ```
    opencv-python
    mediapipe
    pyautogui
    ```
2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Option 2: Install manually
Run:
```bash
pip install opencv-python mediapipe pyautogui
````

## How to Use

1. Run the Python script:

   ```bash
   python mouse.py
   ```
2. Allow access to your webcam.
3. Use hand gestures to control the mouse:

   * Pinch your thumb and index finger for left click.
   * Bring thumb close to the middle finger for right click.
   * Hold thumb close to the ring finger to drag.
   * Thumbs up/down to scroll.
4. Press `Esc` to exit the program.

## Notes

* Ensure your hand is clearly visible to the webcam for accurate tracking.
* Move your hand slowly for smoother cursor control.
* Bright lighting improves hand detection accuracy.
* Only one hand is tracked at a time.

```
