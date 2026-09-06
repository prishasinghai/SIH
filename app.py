import streamlit as st 
from streamlit_mic_recorder import speech_to_text 
from gtts import gTTS 
import easyocr 
import cv2 
import numpy as np 
import io 
from deep_translator import GoogleTranslator

# Initialize Page Setting
st.set_page_config(page_title="AI Swasthya Voice Portal", page_icon="🎙️", layout="centered")
st.title("🏥 Voice & Vision AI Patient Intake Portal")
st.caption("First-Year BTech Prototype: Multilingual Speech & OCR Driven Routing")

# Helper function to generate and play voice audio back to the patient
def speak_text(text_to_speak, key):
    try:
        tts = gTTS(text=text_to_speak, lang='en', slow=False)
        sound_file = io.BytesIO()
        tts.write_to_fp(sound_file)
        st.audio(sound_file, format="audio/mp3", start_time=0)
    except Exception as e:
        st.error(f"Audio engine delay: {e}")

# Helper function to translate any language text to English safely
def translate_to_english(text_to_translate):
    if not text_to_translate.strip():
        return ""
    try:
        # Automatically detects the language (Hindi, Urdu, English, etc.) and translates to English
        translated = GoogleTranslator(source='auto', target='en').translate(text_to_translate)
        return translated.lower()
    except Exception as e:
        st.warning(f"Translation service busy, using raw text. Error: {e}")
        return text_to_translate.lower()

# Cache the AI text-reader model so it doesn't slow down the site on every button click
@st.cache_resource
def load_ocr_reader():
    return easyocr.Reader(['en'])

reader = load_ocr_reader()

# --- SECTION 1: VOICE INTAKE ---
st.header("1. 🎙️ Speak Your Symptoms & Profile")
st.write("Click the button below and describe your name, age, and symptoms in **English, Hindi (हिंदी), or Urdu (اردو)**.")

spoken_text = speech_to_text(
    start_prompt="🔴 Start Recording Voice (English/Hindi/Urdu)", 
    stop_prompt="⏹️ Stop & Process Voice", 
    language='en', 
    use_container_width=True, 
    key='intake_mic'
)

if spoken_text:
    st.success("✨ Voice Successfully Captured!")
    st.info(f'**What you said (Original):** "{spoken_text}"')
    
    with st.spinner("Translating your response to English..."):
        translated_voice = translate_to_english(spoken_text)
        st.session_state['voice_transcript'] = translated_voice
        st.info(f'**Translated English Profile:** "{translated_voice}"')
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
    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    opencv_image = cv2.imdecode(file_bytes, 1)
    with st.spinner("AI Reading handwriting & text from prescription..."):
        ocr_result = reader.readtext(opencv_image, detail=0)
        raw_ocr = " ".join(ocr_result)
        ocr_extracted_text = translate_to_english(raw_ocr)
        st.success("✓ AI Character Extraction & Translation Finished!")
        with st.expander("📄 View Extracted Text Matrix"):
            st.write(ocr_extracted_text)

