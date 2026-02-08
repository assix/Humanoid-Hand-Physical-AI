import cv2
import mediapipe as mp
import time
import math
import random
import board
import busio
from adafruit_pca9685 import PCA9685

# ==========================================
# 1. HARDWARE SETUP & CALIBRATION
# ==========================================
print("Initializing Robot Driver...")
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    pca = PCA9685(i2c)
    pca.frequency = 60 
except:
    print("Hardware Error: Check I2C connection.")

# --- GLOBAL SAFETY LIMITS ---
# Keeps motors from hitting physical stops (Anti-Buzz)
SAFE_MIN = 3000  
SAFE_MAX = 9000 

# --- FINGER MAPPING (Your Custom Wiring) ---
FINGER_5 = 2  # Thumb
FINGER_4 = 0  # Index
FINGER_3 = 1  # Middle
FINGER_2 = 3  # Ring
FINGER_1 = 4  # Pinky

# Track current state of each finger (for toggle mode)
finger_states = {
    FINGER_1: "RELAX", FINGER_2: "RELAX", FINGER_3: "RELAX",
    FINGER_4: "RELAX", FINGER_5: "RELAX"
}

def set_finger(channel, state):
    """
    Moves a specific finger to OPEN, CLOSED, or RELAX.
    Includes custom calibration for specific fingers to stop buzzing.
    """
    finger_states[channel] = state
    
    # Default Limits
    limit_min = SAFE_MIN
    limit_max = SAFE_MAX
    
    # --- INDIVIDUAL FINGER CALIBRATION ---
    # Adjustments based on your previous testing
    if channel == 3:  # Ring
        limit_max = 7500
        limit_min = 4500
    if channel == 1:  # Middle
        limit_min = 4500
        limit_max = 7500
    if channel == 0:  # Index
        limit_min = 4500
        
    # --- DIRECTION LOGIC ---
    # Fingers 1 & 2 (Pinky/Ring) are REVERSED logic
    if channel == FINGER_1 or channel == FINGER_2:
        val_open = limit_max
        val_closed = limit_min
    else:
        # Fingers 3, 4, 5 are STANDARD logic
        val_open = limit_min
        val_closed = limit_max

    # Send Signal
    if state == "OPEN":
        pca.channels[channel].duty_cycle = val_open
    elif state == "CLOSED":
        pca.channels[channel].duty_cycle = val_closed
    elif state == "RELAX":
        pca.channels[channel].duty_cycle = 0

def toggle_finger(channel):
    """Helper to switch a finger state manually"""
    current = finger_states.get(channel, "RELAX")
    if current == "OPEN":
        set_finger(channel, "CLOSED")
    else:
        set_finger(channel, "OPEN")

def relax_all():
    """Cuts power to all motors"""
    for i in range(5): pca.channels[i].duty_cycle = 0

# ==========================================
# 2. ROBOT MOVES
# ==========================================

def move_rock():
    # Close 1-5
    for i in range(5): set_finger(i, "CLOSED")

def move_paper():
    # Open 1-5
    for i in range(5): set_finger(i, "OPEN")

def move_scissors():
    # 1. Flair (Open All)
    move_paper()
    time.sleep(0.2)
    
    # 2. Form Scissors
    # OPEN: Ring(2) & Middle(3)
    # CLOSED: Pinky(1), Index(4), Thumb(5)
    set_finger(FINGER_1, "CLOSED") 
    set_finger(FINGER_2, "OPEN")   
    set_finger(FINGER_3, "OPEN")   
    set_finger(FINGER_4, "CLOSED") 
    set_finger(FINGER_5, "CLOSED") 

# ==========================================
# 3. AI & GAME LOGIC
# ==========================================
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

def calculate_distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def get_user_gesture(landmarks):
    """Determines if user is showing Rock, Paper, or Scissors"""
    fingers = []
    wrist = landmarks[0]
    tips = [8, 12, 16, 20]
    bases = [5, 9, 13, 17]
    
    # Thumb Logic (Distance to Pinky Base)
    if calculate_distance(landmarks[4], landmarks[17]) > 0.2:
        fingers.append(1) # Open
    else:
        fingers.append(0) # Closed

    # Finger Logic (Distance from Wrist)
    for i in range(4):
        dist_tip = calculate_distance(wrist, landmarks[tips[i]])
        dist_base = calculate_distance(wrist, landmarks[bases[i]])
        if dist_tip > dist_base + 0.02:
            fingers.append(1)
        else:
            fingers.append(0)

    total = sum(fingers)
    if total == 0: return "ROCK"
    if total == 5: return "PAPER"
    if total == 2 and fingers[1]==1 and fingers[2]==1: return "SCISSORS"
    return "UNKNOWN"

def get_winner(user, robot):
    if user == robot: return "TIE"
    if (user == "ROCK" and robot == "SCISSORS") or \
       (user == "PAPER" and robot == "ROCK") or \
       (user == "SCISSORS" and robot == "PAPER"):
        return "YOU WIN"
    return "ROBOT WINS"

# ==========================================
# 4. MAIN LOOP
# ==========================================
cap = cv2.VideoCapture(0)
window_name = "Robot Control Panel"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 800, 600)

mode = "TEST" 
current_state = "RELAXED"

