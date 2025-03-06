import os
import streamlit as st
import datetime
from dotenv import load_dotenv
import google.generativeai as genAI
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables
load_dotenv()
genAI.configure(api_key=os.getenv("GEMINI_API"))

# Load Firebase credentials
firebase_json_path = "numerosubscription-firebase-adminsdk-fbsvc-41b30ce938.json"
cred = credentials.Certificate(firebase_json_path)
# Load Firebase credentials only if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_json_path)
    firebase_admin.initialize_app(cred)

# Firestore Database Reference
db = firestore.client()

# Function to check user credentials
def verify_user(username, password):
    users_ref = db.collection("users").document(username).get()
    if users_ref.exists:
        user_data = users_ref.to_dict()
        return user_data["password"] == password  # Ensure passwords match
    return False

# Function to handle user sign-up
def sign_up():
    st.title("📝 Sign Up for Numerology Report")
    new_username = st.text_input("Choose a Username").strip().lower()  # Convert to lowercase
    new_password = st.text_input("Choose a Password", type="password")
    
    if st.button("Sign Up"):
        if not new_username or not new_password:
            st.error("⚠️ Please fill in both fields.")
            return

        users_ref = db.collection("users").document(new_username).get()
        if users_ref.exists:
            st.error("⚠️ Username already exists. Choose a different one.")
        else:
            db.collection("users").document(new_username).set({"password": new_password})
            st.success("✅ Account created successfully! Please log in.")
            st.session_state["signing_up"] = False
            st.experimental_rerun()

# Function to handle login
def login():
    st.title("🔐 Login to Numerology Report")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if verify_user(username, password):
            st.session_state["logged_in"] = True
            st.success("✅ Login successful! Redirecting...")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid credentials! Try again.")
    
    st.markdown("---")
    if st.button("Don't have an account? Sign Up"):
        st.session_state["signing_up"] = True
        st.experimental_rerun()


# Function to reduce a number to a single digit
def sum_digits_until_single(num):
    while num >= 10:
        num = sum(int(digit) for digit in str(num))
    return num

# Function to calculate Driver & Conductor numbers
def calculate_driver_and_conductor(dob):
    day, month, year = map(int, dob.split('/'))
    driver_number = sum_digits_until_single(day)
    conductor_number = sum_digits_until_single(day + month + sum(int(digit) for digit in str(year)))
    return driver_number, conductor_number

# Function to create the Vedic Grid
def create_grid(dob):
    day, month, year = map(int, dob.split('/'))
    driver, conductor = calculate_driver_and_conductor(dob)
    
    # Extract last two digits of the year
    year_last_two = year % 100
    
    # Extract digits from day, month, and year_last_two
    elements = list(map(int, str(day) + str(month) + str(year_last_two)))
    
    # Include driver & conductor numbers if driver is not equal to date
    if driver != day:
        elements.append(driver)
    elements.append(conductor)
    
    # Count occurrences of each digit
    digit_count = {str(i): '' for i in range(1, 10)}
    for digit in elements:
        digit_str = str(digit)
        if digit_str in digit_count:
            digit_count[digit_str] += digit_str
    
    # Define numerology grid positions
    grid_positions = {
        '1': (0, 1), '2': (2, 0), '3': (0, 0),
        '4': (2, 2), '5': (1, 2), '6': (1, 0),
        '7': (1, 1), '8': (2, 1), '9': (0, 2)
    }
    
    # Initialize a 3x3 grid with underscores
    grid = [['_' for _ in range(3)] for _ in range(3)]
    
    # Fill the grid with numerology numbers
    for digit, position in grid_positions.items():
        x, y = position
        if digit_count[digit]:
            grid[x][y] = digit_count[digit]
    
    return grid, driver, conductor

# Function to format and return the Vedic Grid with styling
def format_grid(grid):
    styled_grid = "<table style='border-collapse: collapse; width: 100%; text-align: center;'>"
    for row in grid:
        styled_grid += "<tr>"
        for cell in row:
            styled_grid += f"<td style='border: 1px solid black; padding: 10px; font-size: 18px;'>{cell}</td>"
        styled_grid += "</tr>"
    styled_grid += "</table>"
    return styled_grid

