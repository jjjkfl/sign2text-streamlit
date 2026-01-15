import streamlit as st
import cv2
import pickle
import mediapipe as mp
import numpy as np
import time
import warnings

warnings.filterwarnings("ignore")

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ISL – The Upside Down",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- STRANGER THINGS INTRO ----------------
if "intro_shown" not in st.session_state:
    st.session_state.intro_shown = False

if not st.session_state.intro_shown:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
    
    .intro-screen {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100vh;
        background: #000;
        z-index: 10000;
        display: flex;
        justify-content: center;
        align-items: center;
        animation: fadeOut 1s ease-out 7s forwards;
    }
    
    @keyframes fadeOut {
        to {
            opacity: 0;
            visibility: hidden;
        }
    }
    
    .st-logo {
        font-family: 'Creepster', cursive;
        text-align: center;
        position: relative;
        opacity: 0;
        animation: logoAppear 3s ease-out 0.5s forwards;
    }
    
    @keyframes logoAppear {
        0% {
            opacity: 0;
            transform: scale(4) translateZ(200px);
            filter: blur(30px);
        }
        50% {
            opacity: 0.8;
            filter: blur(10px);
        }
        100% {
            opacity: 1;
            transform: scale(1) translateZ(0);
            filter: blur(0);
        }
    }
    
    .logo-line1 {
        font-size: 2.5rem;
        color: #ff6666;
        display: block;
        line-height: 0.9;
        animation: glowPulse 2s ease-in-out 3.5s infinite;
    }
    
    .logo-line2 {
        font-size: 5rem;
        color: #ff0000;
        display: block;
        line-height: 0.9;
        text-shadow: 
            0 0 10px #ff0000,
            0 0 20px #ff0000,
            0 0 30px #ff0000,
            0 0 40px #8b0000,
            0 0 70px #8b0000,
            0 0 100px #8b0000;
        animation: flicker 2s infinite 3.5s, glowPulse 2s ease-in-out 3.5s infinite;
    }
    
    .logo-line3 {
        font-size: 2rem;
        color: #ffaaaa;
        display: block;
        line-height: 0.9;
        animation: glowPulse 2s ease-in-out 3.5s infinite;
    }
    
    @keyframes flicker {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.85; }
        51% { opacity: 1; }
        60% { opacity: 0.92; }
        61% { opacity: 1; }
    }
    
    @keyframes glowPulse {
        0%, 100% { 
            text-shadow: 
                0 0 10px currentColor,
                0 0 20px currentColor,
                0 0 30px currentColor;
        }
        50% { 
            text-shadow: 
                0 0 20px currentColor,
                0 0 30px currentColor,
                0 0 40px currentColor,
                0 0 50px currentColor;
        }
    }
    
    .st-subtitle {
        font-family: 'Courier New', monospace;
        font-size: 1rem;
        margin-top: 3rem;
        opacity: 0;
        animation: subtitleAppear 2s ease-out 4s forwards;
        letter-spacing: 8px;
        text-transform: uppercase;
        color: #888;
    }
    
    @keyframes subtitleAppear {
        to {
            opacity: 1;
        }
    }
    
    /* Particle effects */
    .particle {
        position: fixed;
        width: 2px;
        height: 2px;
        background: rgba(255, 50, 50, 0.6);
        border-radius: 50%;
        animation: floatParticle 12s infinite;
        z-index: 9999;
    }
    
    @keyframes floatParticle {
        0%, 100% {
            transform: translateY(100vh) translateX(0);
            opacity: 0;
        }
        10% {
            opacity: 1;
        }
        90% {
            opacity: 1;
        }
        100% {
            transform: translateY(-100vh) translateX(30px);
            opacity: 0;
        }
    }
    </style>
    
    <div class="intro-screen">
        <div>
            <div class="st-logo">
                <span class="logo-line1">REAL TIME</span>
                <span class="logo-line2">ISL</span>
                <span class="logo-line3">TRANSLATION SYSTEM</span>
            </div>
            <div class="st-subtitle">A Communication Portal</div>
        </div>
    </div>
    
    <script>
    for(let i = 0; i < 25; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 12 + 's';
        particle.style.animationDuration = (Math.random() * 8 + 8) + 's';
        document.body.appendChild(particle);
    }
    
    setTimeout(() => {
        const intro = document.querySelector('.intro-screen');
        if(intro) intro.remove();
    }, 8000);
    </script>
    """, unsafe_allow_html=True)
    
    # Auto-advance after intro
    time.sleep(8)
    st.session_state.intro_shown = True
    st.rerun()

# ---------------- STRANGER THINGS THEME ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Creepster&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Special+Elite&display=swap');

.stApp {
    background: linear-gradient(180deg, #0a0a0a 0%, #1a0000 50%, #000 100%);
}

.main-title {
    font-family: 'Creepster', cursive;
    font-size: 4rem;
    text-align: center;
    color: #ff0000;
    text-shadow: 0 0 25px #ff0000;
}

.subtitle {
    text-align: center;
    font-family: 'Special Elite', cursive;
    color: #ff6666;
    letter-spacing: 3px;
    margin-bottom: 2rem;
}

.output-box {
    background: #000;
    border: 3px solid #ff0000;
    border-radius: 10px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 0 20px rgba(255,0,0,0.5);
}

.predicted-char {
    font-family: 'Creepster', cursive;
    font-size: 4rem;
    color: #00ff00;
    text-shadow: 0 0 30px #00ff00;
}

.waiting {
    font-family: 'Special Elite', cursive;
    color: #ff6666;
    letter-spacing: 2px;
}

.stButton > button {
    background: rgba(139,0,0,0.85);
    color: white;
    border: 2px solid #ff0000;
    font-family: 'Special Elite', cursive;
}

#MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown("""
<div class="main-title">ISL REAL TIME<br>TRANSLATION</div>
<div class="subtitle">⚡ COMMUNICATION FROM THE UPSIDE DOWN ⚡</div>
""", unsafe_allow_html=True)

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_model():
    with open("model.p", "rb") as f:
        return pickle.load(f)["model"]

model = load_model()

# ---------------- MEDIAPIPE ----------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.3,
    min_tracking_confidence=0.3
)

# ---------------- LABELS ----------------
LABELS = {
    0:'A', 1:'B', 2:'C', 3:'D', 4:'E', 5:'F', 6:'G',
    7:'H', 8:'I', 9:'J', 10:'K', 11:'L', 12:'M',
    13:'N', 14:'O', 15:'P', 16:'Q', 17:'R',
    18:'S', 19:'T', 20:'U', 21:'V', 22:'W',
    23:'X', 24:'Y', 25:'Z',
    26:'Hello',
    27:'Done',
    28:'Thank You',
    29:'I Love You',
    30:'Sorry',
    31:'Please',
    32:'You are welcome'
}

# ---------------- SESSION STATE ----------------
if "running" not in st.session_state:
    st.session_state.running = False

if "text" not in st.session_state:
    st.session_state.text = ""

# ---------------- LAYOUT ----------------
left, right = st.columns(2)

with left:
    st.subheader("🎥 THE PORTAL")
    frame_box = st.empty()

    c1, c2, c3 = st.columns(3)
    with c1:
        start = st.button("🔮 START")
    with c2:
        stop = st.button("⛔ STOP")
    with c3:
        reset = st.button("🔄 RESET")

with right:
    st.subheader("🔮 OUTPUT")
    output_box = st.empty()

    st.subheader("📝 COLLECTED MESSAGE")
    message_box = st.empty()

    st.subheader("📖 ANCIENT CODEX")

    img_col1, img_col2 = st.columns(2)

    with img_col1:
        st.image(
            "sign language 2.jpg",
            caption="Custom Sign Reference"
        )

    with img_col2:
        st.image(
            "https://raw.githubusercontent.com/uzibytes/Sign2Text/master/hand-signs-of-the-ASL-Language.png",
            caption="ASL Alphabet Chart"
        )

# ---------------- BUTTON LOGIC ----------------
if start:
    st.session_state.running = True

if stop:
    st.session_state.running = False

if reset:
    st.session_state.text = ""

# ---------------- CAMERA LOOP ----------------
if st.session_state.running:
    cap = cv2.VideoCapture(0)

    last_prediction = None
    last_time = time.time()
    delay = 1.2

    while st.session_state.running:
        ret, frame = cap.read()
        if not ret:
            st.error("Camera error")
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        predicted = None

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )

                x_, y_, data = [], [], []
                for lm in hand_landmarks.landmark:
                    x_.append(lm.x)
                    y_.append(lm.y)

                for lm in hand_landmarks.landmark:
                    data.append(lm.x - min(x_))
                    data.append(lm.y - min(y_))

                try:
                    pred = model.predict([np.array(data)])
                    predicted = LABELS[int(pred[0])]

                    current_time = time.time()
                    if predicted == last_prediction and current_time - last_time > delay:
                        if len(predicted) > 1:
                            st.session_state.text += predicted + " "
                        else:
                            st.session_state.text += predicted
                        last_time = current_time

                    last_prediction = predicted
                except:
                    pass

        frame_box.image(frame, channels="BGR")

        if predicted:
            output_box.markdown(
                f"<div class='output-box'><div class='predicted-char'>{predicted}</div></div>",
                unsafe_allow_html=True
            )
        else:
            output_box.markdown(
                "<div class='output-box'><div class='waiting'>AWAITING TRANSMISSION...</div></div>",
                unsafe_allow_html=True
            )

        message_box.markdown(
            f"<div class='output-box'><div class='waiting'>{st.session_state.text or '...'}</div></div>",
            unsafe_allow_html=True
        )

        time.sleep(0.05)

    cap.release()
else:
    output_box.markdown(
        "<div class='output-box'><div class='waiting'>PORTAL INACTIVE</div></div>",
        unsafe_allow_html=True
    )

    message_box.markdown(
        f"<div class='output-box'><div class='waiting'>{st.session_state.text or '...'}</div></div>",
        unsafe_allow_html=True
    )