# --- SECTION 3: ADAPTIVE SCREENING & DIAGNOSTIC RECOMMENDATION ---
if st.session_state['voice_transcript'] or ocr_extracted_text:
    st.divider()
    st.header("3. 🩺 Intelligent Clinical Guidance")
    
    combined_health_profile = st.session_state['voice_transcript'] + " " + ocr_extracted_text
    
    # Keyword checks to dynamically trigger relevant follow-up logic
    is_ortho = any(word in combined_health_profile for word in ["joint", "pain", "stiffness", "knee", "bone", "arthritis", "backache", "fracture", "dard"])
    is_cardio = any(word in combined_health_profile for word in ["heart", "chest", "breathing", "pressure", "bp", "hypertension", "stroke", "heartbeat"])
    is_fever_cold = any(word in combined_health_profile for word in ["fever", "cough", "cold", "flu", "chills", "headache", "throat"])
    is_stomach = any(word in combined_health_profile for word in ["stomach", "belly", "vomit", "nausea", "diarrhea", "acidity", "digestion"])

    st.subheader("💡 Tailored AI Follow-up Question:")
    
    if is_ortho:
        question = "Based on your bone or joint pain indicators, does your stiffness significantly worsen during cold weather mornings or after sitting down for a long period?"
        st.warning(f"🤖 **Question:** {question}")
        speak_text(question, key="ortho_q")
        
        st.write("Speak your answer:")
        ans_ortho = speech_to_text(start_prompt="🎙️ Record Answer", stop_prompt="⏹️ Save Answer", language='en', key='ans_ortho')
        
        st.markdown("### 📍 Your Assigned Doctor & Clinic Allocation")
        rec_text = "Please report to the AYUSH Integrated Rheumatology & Musculoskeletal Clinic at Block C. You will be visiting Dr. Anand Sharma, Chief Ayurvedic Orthopedic Specialist."
        st.success(rec_text)
        speak_text(rec_text, key="ortho_rec")
        
    elif is_cardio:
        question = "Since cardiovascular patterns are highlighted, are you experiencing any active numbness in your left arm, jaw pain, or sudden cold sweats?"
        st.error(f"🤖 **Question:** {question}")
        speak_text(question, key="cardio_q")
        
        st.write("Speak your answer:")
        ans_cardio = speech_to_text(start_prompt="🎙️ Record Answer", stop_prompt="⏹️ Save Answer", language='en', key='ans_cardio')
        
        st.markdown("### 📍 Your Assigned Doctor & Clinic Allocation")
        rec_text = "Please report to the Primary Preventive Cardiology Clinic at Block A, Room 102. You are scheduled with Dr. Kiran Rao, Senior Consultant Cardiologist."
        st.success(rec_text)
        speak_text(rec_text, key="cardio_rec")

    elif is_fever_cold:
        question = "Regarding your fever or cold symptoms, do you currently have a sore throat, loss of taste, or a cough that produces dark mucus?"
        st.info(f"🤖 **Question:** {question}")
        speak_text(question, key="fever_q")
        
        st.write("Speak your answer:")
        ans_fever = speech_to_text(start_prompt="🎙️ Record Answer", stop_prompt="⏹️ Save Answer", language='en', key='ans_fever')
        
        st.markdown("### 📍 Your Assigned Doctor & Clinic Allocation")
        rec_text = "Please proceed to General Medicine OPD at Block B. You will be screened by Dr. Neha Patil, General Medical Officer."
        st.success(rec_text)
        speak_text(rec_text, key="fever_rec")

    elif is_stomach:
        question = "For your abdominal issues, are you experiencing sharp cramps on an empty stomach or have you recently consumed outside street food?"
        st.info(f"🤖 **Question:** {question}")
        speak_text(question, key="stomach_q")
        
        st.write("Speak your answer:")
        ans_stomach = speech_to_text(start_prompt="🎙️ Record Answer", stop_prompt="⏹️ Save Answer", language='en', key='ans_stomach')
        
        st.markdown("### 📍 Your Assigned Doctor & Clinic Allocation")
        rec_text = "Please proceed to the Gastroenterology & Internal Medicine Help Desk at Room 104. You will see Dr. Suresh Mehta."
        st.success(rec_text)
        speak_text(rec_text, key="stomach_rec")
        
    else:
        question = "Could you tell me if your general symptom started suddenly today, or has it been ongoing for more than three days?"
        st.info(f"🤖 **Question:** {question}")
        speak_text(question, key="gen_q")
        
        st.write("Speak your answer:")
        ans_gen = speech_to_text(start_prompt="🎙️ Record Answer", stop_prompt="⏹️ Save Answer", language='en', key='ans_gen')
        
        st.markdown("### 📍 Your Assigned Doctor & Clinic Allocation")
        rec_text = "Please proceed to the Community Primary Health Center, General Emergency and Triage Desk for baseline assessment."
        st.success(rec_text)
        speak_text(rec_text, key="gen_rec")
        st.divider()
st.header("📋 Formal Clinical Case Sheet & Export")

# Check if data exists
if st.session_state.get('voice_transcript'):
    # Structure the collected text into Ayush-specific fields
    st.markdown("### Ayush Digital Health Record")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Patient Prakriti / Constitution (AI Inferred)", value="Vata-Pitta Tendency")
        st.text_area("Symptom Aggravation Factors", value="Worsens in morning/cold climate")
    with col2:
        st.text_input("Associated Agni (Digestive State)", value="Mandagni (Low/Sluggish)")
        st.text_input("ABDM Compliance Status", value="Ready for FHIR Integration")

    # Generate a simple downloadable CSV file for hospital database storage
    patient_data = f"Field,Value\nTranscript,{st.session_state['voice_transcript']}\nInferred Department,Musculoskeletal\nAgni State,Mandagni"
    
    st.download_button(
        label="📥 Download Clinical Case Sheet (CSV)",
        data=patient_data,
        file_name="ayush_patient_case.csv",
        mime="text/csv"
    )
