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

# --- INITIALIZE INTERNAL MEMORY BANK (SESSION STATE) ---
if 'voice_transcript' not in st.session_state:
    st.session_state['voice_transcript'] = ""
if 'ocr_transcript' not in st.session_state:
    st.session_state['ocr_transcript'] = ""
if 'frozen_questions' not in st.session_state:
    st.session_state['frozen_questions'] = None
if 'persisted_ans1' not in st.session_state:
    st.session_state['persisted_ans1'] = ""

# --- CALLBACK FUNCTION TO SECURELY SAVE ANSWER 1 BEFORE RERENDER ---
def save_answer_1():
    if 'ans_1_mic' in st.session_state and st.session_state['ans_1_mic']:
        st.session_state['persisted_ans1'] = st.session_state['ans_1_mic']

# --- MULTILINGUAL INTERFACE DICTIONARY ---
ui_lang = st.selectbox("🌐 Select Portal UI Language / पोर्टल की भाषा चुनें", ["English", "Hindi (हिंदी)"])

text_labels = {
    "English": {
        "title": "🏥 Voice & Vision AI Patient Intake Portal",
        "caption": "First-Year BTech Prototype: Multilingual Speech & OCR Driven Routing",
        "sec1_h": "1. 🎙️ Speak Your Symptoms & Profile",
        "sec1_p": "Click the button below and describe your name, age, and symptoms in **English, Hindi (हिंदी), or Urdu (اردو)**.",
        "rec_btn_1": "🔴 Start Recording Voice (English/Hindi/Urdu)",
        "stop_btn_1": "⏹️ Stop & Process Voice",
        "capture_success": "✨ Voice Successfully Captured!",
        "orig_msg": "**What you said (Original):**",
        "trans_msg": "**Translated English Profile:**",
        "sec2_h": "2. 📸 Upload Past Paper Prescription",
        "sec2_p": "Add previous medical notes or treatment files to screen for chronic history.",
        "uploader_label": "Snap or Upload a prescription photo",
        "ocr_spinner": "AI Reading handwriting & text from prescription...",
        "ocr_success": "✓ AI Character Extraction & Translation Finished!",
        "ocr_expander": "📄 View Extracted Text Matrix",
        "sec3_h": "3. 🩺 Intelligent Clinical Guidance",
        "tailored_h": "💡 Tailored AI Follow-up Question:",
        "rec_btn_general": "🎙️ Record Answer",
        "stop_btn_general": "⏹️ Save Answer",
        "assigned_h": "### 📍 Your Assigned Doctor & Clinic Allocation",
        "case_h": "📋 Formal Clinical Case Sheet & Export",
        "health_rec_h": "### Ayush Digital Health Record",
        "download_lbl": "📥 Download Clinical Case Sheet (CSV)"
    },
    "Hindi (हिंदी)": {
        "title": "🏥 वॉयस और विज़न एआई मरीज इनटेक पोर्टल",
        "caption": "प्रथम वर्ष बीटेक प्रोटोटाइप: बहुभाषी भाषण और ओसीआर संचालित रूटिंग",
        "sec1_h": "1. 🎙️ अपने लक्षण और प्रोफाइल बोलें",
        "sec1_p": "नीचे दिए गए बटन पर क्लिक करें और अपना नाम, उम्र और लक्षण अंग्रेजी, हिंदी या उर्दू में स्पष्ट रूप से बताएं।",
        "rec_btn_1": "🔴 आवाज रिकॉर्ड करना शुरू करें (अंग्रेजी/हिंदी/उर्दू)",
        "stop_btn_1": "⏹️ आवाज बंद करें और प्रोसेस करें",
        "capture_success": "✨ आवाज सफलतापूर्वक रिकॉर्ड हो गई!",
        "orig_msg": "आपने जो कहा (मूल):",
        "trans_msg": "अनुवादित अंग्रेजी प्रोफ़ाइल:",
        "sec2_h": "2. 📸 पिछला पुराना पर्चा अपलोड करें",
        "sec2_p": "क्रोनिक इतिहास की जांच के लिए पिछले मेडिकल नोट्स या उपचार फाइलें जोड़ें।",
        "uploader_label": "पर्चे की फोटो खींचे या अपलोड करें",
        "ocr_spinner": "एआई पर्चे से लिखावट और टेक्स्ट पढ़ रहा है...",
        "ocr_success": "एआई कैरेक्टर निष्कर्षण और अनुवाद समाप्त!",
        "ocr_expander": "निकाले गए टेक्स्ट को देखें",
        "sec3_h": "3. 🩺 बुद्धिमान नैदानिक मार्गदर्शन",
        "tailored_h": "अनुकूलित एआई अनुवर्ती प्रश्न:",
        "rec_btn_general": "उत्तर रिकॉर्ड करें",
        "stop_btn_general": "उत्तर सहेजें",
        "assigned_h": "### आपके आवंटित डॉक्टर और क्लिनिक स्थान",
        "case_h": "औपचारिक नैदानिक के लिए केस शीट और निर्यात",
        "health_rec_h": "### आयुष डिजिटल स्वास्थ्य रिकॉर्ड",
        "download_lbl": "क्लिनिक केस शीट डाउनलोड करें (CSV)"
    }
}