# Function to generate numerology report for a mobile number
def generate_numerology_report(mobileNum):
    try:
        # Calculate sum of digits
        total_sum = sum(int(digit) for digit in mobileNum)
        reduced_sum = sum_digits_until_single(total_sum)

        prompt = f"""
Analyze the given mobile number using numerology principles and provide a detailed report. 

### **MOBILE NUMBER - ({mobileNum})**  
#### **Sum of Digits Analysis:**  
Total Sum: **{total_sum}** → Reduced to Single Digit: **{reduced_sum}**

#### **Final Analysis:**  
- **Strengths:** (Key strengths of this mobile number.)  
- **Challenges:** (Possible difficulties and remedies.)  
- **Overall Impact:** (How this number influences the person’s life.)  

### **Important Notes:**  
1. **Follow Vedic numerology principles.**  
2. **Exclude pairs with '0' (e.g., 30, 60, 09, etc.).**  
3. **Avoid repetitive interpretations.**  
"""
        model = genAI.GenerativeModel("gemini-2.0-flash-exp")
        res = model.generate_content([prompt])
        return res.text
    except Exception as e:
        return f"Error: {e}"
def save_report_to_firebase(name, dob, mobileNum, driver, conductor, report):
    report_data = {
        "name": name,
        "dob": dob,
        "mobileNum": mobileNum,
        "driverNumber": driver,
        "conductorNumber": conductor,
        "report": report,
        "timestamp": datetime.datetime.now().isoformat()
    }
    db.collection("numerology_reports").add(report_data)
    st.success("📤 Report saved successfully!")

<<<<<<< HEAD
# Streamlit UI
st.title("🔮 Mobile Numerology Report Generator")

name = st.text_input("Enter your Name")
dob = st.date_input("Enter Date of Birth:", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today(), format="DD/MM/YYYY")
mobileNum = st.text_input("Enter your Mobile Number", max_chars=10)

if st.button("Generate Report"):
    if len(mobileNum) != 10 or not mobileNum.isdigit():
        st.error("❌ Please enter a valid 10-digit mobile number.")
=======
# Check if user is logged in or signing up
# Ensure user is authenticated before allowing report generation
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    if "signing_up" in st.session_state and st.session_state["signing_up"]:
        sign_up()
>>>>>>> cdca4afc9725af2aaece6d8b4ba42deb748c5051
    else:
        login()
else:
    st.title("🔮 Numerology Report Generator")

    name = st.text_input("Enter your Name").strip()
    dob = st.date_input("Enter Date of Birth:", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
    mobileNum = st.text_input("Enter your Mobile Number").strip()

    if st.button("Generate Report"):
        if not name:
            st.error("❌ Name is required.")
        elif len(mobileNum) != 10 or not mobileNum.isdigit():
            st.error("❌ Please enter a valid 10-digit mobile number.")
        else:
            st.subheader(f"🔮 Numerology Report for {name}")
            st.write(f"📅 **Date of Birth:** {dob.strftime('%d-%m-%Y')}")
            st.write(f"📱 **Mobile Number:** {mobileNum}")

            # Generate Vedic Grid
            dob_str = dob.strftime('%d/%m/%Y')
            grid, driver, conductor = create_grid(dob_str)
            grid_display = format_grid(grid)

            # Display Vedic Grid
            st.markdown("### 🛕 **Vedic Grid**", unsafe_allow_html=True)
            st.markdown(grid_display, unsafe_allow_html=True)

            # Display Driver & Conductor Numbers
            st.markdown("### 🔢 **Driver & Conductor Numbers**")
            st.write(f"**Driver Number:** {driver}")
            st.write(f"**Conductor Number:** {conductor}")

            # Generate & Display Numerology Report
            report = generate_numerology_report(mobileNum)
            st.markdown("### 📊 **Mobile Number Analysis**")
            st.markdown(report)

            # Save to Firebase
            save_report_to_firebase(name, dob_str, mobileNum, driver, conductor, report)

    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.experimental_rerun()
