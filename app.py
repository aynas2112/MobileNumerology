import os
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import google.generativeai as genAI
import datetime


load_dotenv()
genAI.configure(api_key=os.getenv("GEMINI_API"))

def generate_numerology_report(mobileNum):
    try:
        prompt=f"""
        Analyze the given mobile number using numerology principles and provide a detailed report. Follow Vedic numerology by breaking the number into digit pairs, assigning planetary influences, and interpreting their effects. Ensure the report is concise, structured, and relevant.  

### Format:  

**MOBILE NUMBER - (XXXXXXXXXX)**  

#### **Digit Pair Analysis:**  
For each pair, determine the ruling planets and provide an interpretation:  

1 - **Yog : XX** → *(Planet1 - Planet2)*  
   - **Meaning:** (Interpretation based on Vedic numerology, focusing on personality, career, relationships, and life events.)  
   
2 - **Yog : XX** → *(Planet1 - Planet2)*  
   - **Meaning:** (Interpretation…)  

(Continue this for all digit pairs.)  

### **Final Analysis:**  
- **Strengths:** (List the key strengths associated with this mobile number.)  
- **Challenges:** (Mention possible difficulties and remedies, if applicable.)  
- **Overall Impact:** (Summarize how this number influences the person's life.)  

### **Important Notes:**  
1. Follow **authentic Vedic numerology principles**.  
2. Do **not** repeat the same interpretations unnecessarily.  
3. Ensure **concise yet meaningful** explanations.  
4. The analysis should be **balanced**—mention both **positive** and **challenging** aspects.  
5. Avoid generic astrology-style predictions; keep it **mobile number-focused**.  

        """
        model=genAI.GenerativeModel("gemini-2.0-flash-exp")
        res=model.generate_content([prompt,mobileNum])
        return res.text
    except Exception as e:
        return f"Error: {e}"
st.title("Numerology Report Generator")
name=st.text_input("Enter your Name")
dob=st.date_input("Enter Date of Birth:", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
mobileNum=st.text_input("Enter your Mobile Number", max_chars=10)
if st.button("Generate Report"):
    if len(mobileNum) != 10 or not mobileNum.isdigit():
        st.error("Please enter a valid 10-digit mobile number.")
    else:
        st.subheader(f"🔮 Numerology Report for {name}")
        st.write(f"**Date of Birth:** {dob.strftime('%d-%m-%Y')}")
        st.write(f"**Mobile Number:** {mobileNum}")
        report = generate_numerology_report(mobileNum)
        st.markdown("### **Mobile Number Analysis**")  
        st.markdown(report)