lbl = text_labels[ui_lang]

st.title(lbl["title"])
st.caption(lbl["caption"])

def speak_text(text_to_speak, key):
    try:
        tts = gTTS(text=text_to_speak, lang='en', slow=False)
        sound_file = io.BytesIO()
        tts.write_to_fp(sound_file)
        st.audio(sound_file, format="audio/mp3", start_time=0)
    except Exception as e:
        pass

def translate_to_english(text_to_translate):
    if not text_to_translate or not text_to_translate.strip():
        return ""
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text_to_translate)
        return translated.lower()
    except Exception as e:
        return text_to_translate.lower()

@st.cache_resource
def load_ocr_reader():
    return easyocr.Reader(['en'])

reader = load_ocr_reader()

# --- SECTION 1: VOICE INTAKE ---
st.header(lbl["sec1_h"])
st.write(lbl["sec1_p"])

spoken_text = speech_to_text(
    start_prompt=lbl["rec_btn_1"], 
    stop_prompt=lbl["stop_btn_1"], 
    language='en', 
    use_container_width=True, 
    key='intake_mic'
)

if spoken_text:
    st.success(lbl["capture_success"])
    st.info(f"{lbl['orig_msg']} {spoken_text}")
    
    with st.spinner("Translating..."):
        translated_voice = translate_to_english(spoken_text)
        st.session_state['voice_transcript'] = translated_voice
        st.session_state['frozen_questions'] = None 
        st.session_state['persisted_ans1'] = ""

if st.session_state['voice_transcript']:
    st.info(f"{lbl['trans_msg']} {st.session_state['voice_transcript']}")

# --- SECTION 2: PRESCRIPTION OCR ---
st.divider()
st.header(lbl["sec2_h"])
st.write(lbl["sec2_p"])
uploaded_image = st.file_uploader(lbl["uploader_label"], type=["png", "jpg", "jpeg"])

if uploaded_image is not None:
    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    opencv_image = cv2.imdecode(file_bytes, 1)
    with st.spinner(lbl["ocr_spinner"]):
        ocr_result = reader.readtext(opencv_image, detail=0)
        raw_ocr = " ".join(ocr_result)
        st.session_state['ocr_transcript'] = translate_to_english(raw_ocr)
        st.session_state['frozen_questions'] = None
        st.session_state['persisted_ans1'] = ""
        st.success(lbl["ocr_success"])

if st.session_state['ocr_transcript']:
    with st.expander(lbl["ocr_expander"]):
        st.write(st.session_state['ocr_transcript'])

