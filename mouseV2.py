import cv2
import mediapipe as mp
import pyautogui
import time

# Constants for drawing
LANDMARK_CIRCLE_RADIUS = 5
LANDMARK_CIRCLE_COLOR = (0, 235, 0)  # Green
LANDMARK_CIRCLE_THICKNESS = -1  # Filled circle
CONNECTION_LINE_COLOR = (0, 255, 0)  # Green
CONNECTION_LINE_THICKNESS = 2
CURSOR_MOVEMENT_SCALE = 5.0  # Factor to amplify the cursor movement
SMOOTHING_FACTOR = 0.2  # Exponential smoothing factor

def initialize_webcam():
    webcam = cv2.VideoCapture(0)
    webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not webcam.isOpened():
        raise RuntimeError("Error: Could not open video device.")
    return webcam

def preprocess_frame(frame):
    mirrored_frame = cv2.flip(frame, 1)  # Mirror the frame
    rgb_converted_frame = cv2.cvtColor(mirrored_frame, cv2.COLOR_BGR2RGB)
    return mirrored_frame, rgb_converted_frame

def draw_hand_landmarks(frame, hand_landmarks_list, drawing_utils):
    for hand_landmarks in hand_landmarks_list:
        drawing_utils.draw_landmarks(frame, hand_landmarks)
        landmarks = hand_landmarks.landmark
        for landmark in landmarks:
            x_coord = int(landmark.x * frame.shape[1])
            y_coord = int(landmark.y * frame.shape[0])
            cv2.circle(frame, (x_coord, y_coord), LANDMARK_CIRCLE_RADIUS, LANDMARK_CIRCLE_COLOR, LANDMARK_CIRCLE_THICKNESS)
        for connection in mp.solutions.hands.HAND_CONNECTIONS:
            start_idx, end_idx = connection
            start_x = int(landmarks[start_idx].x * frame.shape[1])
            start_y = int(landmarks[start_idx].y * frame.shape[0])
            end_x = int(landmarks[end_idx].x * frame.shape[1])
            end_y = int(landmarks[end_idx].y * frame.shape[0])
            cv2.line(frame, (start_x, start_y), (end_x, end_y), CONNECTION_LINE_COLOR, CONNECTION_LINE_THICKNESS)
    return landmarks

def extract_landmark_coordinates(landmarks, frame_width, frame_height):
    coordinates = {}
    for idx, landmark in enumerate(landmarks):
        x_coord = int(landmark.x * frame_width)
        y_coord = int(landmark.y * frame_height)
        coordinates[idx] = (x_coord, y_coord)
    return coordinates

def map_coordinates_to_screen(coordinates, screen_width, screen_height, frame_width, frame_height):
    screen_mapped_coordinates = {}
    for idx, (x_coord, y_coord) in coordinates.items():
        mapped_x = screen_width * x_coord / frame_width
        mapped_y = screen_height * y_coord / frame_height
        screen_mapped_coordinates[idx] = (mapped_x, mapped_y)
    return screen_mapped_coordinates

def update_cursor_position(index_finger_coords, prev_cursor_x, prev_cursor_y):
    index_x, index_y = index_finger_coords
    smoothed_x = (1 - SMOOTHING_FACTOR) * prev_cursor_x + SMOOTHING_FACTOR * index_x
    smoothed_y = (1 - SMOOTHING_FACTOR) * prev_cursor_y + SMOOTHING_FACTOR * index_y

    scaled_x = prev_cursor_x + (smoothed_x - prev_cursor_x) * CURSOR_MOVEMENT_SCALE
    scaled_y = prev_cursor_y + (smoothed_y - prev_cursor_y) * CURSOR_MOVEMENT_SCALE

    pyautogui.moveTo(scaled_x, scaled_y)
    return scaled_x, scaled_y

def detect_hand_gestures(coordinates, thumb_coordinates, last_click_time, click_interval_threshold, has_clicked_once):
    thumb_x, thumb_y = thumb_coordinates

    # Left click detection
    if abs(coordinates[8][1] - thumb_y) < 70:
        current_time = time.time()
        if current_time - last_click_time < click_interval_threshold:
            pyautogui.doubleClick()
            last_click_time = 0
        else:
            if not has_clicked_once:
                pyautogui.click()
                has_clicked_once = True
            last_click_time = current_time
    else:
        has_clicked_once = False

    # Scroll detection
    extended_fingers = [idx for idx in [8, 12, 16, 20] if coordinates[idx][1] < coordinates[idx - 2][1]]

    if len(extended_fingers) == 0:  # Only thumb extended
        thumb_tip_y = coordinates[4][1]
        wrist_y = coordinates[0][1]
        if thumb_tip_y < wrist_y - 40:
            pyautogui.scroll(200)
        elif thumb_tip_y > wrist_y + 40:
            pyautogui.scroll(-200)

    return last_click_time, has_clicked_once

def display_user_instructions(frame):
    instructions = [
        "Virtual Mouse Instructions:",
        "1. Move cursor: Use Index Finger",
        "2. Left Click: Bring Thumb close to Index Finger",
        "3. Scroll: Thumbs Up to Scroll Up, Thumbs Down to Scroll Down"
    ]
    initial_y, y_offset = 20, 30
    for idx, instruction in enumerate(instructions):
        y_position = initial_y + idx * y_offset
        cv2.putText(frame, instruction, (10, y_position), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

def main():
    webcam = initialize_webcam()
    hand_detector = mp.solutions.hands.Hands(max_num_hands=1)
    drawing_utils = mp.solutions.drawing_utils
    screen_width, screen_height = pyautogui.size()
    prev_cursor_x, prev_cursor_y = 0, 0
    last_click_time = 0
    click_interval_threshold = 0.3
    has_clicked_once = False
    frame_counter = 0

    while True:
        success, frame = webcam.read()
        if not success:
            print("Error: Failed to capture image.")
            break

        if frame_counter % 3 == 0:
            mirrored_frame, rgb_frame = preprocess_frame(frame)
            frame_height, frame_width, _ = mirrored_frame.shape
            detection_result = hand_detector.process(rgb_frame)
            hand_landmarks_list = detection_result.multi_hand_landmarks

            if hand_landmarks_list:
                landmarks = draw_hand_landmarks(mirrored_frame, hand_landmarks_list, drawing_utils)
                coordinates = extract_landmark_coordinates(landmarks, frame_width, frame_height)
                screen_mapped_coordinates = map_coordinates_to_screen(coordinates, screen_width, screen_height, frame_width, frame_height)
                prev_cursor_x, prev_cursor_y = update_cursor_position(screen_mapped_coordinates[8], prev_cursor_x, prev_cursor_y)
                last_click_time, has_clicked_once = detect_hand_gestures(
                    screen_mapped_coordinates, screen_mapped_coordinates[4], last_click_time, click_interval_threshold, has_clicked_once
                )

            display_user_instructions(mirrored_frame)

        cv2.imshow('Virtual Mouse', mirrored_frame)
        frame_counter += 1

        if cv2.waitKey(1) & 0xFF == 27:  # Press Esc to exit
            break

    webcam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
