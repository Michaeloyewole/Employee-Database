import os  
import streamlit as st  
import pandas as pd  
import matplotlib.pyplot as plt  
import datetime  
import smtplib  
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart  
import io  
  
# -------------------------------  
# 1. Page Config & Data Directory  
# -------------------------------  
st.set_page_config(  
    page_title="Employee Records Tool",  
    page_icon="👥",  
    layout="wide",  
    initial_sidebar_state="expanded"  
)  
  
DATA_DIR = 'data'  
if not os.path.exists(DATA_DIR):  
    os.makedirs(DATA_DIR)  
  
# -------------------------------  
# 2. Data Persistence Functions  
# -------------------------------  
def load_table(table_name, columns):  
    path = os.path.join(DATA_DIR, f"{table_name}.csv")  
    if os.path.exists(path):  
        return pd.read_csv(path)  
    else:  
        return pd.DataFrame({col: [] for col in columns})  
  
def save_table(table_name, df):  
    path = os.path.join(DATA_DIR, f"{table_name}.csv")  
    df.to_csv(path, index=False)  
    st.success(table_name.capitalize() + " data saved successfully!")  
  
# -------------------------------  
# 3. Helper Functions for Employees  
# -------------------------------  
def get_employee_display_name(emp_id):  
    if emp_id is None or pd.isna(emp_id):  
        return "N/A"  
    employee = st.session_state.employees[st.session_state.employees['employee_id'] == emp_id]  
    if not employee.empty:  
        return f"{employee['first_name'].values[0]} {employee['last_name'].values[0]}"  
    return "Unknown"  
  
def get_employee_email(emp_id):  
    if emp_id is None or pd.isna(emp_id):  
        return None  
    employee = st.session_state.employees[st.session_state.employees['employee_id'] == emp_id]  
    if not employee.empty:  
        return employee['email'].values[0]  
    return None  
  
# -------------------------------  
# 4. Email and Calendar Integration Functions  
# -------------------------------  
def send_meeting_email(employee_id, meeting_date, meeting_time, meeting_agenda, action_items, next_meeting_date):  
    employee_email = get_employee_email(employee_id)  
    if not employee_email:  
        st.warning("Could not find employee email. Email notification not sent.")  
        return False  
  
    # Use admin email settings from session state  
    admin_email = st.session_state.get("admin_email", None)  
    smtp_server = st.session_state.get("smtp_server", None)  
    smtp_port = st.session_state.get("smtp_port", None)  
    smtp_password = st.session_state.get("smtp_password", None)  
      
    if not all([admin_email, smtp_server, smtp_port, smtp_password]):  
        st.warning("Admin email settings are incomplete. Email notification not sent.")  
        return False  
  
    try:  
        msg = MIMEMultipart()  
        msg['From'] = admin_email  
        msg['To'] = employee_email  
        msg['Subject'] = "One-on-One Meeting Details"  
        body = (  
            "Dear " + get_employee_display_name(employee_id) + ",\n\n" +  
            "Your one-on-one meeting has been scheduled.\n\n" +  
            "Meeting Date: " + meeting_date.strftime("%Y-%m-%d") + "\n" +  
            "Meeting Time: " + meeting_time.strftime("%H:%M:%S") + "\n" +  
            "Meeting Agenda: " + meeting_agenda + "\n" +  
            "Action Items: " + action_items + "\n" +  
            "Next Meeting Date: " + next_meeting_date.strftime("%Y-%m-%d") + "\n\n" +  
            "Best regards,\n" +  
            "Admin"  
        )  
        msg.attach(MIMEText(body, 'plain'))  
      
        server = smtplib.SMTP(smtp_server, int(smtp_port))  
        server.starttls()  
        server.login(admin_email, smtp_password)  
        server.send_message(msg)  
        server.quit()  
        st.success("Email sent to " + employee_email)  
        return True  
    except Exception as e:  
        st.error("Failed to send email: " + str(e))  
        return False  
  
def update_ms_calendar(employee_id, next_meeting_date):  
    # Placeholder function for Microsoft Calendar integration.  
    # You should use Microsoft Graph API to update the calendar event.  
    # This example simply prints a message.  
    st.info("Microsoft Calendar update placeholder called for employee " + str(employee_id) +   
            " with next meeting date " + next_meeting_date.strftime("%Y-%m-%d"))  
    return True  
  