# Game Variables
game_state = "IDLE"
timer_start = 0
locked_user = "..."
locked_robot = "..."
result_text = "..."
score_user = 0
score_robot = 0
rounds_played = 0

print("--- ROBOT ONLINE ---")
relax_all() # Silent Start

try:
    while True:
        # Handle Window Close
        try:
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1: break
        except: break

        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        
        user_gesture = "UNKNOWN"
        
        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)
                user_gesture = get_user_gesture(hand_lms.landmark)

        # ----------------------
        # MODE: MIMIC
        # ----------------------
        if mode == "MIMIC":
            if user_gesture == "ROCK": 
                move_rock()
                current_state = "ROCK"
            elif user_gesture == "PAPER": 
                move_paper()
                current_state = "PAPER"
            elif user_gesture == "SCISSORS": 
                move_scissors()
                current_state = "SCISSORS"

        # ----------------------
        # MODE: GAME
        # ----------------------
        if mode == "GAME":
            elapsed = time.time() - timer_start
            
            if game_state == "COUNTDOWN":
                left = 3 - int(elapsed)
                if left <= 0:
                    game_state = "SHOWDOWN"
                else:
                    # Draw Big Countdown
                    cv2.putText(frame, str(left), (350, 240), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 255), 5)
            
            elif game_state == "SHOWDOWN":
                locked_user = user_gesture
                if locked_user == "UNKNOWN": locked_user = "ROCK" # Penalty for bad tracking
                
                # Pick Random Move
                moves = ["ROCK", "PAPER", "SCISSORS"]
                locked_robot = moves[random.randint(0, 2)]
                
                # EXECUTE ROBOT MOVE
                if locked_robot == "ROCK": move_rock()
                elif locked_robot == "PAPER": move_paper()
                elif locked_robot == "SCISSORS": move_scissors()
                
                current_state = locked_robot
                result_text = get_winner(locked_user, locked_robot)
                
                # Score Logic
                if "YOU WIN" in result_text: score_user += 1
                elif "ROBOT WINS" in result_text: score_robot += 1
                
                rounds_played += 1
                game_state = "RESULT"
                timer_start = time.time()
                
            elif game_state == "RESULT":
                # Show Result for 3 Seconds
                cv2.putText(frame, f"YOU: {locked_user}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, f"ROBOT: {locked_robot}", (450, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                col = (0, 255, 255) # Tie = Yellow
                if "YOU" in result_text: col = (0, 255, 0) # Win = Green
                elif "ROBOT" in result_text: col = (0, 0, 255) # Loss = Red
                
                cv2.putText(frame, result_text, (150, 300), cv2.FONT_HERSHEY_SIMPLEX, 2, col, 4)
                
                if time.time() - timer_start > 3.0:
                    game_state = "COUNTDOWN"
                    timer_start = time.time()

        # ----------------------
        # DRAW UI OVERLAY
        # ----------------------
        h, w, _ = frame.shape
        
        # Top Info Bar
        cv2.rectangle(frame, (0, 0), (w, 60), (40, 40, 40), -1)
        cv2.putText(frame, f"MODE: {mode}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(frame, f"ROBOT: {current_state}", (300, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Scoreboard (Visible always)
        if mode == "GAME":
            cv2.putText(frame, f"ROBOT: {score_robot}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 255), 2)
            cv2.putText(frame, f"YOU: {score_user}", (w-200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 100), 2)
        else:
            cv2.putText(frame, f"DETECTED: {user_gesture}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)

        # Bottom Controls
        cv2.rectangle(frame, (0, h-100), (w, h), (40, 40, 40), -1)
        cv2.putText(frame, "[X]: Start Game   [M]: Mimic   [T]: Manual Test   [SPACE]: Relax", (20, h-60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(frame, "[R]ock [P]aper [S]cissors  |  [1-5] Toggle Fingers  |  [Q]uit", (20, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        cv2.imshow(window_name, frame)

        # ----------------------
        # KEYBOARD CONTROLS
        # ----------------------
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'): 
            break
        elif key == ord(' '): 
            mode = "TEST"
            current_state = "RELAXING..."
            relax_all()
            current_state = "LOOSE"
        elif key == ord('m'):
            mode = "MIMIC"
            current_state = "WATCHING..."
        elif key == ord('t'):
            mode = "TEST"
            current_state = "MANUAL"
        elif key == ord('x'):
            mode = "GAME"
            game_state = "COUNTDOWN"
            timer_start = time.time()
            score_user = 0
            score_robot = 0
            current_state = "GAME ON"
        
        # Manual Triggers (TEST Mode Only)
        if mode == "TEST":
            if key == ord('r'):
                move_rock()
                current_state = "ROCK"
            elif key == ord('p'):
                move_paper()
                current_state = "PAPER"
            elif key == ord('s'):
                move_scissors()
                current_state = "SCISSORS"
            # Finger Toggles
            elif key == ord('1'): toggle_finger(FINGER_1)
            elif key == ord('2'): toggle_finger(FINGER_2)
            elif key == ord('3'): toggle_finger(FINGER_3)
            elif key == ord('4'): toggle_finger(FINGER_4)
            elif key == ord('5'): toggle_finger(FINGER_5)

finally:
    print("Shutting down & Loosening motors...")
    cap.release()
    cv2.destroyAllWindows()
    relax_all()