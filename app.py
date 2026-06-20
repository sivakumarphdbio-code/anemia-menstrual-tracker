import streamlit as st
import pandas as pd
import sqlite3
import qrcode
from io import BytesIO
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("health_tracker.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT,
            flow_intensity TEXT,
            fatigue_level INTEGER,
            dizziness_level INTEGER,
            iron_foods INTEGER,
            anemia_risk TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_log(flow, fatigue, dizziness, iron, risk):
    conn = sqlite3.connect("health_tracker.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO health_logs (log_date, flow_intensity, fatigue_level, dizziness_level, iron_foods, anemia_risk)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (datetime.now().strftime("%Y-%m-%d"), flow, fatigue, dizziness, iron, risk))
    conn.commit()
    conn.close()

def get_logs():
    conn = sqlite3.connect("health_tracker.db")
    df = pd.read_sql_query("SELECT log_date, flow_intensity, fatigue_level, dizziness_level, iron_foods, anemia_risk FROM health_logs ORDER BY id DESC", conn)
    conn.close()
    return df

def clear_db():
    conn = sqlite3.connect("health_tracker.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM health_logs")
    conn.commit()
    conn.close()

# --- 2. SCREENING AI LOGIC ---
def calculate_anemia_risk(flow, fatigue, dizziness, iron):
    score = 0
    if flow == "Heavy":
        score += 3
    elif flow == "Medium":
        score += 1
        
    score += fatigue
    score += dizziness
    score -= iron
    
    if score >= 5:
        return "🔴 High Risk"
    elif 2 <= score < 5:
        return "🟡 Moderate Risk"
    else:
        return "🟢 Low Risk"

# --- 3. APP USER INTERFACE ---
init_db()
st.set_page_config(page_title="Adolescent Health Assistant", page_icon="🩸", layout="centered")

# --- 🌟 SIDEBAR NAVIGATION MENU ---
st.sidebar.title("🧭 Main Menu")
menu_choice = st.sidebar.radio(
    "Go To Page:",
    ["📝 Log Daily Health", "📊 Dashboard & History", "📚 Nutrition & Education", "📲 Scan & Share App"]
)

# App Main Title
st.title("🩸 Adolescent Anemia & Menstrual Health Tracker")

# 🚨 PERMANENT EXTREME USER EMERGENCY PANEL
st.error("### 🚨 GUIDANCE FOR EXTREME SITUATIONS (Fainting / Severe Bleeding)")
st.markdown("""
If you are passing exceptionally large blood clots, soaking through a pad in under an hour, or feeling so dizzy that you might faint, please follow these steps immediately:
1. **Inform an Adult Immediately:** Tell a parent, guardian, teacher, or school nurse right away. Do not stay alone.
2. **Rest Correctly:** Lie down flat on your back. Place a pillow under your feet and legs to help blood travel easily back to your brain.
3. **Seek Clinical Help:** Go straight to the nearest clinic or hospital. Extreme bleeding or severe weakness requires physical medical testing.
""")
st.divider()

# Medical Disclaimer Requirement
st.warning("⚠️ **Disclaimer:** This app is an educational screening assistant. It does not provide medical diagnoses or replace a clinical blood test.")

# --- PAGE ROUTING BASED ON SIDEBAR SELECTION ---

if menu_choice == "📝 Log Daily Health":
    st.header("Daily Health Log")
    with st.form("log_form", clear_on_submit=True):
        st.subheader("Menstrual Cycle Info")
        flow = st.selectbox("Period Flow Intensity today:", ["None", "Light", "Medium", "Heavy"])
        
        st.subheader("Physical Symptoms")
        fatigue = st.slider("Fatigue/Tiredness Level (0 = Energetic, 3 = Exhausted):", 0, 3, 0)
        dizziness = st.slider("Dizziness/Lightheadedness (0 = None, 3 = Severe):", 0, 3, 0)
        
        st.subheader("Nutrition")
        iron = st.slider("Iron-rich foods eaten today (Spinach, beans, meat, eggs) (0 = None, 3 = Multiple portions):", 0, 3, 0)
        
        submit_btn = st.form_submit_button("Analyze & Save Log")
        
        if submit_btn:
            risk_result = calculate_anemia_risk(flow, fatigue, dizziness, iron)
            save_log(flow, fatigue, dizziness, iron, risk_result)
            st.success("Log saved successfully!")
            st.metric(label="Calculated Screening Risk Level", value=risk_result)

elif menu_choice == "📊 Dashboard & History":
    st.header("Your Health History")
    logs_df = get_logs()
    
    if not logs_df.empty:
        st.dataframe(logs_df, use_container_width=True)
        high_risk_days = len(logs_df[logs_df["anemia_risk"] == "🔴 High Risk"])
        if high_risk_days > 0:
            st.error(f"Notice: You have logged {high_risk_days} high-risk symptom profiles. Consider taking a screenshot of this history to discuss with a doctor.")
        
        # 🗑️ THE CLEAR HISTORY BUTTON
        st.write("---")
        if st.button("🗑️ Clear All Previous Logs"):
            clear_db()
            st.success("All previous history has been cleared successfully!")
            st.rerun()
    else:
        st.info("No logs found. Use the 'Log Daily Health' menu option to enter your details.")

elif menu_choice == "📚 Nutrition & Education":
    st.header("Educational Hub")
    st.markdown("""
    ### Why is Iron Important for Adolescent Girls?
    During adolescence, girls experience rapid growth spurts while simultaneously losing blood through monthly menstruation cycles. This makes young girls highly vulnerable to **Iron Deficiency Anemia (IDA)**.
    
    ### Simple Ways to Boost Your Iron Levels:
    * **Focus on Iron-Rich Items:** Add dark green leafy vegetables (spinach), lentils, beans, fortified cereals, and poultry to your diet.
    * **Add Vitamin C:** Eating citrus fruit (oranges, lemons), tomatoes, or bell peppers with meals significantly boosts your body's iron absorption capacity.
    * **Avoid Tannins with Meals:** Avoid drinking black tea or coffee right after lunch or dinner, as they can block iron absorption.
    """)

elif menu_choice == "📲 Scan & Share App":
    st.header("📲 Scan to Open App on Your Phone")
    st.write("Examiners and students can scan this QR code using a phone camera to quickly access the tracking application interface.")
    
    # --- AUTOMATED URL DETECTION ENGINE ---
    # Hidden query parameter check
    url_params = st.query_params
    detected_url = url_params.get("current_address", "https://share.streamlit.io/")
    
    # Seamless background script reading parent page address bar
    components.html("""
        <script>
            const parentUrl = window.parent.location.href;
            if (!parentUrl.includes('current_address=')) {
                const separator = parentUrl.includes('?') ? '&' : '?';
                window.parent.location.href = parentUrl + separator + 'current_address=' + encodeURIComponent(parentUrl);
            }
        </script>
    """, height=0)
    
    # Fallback input field which auto-populates with the verified global user address
    clean_url = detected_url.split('?')[0] if '?' in detected_url else detected_url
    if "share.streamlit.io" in clean_url:
        clean_url = "Please verify your public user link address string."
        
    app_link = st.text_input("Verified Public App URL Vector:", value=clean_url)
    
    if app_link and "Please" not in app_link:
        # Generate the QR Code dynamically based on the verified site address string 
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(app_link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert image map to stream bytes for UI framework processing
        buf = BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        # Display clean render
        st.image(byte_im, caption=f"Scan this code to route to: {app_link}")
    else:
        st.info("🔄 Detecting secure user parameters... If the QR code doesn't load, copy and paste your clean public .streamlit.app web address bar path directly into the input text box above.")
