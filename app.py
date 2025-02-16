import os
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import google.generativeai as genAI
import datetime

load_dotenv()
genAI.configure(api_key=os.getenv("GEMINI_API"))

# Function to extract valid digit pairs (excluding 0-containing pairs)
def extract_valid_pairs(mobileNum):
    pairs = [mobileNum[i:i+2] for i in range(len(mobileNum) - 1)]
    valid_pairs = [pair for pair in pairs if '0' not in pair]  # Exclude pairs with '0'
    return valid_pairs

def sum_digits_until_single(num):
    """Calculates the sum of digits until a single digit is obtained."""
    while num >= 10:
        num = sum(int(digit) for digit in str(num))
    return num

def generate_numerology_report(mobileNum):
    try:
        # Calculate the sum of digits
        total_sum = sum(int(digit) for digit in mobileNum)
        reduced_sum = sum_digits_until_single(total_sum)

        valid_pairs = extract_valid_pairs(mobileNum)
        if not valid_pairs:
            return "No valid digit pairs available for numerology analysis."

        # Create analysis lines separately
        analysis_lines = [
            f"{i+1} - **Yog : {pair}** → *(Planet1 - Planet2)*\n   - **Meaning:** (Interpretation...)"
            for i, pair in enumerate(valid_pairs)
        ]
        analysis_text = "\n\n".join(analysis_lines)  # Join with double newlines for readability

        prompt = f"""
Analyze the given mobile number using numerology principles and provide a detailed report. Follow Vedic numerology by breaking the number into **valid digit pairs** (excluding any pair containing '0'), assigning planetary influences, and interpreting their effects. Ensure the report is concise, structured, and relevant.

### Format:  

**MOBILE NUMBER - ({mobileNum})**  

#### **Sum of Digits Analysis:**  
Total Sum: **{total_sum}** → Reduced to Single Digit: **{reduced_sum}**

#### **Digit Pair Analysis:**  
{analysis_text}  

### **Final Analysis:**  
- **Strengths:** (List the key strengths associated with this mobile number.)  
- **Challenges:** (Mention possible difficulties and remedies, if applicable.)  
- **Overall Impact:** (Summarize how this number influences the person's life.)  

### **Important Notes:**  
1. Follow **authentic Vedic numerology principles**.  
2. **Exclude pairs that contain '0' (e.g., 30, 60, 09, etc.).**  
3. Ensure **concise yet meaningful** explanations.  
4. Do **not** repeat the same interpretations unnecessarily.  
5. Maintain **balance**—mention both **positive** and **challenging** aspects.  
6. Avoid generic astrology-style predictions; keep it **mobile number-focused**.  
"""
        model = genAI.GenerativeModel("gemini-2.0-flash-exp")
        res = model.generate_content([prompt])
        return res.text
    except Exception as e:
        return f"Error: {e}"


st.title("Numerology Report Generator")
name = st.text_input("Enter your Name")
dob = st.date_input("Enter Date of Birth:", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
mobileNum = st.text_input("Enter your Mobile Number", max_chars=10)

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