# --- SECTION 3: ADAPTIVE SCREENING & DIAGNOSTIC RECOMMENDATION ---
if st.session_state['voice_transcript'] or st.session_state['ocr_transcript']:
    st.divider()
    st.header(lbl["sec3_h"])
    
    combined_health_profile = st.session_state['voice_transcript'] + " " + st.session_state['ocr_transcript']
    
    if st.session_state['frozen_questions'] is None:
        is_ortho = any(word in combined_health_profile for word in ["joint", "pain", "stiffness", "knee", "bone", "arthritis", "backache", "fracture", "dard"])
        is_cardio = any(word in combined_health_profile for word in ["heart", "chest", "breathing", "pressure", "bp", "hypertension", "stroke", "heartbeat"])
        is_fever_cold = any(word in combined_health_profile for word in ["fever", "cough", "cold", "flu", "chills", "headache", "throat"])
        is_stomach = any(word in combined_health_profile for word in ["stomach", "belly", "vomit", "nausea", "diarrhea", "acidity", "digestion"])

        if is_ortho:
            q1 = "Based on your bone or joint pain indicators, does your stiffness significantly worsen during cold weather mornings or after sitting down for a long period?"
            category = "ortho"
        elif is_cardio:
            q1 = "Since cardiovascular patterns are highlighted, are you experiencing any active numbness in your left arm, jaw pain, or sudden cold sweats?"
            category = "cardio"
        elif is_fever_cold:
            q1 = "Regarding your fever or cold symptoms, do you currently have a sore throat, loss of taste, or a cough that produces dark mucus?"
            category = "fever"
        elif is_stomach:
            q1 = "For your abdominal issues, are you experiencing sharp cramps on an empty stomach or have you recently consumed outside street food?"
            category = "stomach"
        else:
            q1 = "Could you tell me if your general symptom started suddenly today, or has it been ongoing for more than three days?"
            category = "general"
            
        st.session_state['frozen_questions'] = {"q1": q1, "category": category}

    q_data = st.session_state['frozen_questions']
    current_category = q_data["category"]

    # --- Render The Single Follow-up Question ---
    st.subheader(lbl["tailored_h"])
    st.info(f"🤖 Q1: {q_data['q1']}")
    speak_text(q_data['q1'], key="audio_q1")
    
    st.write("Speak answer to Q1 / पहले प्रश्न का उत्तर दें:")
    speech_to_text(start_prompt=lbl["rec_btn_general"], stop_prompt=lbl["stop_btn_general"], language='en', key='ans_1_mic', on_change=save_answer_1)
    
    if st.session_state['persisted_ans1']:
        st.write(f"**Answer Recorded:** {st.session_state['persisted_ans1']}")

    # --- Final Patient Routing Display (Directly Appears Instantly!) ---
    st.divider()
    st.markdown(lbl["assigned_h"])
    if current_category == "ortho":
        rec_text = "Please report to the AYUSH Integrated Rheumatology & Musculoskeletal Clinic (Sandhigata Vata Desk) at Block C. You are scheduled with Dr. Anand Sharma, Chief Ayurvedic Marma & Orthopedic Specialist."
        st.success(rec_text)
    elif current_category == "cardio":
        rec_text = "Please report to the Hridroga & Rasayana Clinic (Ayurvedic Preventive Cardiology Wing) at Block A, Room 102. You are scheduled with Dr. Kiran Rao, Senior Consultant in Ayurvedic Internal Medicine (Kaya Chikitsa)."
        st.error(rec_text)
    elif current_category == "fever":
        rec_text = "Please proceed to the Jvara & Shwasa Roga OPD (Ayurvedic Respiratory Care Unit) at Block B. You will be screened by Dr. Neha Patil, Resident Medical Officer (Kaya Chikitsa)."
        st.success(rec_text)
    elif current_category == "stomach":
        rec_text = "Please proceed to the Udara Roga & Annavaha Srotas Help Desk (Ayurvedic Gastroenterology Desk) at Room 104. You will see Dr. Suresh Mehta, Senior Specialist in Agni & Digestion Optimization."
        st.success(rec_text)
    else:
        rec_text = "Please proceed to the General Ayush Wellness Clinic (Prathamika Chikitsa Center) at the General OPD Triage Desk for baseline constitutional (Prakriti) assessment."
        st.success(rec_text)

    # --- SECTION 4: DATA EXPORT SHEET ---
    st.divider()
    st.header(lbl["case_h"])
    st.markdown(lbl["health_rec_h"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Patient Prakriti (AI Inferred)", value="Inference Active", disabled=True, key="prakriti_inferred")
        st.text_area("Symptom Aggravation Logs", value=f"Profile: {combined_health_profile[:60]}...", disabled=True, key="aggravation_logs")
    with col2:
        st.text_input("Associated Agni State", value="Inferred Assessment", disabled=True, key="agni_state")
        st.text_input("ABDM Compliance Status", value="Ready for FHIR Integration Pipeline", disabled=True, key="abdm_status")

    patient_data = (
        "Field,Value\n"
        f"Base Transcript,{st.session_state['voice_transcript']}\n"
        f"OCR Data,{st.session_state['ocr_transcript']}\n"
        f"Followup Answer,{st.session_state['persisted_ans1']}\n"
        f"Routing Department,Ayurveda - {current_category}"
    )
    
    st.download_button(
        label=lbl["download_lbl"],
        data=patient_data,
        file_name="ayush_patient_case.csv",
        mime="text/csv",
        key="btn_csv_dl"
    )
