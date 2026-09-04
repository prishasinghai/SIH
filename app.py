import streamlit as st
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import easyocr
import cv2
import numpy as np
import io

# Initialize Page Setting
st.set_page_config(page_title="AI Swasthya Voice Portal", page_icon="🎙️", layout="centered")

st.title("🏥 Voice & Vision AI Patient Intake Portal")
st.caption("First-Year BTech Prototype: Speech & OCR Driven Routing")

# Helper function to generate and play voice audio back to the patient
def speak_text(text_to_speak, key):
    try:
        tts = gTTS(text=text_to_speak, lang='en', slow=False)
        sound_file = io.BytesIO()
        tts.write_to_fp(sound_file)
        st.audio(sound_file, format="audio/mp3", start_time=0)
    except Exception as e:
        st.error(f"Audio engine delay: {e}")

# Cache the AI text-reader model so it doesn't slow down the site on every button click
@st.cache_resource
def load_ocr_reader():
    return easyocr.Reader(['en'])

reader = load_ocr_reader()

# --- SECTION 1: VOICE INTAKE ---
st.header("1. 🎙️ Speak Your Symptoms & Profile")
st.write("Click the button below and describe your name, age, and current symptoms clearly.")

# Audio voice-to-text recording widget
spoken_text = speech_to_text(
    start_prompt="🔴 Start Recording Voice",
    stop_prompt="⏹️ Stop & Process Voice",
    language='en',
    use_container_width=True,
    key='intake_mic'
)

if spoken_text:
    st.success("✨ Voice Successfully Converted to Text!")
    st.info(f'**What you said:** "{spoken_text}"')
    st.session_state['voice_transcript'] = spoken_text.lower()
else:
    if 'voice_transcript' not in st.session_state:
        st.session_state['voice_transcript'] = ""

# --- SECTION 2: PRESCRIPTION OCR ---
st.divider()
st.header("2. 📸 Upload Past Paper Prescription")
st.write("Add previous medical notes or treatment files to screen for chronic history.")

uploaded_image = st.file_uploader("Snap or Upload a prescription photo", type=["png", "jpg", "jpeg"])
ocr_extracted_text = ""

if uploaded_image is not None:
    # Convert uploaded image to structural format for AI Reading
    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    opencv_image = cv2.imdecode(file_bytes, 1)
    
    with st.spinner("AI Reading handwriting & text from prescription..."):
        # Run EasyOCR prediction
        ocr_result = reader.readtext(opencv_image, detail=0)
        ocr_extracted_text = " ".join(ocr_result).lower()
        
    st.success("✓ AI Character Extraction Finished!")
    with st.expander("📄 View Extracted Text Matrix"):
        st.write(ocr_extracted_text)

# --- SECTION 3: ADAPTIVE SCREENING & DIAGNOSTIC RECOMMENDATION ---
if st.session_state['voice_transcript'] or ocr_extracted_text:
    st.divider()
    st.header("3. 🩺 Intelligent Clinical Guidance")
    
    # Combine inputs to diagnose the target workflow
    combined_health_profile = st.session_state['voice_transcript'] + " " + ocr_extracted_text
    
    # Baseline Adaptive Evaluation Math
    is_ortho = any(word in combined_health_profile for word in ["joint", "pain", "stiffness", "knee", "bone", "arthritis"])
    is_cardio = any(word in combined_health_profile for word in ["heart", "chest", "breathing", "pressure", "bp", "hypertension"])
    
    # Trigger Dynamic Adaptive Followup Questions
    st.subheader("💡 Tailored AI Follow-up Question:")
    
    if is_ortho:
        question = "Based on your joint pain indicators, does your stiffness significantly worsen during cold weather mornings or after heavy meals?"
        st.warning(f"🤖 **Question:** {question}")
        speak_text(question, key="ortho_q")
        
        # User answers next step via voice
        st.write("Speak your answer:")
        ans_ortho = speech_to_text(start_prompt="🎙️ Record Answer to Question", stop_prompt="⏹️ Save Answer", language='en', key='ans_ortho')
        if ans_ortho:
            st.write(f"*Your Answer:* {ans_ortho}")

        # Final Clinic / Doctor Routing
        st.markdown("### 📍 Your Assigned Doctor & Clinic Allocation")
        rec_text = "Please report to the AYUSH Integrated Rheumatology & Musculoskeletal Clinic at Block C. You will be visiting Dr. Anand Sharma, Chief Ayurvedic Orthopedic Specialist."
        st.success(rec_text)
        speak_text(rec_text, key="ortho_rec")

    elif is_cardio:
        question = "Since cardiovascular patterns are detected, are you experiencing any active numbness in your left arm or sudden cold sweats?"
        st.error(f"🤖 **Question:** {question}")
        speak_text(question, key="cardio_q")
        
        st.write("Speak your answer:")
        ans_cardio = speech_to_text(start_prompt="🎙️ Record Answer to Question", stop_prompt="⏹️ Save Answer", language='en', key='ans_cardio')
        if ans_cardio:
            st.write(f"*Your Answer:* {ans_cardio}")

        st.markdown("### 📍 Your Assigned Doctor & Clinic Allocation")
        rec_text = "Please report to the Primary Preventive Cardiology Clinic at Block A, Room 102. You are scheduled with Dr. Kiran Rao, Senior Consultant Cardiologist."
        st.success(rec_text)
        speak_text(rec_text, key="cardio_rec")

    else:
        # Standard fallback if keywords don't match specific specialties
        question = "Could you tell me if you have an active fever or if this issue has been bothering you for more than three days?"
        st.info(f"🤖 **Question:** {question}")
        speak_text(question, key="gen_q")
        
        st.write("Speak your answer:")
        ans_gen = speech_to_text(start_prompt="🎙️ Record Answer to Question", stop_prompt="⏹️ Save Answer", language='en', key='ans_gen')
        if ans_gen:
            st.write(f"*Your Answer:* {ans_gen}")

        st.markdown("### 📍 Your Assigned Doctor & Clinic Allocation")
        rec_text = "Please proceed to the Community Primary Health Center, General OPD Desk. You will be screened by Dr. Neha Patil, General Medical Officer."
        st.success(rec_text)
        speak_text(rec_text, key="gen_rec")
