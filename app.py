import streamlit as st

# Set up page layout and title
st.set_page_config(page_title="AI Swasthya Intake Engine", page_icon="🏥", layout="centered")

st.title("🏥 Smart Multimodal Patient Intake Portal")
st.caption("Developed for medical history collection and adaptive AI routing.")

# --- SECTION 1: MULTIMODAL INTAKE ENGINE ---
st.header("1. Multimodal Intake Engine")
st.markdown("Patients can record their history in regional languages or upload physical prescription sheets.")

# State initialization to keep track of inputs across screen refreshes
if 'patient_profile' not in st.session_state:
    st.session_state.patient_profile = None

# Input Selection
input_mode = st.radio("Choose Input Method:", [
    "🎙️ Voice Intake (Regional Language Speech-to-Text)", 
    "📄 Upload Past Paper Prescription (OCR Parsing)",
    "✍️ Type Manually"
])

# Simulating Voice-to-Text
if input_mode == "🎙️ Voice Intake (Regional Language Speech-to-Text)":
    st.info("💡 **Voice Intake Demo:** Simulates regional audio ingestion (e.g., Hindi, Tamil, Telugu) and maps it to core demographics.")
    language = st.selectbox("Select Regional Language Spoken:", ["Hindi", "Telugu", "Tamil", "Marathi", "Bengali", "English"])
    
    if st.button("🔴 Simulate Microphone Recording"):
        st.success(f"✓ Speech recognized successfully in {language}!")
        # Simulated extraction dictionary
        st.session_state.patient_profile = {
            "name": "Ramesh Kumar", "age": "48", "gender": "Male",
            "address": "Gachibowli, Hyderabad, Telangana",
            "history": "Diagnosed with mild hypertension 2 years ago.",
            "symptoms": "Experiencing severe chronic joint pain and stiffness in knees for 3 weeks."
        }

# Simulating OCR Extraction
elif input_mode == "📄 Upload Past Paper Prescription (OCR Parsing)":
    st.info("💡 **OCR Demo:** Simulates processing a scanned prescription photo to automatically extract typed or written profile keys.")
    uploaded_file = st.file_uploader("Upload an image/PDF prescription", type=["png", "jpg", "jpeg", "pdf"])
    
    if uploaded_file is not None:
        st.success("✓ Prescription read via AI OCR parsing!")
        st.session_state.patient_profile = {
            "name": "Ananya Desai", "age": "54", "gender": "Female",
            "address": "Andheri West, Mumbai, Maharashtra",
            "history": "History of irregular digestion and high cholesterol.",
            "symptoms": "Chronic shoulder joint swelling and extreme cold sensitivity."
        }

# Manual Fallback Entry
elif input_mode == "✍️ Type Manually":
    with st.form("manual_entry"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Name")
        age = col2.text_input("Age")
        gender = col1.selectbox("Gender", ["Male", "Female", "Other"])
        address = col2.text_input("Address")
        history = st.text_area("Previous Underlying Health Issues")
        symptoms = st.text_area("Current Issues / Symptoms")
        
        if st.form_submit_button("Submit Profile"):
            st.session_state.patient_profile = {
                "name": name, "age": age, "gender": gender, "address": address, "history": history, "symptoms": symptoms
            }

# Render Extracted Profile & Location Recommendation
if st.session_state.patient_profile:
    profile = st.session_state.patient_profile
    st.markdown("### 📋 Structured Intake Profile")
    
    # Custom display boxes
    st.markdown(f"**Name:** {profile['name']} | **Age:** {profile['age']} | **Gender:** {profile['gender']}")
    st.markdown(f"**Address:** {profile['address']}")
    st.markdown(f"**Past History:** {profile['history']}")
    st.markdown(f"**Current Symptoms:** {profile['symptoms']}")
    
    # Smart Location Recommendation Engine (Based on simple keyword intelligence)
    st.markdown("#### 📍 Recommended Local Care Facility")
    symptoms_lower = profile['symptoms'].lower()
    
    if "joint" in symptoms_lower or "pain" in symptoms_lower or "stiffness" in symptoms_lower:
        st.warning("⚠️ **Primary Recommendation:** AYUSH Integrated Musculoskeletal & Rheumatology Clinic, Sector Sub-Block Clinic.")
    else:
        st.info("ℹ️ **Primary Recommendation:** Community Primary Health Center (General OPD).")

    # --- SECTION 2: ADAPTIVE DYNAMIC QUESTIONING ENGINE ---
    st.divider()
    st.header("2. Adaptive Dynamic Questioning Engine")
    st.markdown("*The system acts like a real doctor—changing consecutive questions dynamically based on findings above.*")

    # Tracking questionnaire state progress
    if 'survey_step' not in st.session_state:
        st.session_state.survey_step = 1
    if 'survey_answers' not in st.session_state:
        st.session_state.survey_answers = {}

    # Check if the joint pain/AYUSH branching criteria is met
    is_ayush_branch = "joint" in symptoms_lower or "pain" in symptoms_lower or "stiffness" in symptoms_lower

    if is_ayush_branch:
        st.caption("🤖 **AI Agent Routing Info:** Chronic pain/joint pattern identified. Activating specialized AYUSH digestion & cold tolerance diagnostic pathway.")

        if st.session_state.survey_step == 1:
            st.markdown("**Dynamic Question 1:** How would you describe your standard metabolic digestion or bowel pattern?")
            q1_ans = st.radio("Choose an option:", ["Sluggish, heavy, or frequent bloating", "Highly irregular with recurrent gas", "Sharp appetite but acidic/burning", "Perfectly regular"])
            if st.button("Next Question ➡️"):
                st.session_state.survey_answers["Metabolic Digestion"] = q1_ans
                st.session_state.survey_step = 2
                st.rerun()

        elif st.session_state.survey_step == 2:
            # Shift the context of Question 2 adaptively based on Question 1's answer!
            prev_ans = st.session_state.survey_answers.get("Metabolic Digestion", "")
            st.write(f"ℹ️ *Recorded Digestion State: {prev_ans}*")
            
            if "bloating" in prev_ans.lower() or "irregular" in prev_ans.lower():
                st.markdown("**Dynamic Question 2 (Adapted due to poor digestion):** Does your joint pain distinctly aggravate or lock after eating heavy meals, cold weather shifts, or during high humidity?")
            else:
                st.markdown("**Dynamic Question 2 (Standard):** How is your overall physiological cold tolerance during temperature drops?")
            
            q2_ans = st.radio("Choose an option:", ["Yes, cold/humidity completely freezes up my mobility", "No, warmth actually worsens the inflammation", "The pain stays completely independent of weather patterns"])
            
            if st.button("Complete Comprehensive Intake 🏁"):
                st.session_state.survey_answers["Cold/Weather Triggers"] = q2_ans
                st.session_state.survey_step = 3
                st.rerun()

        elif st.session_state.survey_step == 3:
            st.success("🎉 Adaptive Pre-Intake Form Completed!")
            st.markdown("### 📥 Transmission Package for Attending Doctor")
            st.write("This structured object will be packaged and ready for clinical evaluation:")
            st.json({
                "Demographics Data": f"{profile['name']} ({profile['age']} / {profile['gender']})",
                "Stated Symptoms": profile['symptoms'],
                "Adaptive AYUSH Insights Summary": st.session_state.survey_answers
            })
            
            if st.button("🔄 Reset Questionnaire"):
                st.session_state.survey_step = 1
                st.session_state.survey_answers = {}
                st.session_state.patient_profile = None
                st.rerun()
    else:
        st.success("✅ Standard intake checklist complete. No targeted system branch required for this complaint profile.")