# -------------------------------  
# 5. Sidebar: CSV Upload/Download and Admin Settings  
# -------------------------------  
st.sidebar.header("CSV Import/Export & Admin Settings")  
# CSV Import/Export  
st.sidebar.subheader("CSV Import/Export")  
table_choice = st.sidebar.selectbox("Select Table", ["Employees", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records"])  
uploaded_csv = st.sidebar.file_uploader("Upload CSV for " + table_choice, type=["csv"])  
if uploaded_csv is not None:  
    try:  
        df_uploaded = pd.read_csv(uploaded_csv)  
        if table_choice.lower() in st.session_state:  
            st.session_state[table_choice.lower()] = df_uploaded  
        else:  
            st.session_state[table_choice.lower()] = df_uploaded  
        st.sidebar.success(table_choice + " data updated from CSV!")  
    except Exception as e:  
        st.sidebar.error("Error reading CSV: " + str(e))  
# CSV Download  
if st.sidebar.button("Download CSV for " + table_choice):  
    if table_choice.lower() in st.session_state:  
        csv = st.session_state[table_choice.lower()].to_csv(index=False).encode("utf-8")  
        st.sidebar.download_button(  
            label="Download " + table_choice + " CSV",  
            data=csv,  
            file_name=table_choice + ".csv",  
            mime="text/csv"  
        )  
    else:  
        st.sidebar.info("No data available for " + table_choice)  
          
# Admin Email & Outlook SMTP Settings  
st.sidebar.subheader("Admin Email & SMTP Settings")  
admin_email = st.sidebar.text_input("Admin Email (Outlook)")  
smtp_server = st.sidebar.text_input("SMTP Server", "smtp.office365.com")  
smtp_port = st.sidebar.text_input("SMTP Port", "587")  
smtp_password = st.sidebar.text_input("SMTP Password", type="password")  
if st.sidebar.button("Save Admin Settings"):  
    st.session_state.admin_email = admin_email  
    st.session_state.smtp_server = smtp_server  
    st.session_state.smtp_port = smtp_port  
    st.session_state.smtp_password = smtp_password  
    st.sidebar.success("Admin settings saved.")  
  
# -------------------------------  
# 6. Initialize Tables in Session State  
# -------------------------------  
if "employees" not in st.session_state:  
    st.session_state.employees = load_table("employees", [  
        "employee_id", "first_name", "last_name", "employee_number", "department",  
        "job_title", "hire_date", "email", "phone", "address", "date_of_birth", "manager_id", "employment_status"  
    ])  
  
if "meetings" not in st.session_state:  
    st.session_state.meetings = load_table("meetings", [  
        "meeting_id", "employee_id", "manager_id", "meeting_date", "meeting_time",  
        "meeting_agenda", "action_items", "notes", "next_meeting_date"  
    ])  
# For brevity, initializing other tables similarly (disciplinary, performance, training)  
if "disciplinary" not in st.session_state:  
    st.session_state.disciplinary = load_table("disciplinary", [  
        "disciplinary_id", "employee_id", "date", "type", "reason", "description", "documentation", "issued_by"  
    ])  
if "performance" not in st.session_state:  
    st.session_state.performance = load_table("performance", [  
        "review_id", "employee_id", "review_date", "reviewer_id", "score", "comments"  
    ])  
if "training" not in st.session_state:  
    st.session_state.training = load_table("training", [  
        "training_id", "employee_id", "training_name", "provider", "start_date", "end_date", "status", "certification", "expiration_date", "comments"  
    ])  
  
# -------------------------------  
# 7. Main Navigation  
# -------------------------------  
module = st.selectbox("Select Module", ["Employees", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records"])  
  
# -------------------------------  
# 8. Module: Employees  
# -------------------------------  
if module == "Employees":  
    st.header("Employees")  
    col1, col2 = st.columns(2)  
    with col1:  
        st.subheader("Add Employee")  
        with st.form("employee_form"):  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            first_name = st.text_input("First Name")  
            last_name = st.text_input("Last Name")  
            employee_number = st.text_input("Employee Number")  
            department = st.text_input("Department")  
            job_title = st.text_input("Job Title")  
            hire_date = st.date_input("Hire Date", datetime.date.today())  
            email = st.text_input("Email")  
            phone = st.text_input("Phone")  
            address = st.text_input("Address")  
            date_of_birth = st.date_input("Birth Date", datetime.date.today())  
            manager_id = st.text_input("Manager ID (max 6 digits)", max_chars=6)  
            employment_status = st.text_input("Employment Status")  
            submitted_employee = st.form_submit_button("Add Employee")  
            if submitted_employee:  
                if employee_id == "" or not employee_id.isdigit():  
                    st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
                else:  
                    new_emp = pd.DataFrame({  
                        "employee_id": [employee_id],  
                        "first
