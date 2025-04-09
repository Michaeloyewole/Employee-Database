import os  
import streamlit as st  
import pandas as pd  
import matplotlib.pyplot as plt  
import datetime  
import smtplib  
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart  
import requests  
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
# 3. Email & Calendar Functions  
# -------------------------------  
def get_employee_email(emp_id):  
    if emp_id is None or emp_id == "":  
        return None  
    df = st.session_state.employees  
    employee = df[df['employee_id'] == emp_id]  
    if not employee.empty:  
        return employee['email'].values[0]  
    return None  
  
def send_meeting_email(employee_id, meeting_agenda, action_items, next_meeting_date):  
    # Ensure Outlook credentials are in session_state  
    if 'admin_email' not in st.session_state or 'smtp_password' not in st.session_state:  
        st.warning("Admin email credentials not set. Email not sent.")  
        return  
    recipient = get_employee_email(employee_id)  
    if recipient is None or recipient == "":  
        st.warning("Employee email not found. Email not sent.")  
        return  
  
    admin_email = st.session_state.admin_email  
    smtp_password = st.session_state.smtp_password  
    smtp_server = st.session_state.smtp_server if 'smtp_server' in st.session_state else "smtp.office365.com"  
    smtp_port = st.session_state.smtp_port if 'smtp_port' in st.session_state else 587  
  
    subject = "One-on-One Meeting Details"  
    body = f"""Dear Employee,  
  
Here are the details of your recent one-on-one meeting:  
  
Meeting Agenda: {meeting_agenda}  
Action Items: {action_items}  
Next Meeting Date: {next_meeting_date.strftime('%Y-%m-%d')}  
  
Best regards,  
Admin  
"""  
    msg = MIMEMultipart()  
    msg['From'] = admin_email  
    msg['To'] = recipient  
    msg['Subject'] = subject  
    msg.attach(MIMEText(body, 'plain'))  
      
    try:  
        server = smtplib.SMTP(smtp_server, smtp_port)  
        server.starttls()  
        server.login(admin_email, smtp_password)  
        server.sendmail(admin_email, recipient, msg.as_string())  
        server.quit()  
        st.success("Email notification sent successfully!")  
    except Exception as e:  
        st.error("Error sending email: " + str(e))  
  
def update_ms_calendar(employee_id, next_meeting_date):  
    # Placeholder function for Microsoft Calendar update.  
    # Here you would implement your Microsoft Graph API integration.  
    # For example, you can construct an API call to update the event.  
    # This is a dummy function:  
    st.info("Calendar updated for employee " + employee_id + " with next meeting on " + next_meeting_date.strftime("%Y-%m-%d"))  
    return  
  
# -------------------------------  
# 4. Sidebar: CSV Import/Export & Admin Credentials  
# -------------------------------  
st.sidebar.header("CSV Import/Export & Admin Email Settings")  
# CSV Import  
upload_option = st.sidebar.selectbox("Select Table to Update", ["Employees", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records"])  
uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])  
if uploaded_file is not None:  
    try:  
        data = pd.read_csv(uploaded_file)  
        if upload_option == "Employees":  
            st.session_state.employees = data  
        elif upload_option == "One-on-One Meetings":  
            st.session_state.meetings = data  
        elif upload_option == "Disciplinary Actions":  
            st.session_state.disciplinary = data  
        elif upload_option == "Performance Reviews":  
            st.session_state.performance = data  
        elif upload_option == "Training Records":  
            st.session_state.training = data  
        st.sidebar.success(f"{upload_option} table updated successfully from CSV.")  
    except Exception as e:  
        st.sidebar.error("Error reading CSV: " + str(e))  
  
# CSV Download example (for Employees)  
if st.sidebar.button("Download Employees CSV"):  
    csv = st.session_state.employees.to_csv(index=False).encode('utf-8')  
    st.sidebar.download_button(  
        "Download Employees CSV",  
        csv,  
        "employees.csv",  
        "text/csv",  
        key='download-employees'  
    )  
  
# Admin Email Settings  
st.sidebar.header("Outlook SMTP Settings (Admin)")  
admin_email = st.sidebar.text_input("Admin Email (From address)")  
smtp_server = st.sidebar.text_input("SMTP Server", value="smtp.office365.com")  
smtp_port = st.sidebar.text_input("SMTP Port", value="587")  
smtp_password = st.sidebar.text_input("SMTP Password", type="password")  
if admin_email and smtp_password:  
    st.session_state.admin_email = admin_email  
    st.session_state.smtp_server = smtp_server  
    st.session_state.smtp_port = int(smtp_port)  
    st.session_state.smtp_password = smtp_password  
  
# -------------------------------  
# 5. Initialize Tables in Session State  
# -------------------------------  
if 'employees' not in st.session_state:  
    st.session_state.employees = load_table("employees", [  
        "employee_id", "first_name", "last_name", "employee_number",  
        "department", "job_title", "hire_date", "email", "phone",  
        "address", "date_of_birth", "manager_id", "employment_status"  
    ])  
if 'meetings' not in st.session_state:  
    st.session_state.meetings = load_table("meetings", [  
        "meeting_id", "employee_id", "manager_id", "meeting_date",  
        "meeting_time", "meeting_agenda", "action_items", "notes",  
        "next_meeting_date"  
    ])  
if 'disciplinary' not in st.session_state:  
    st.session_state.disciplinary = load_table("disciplinary", [  
        "disciplinary_id", "employee_id", "date", "type", "reason",  
        "description", "documentation", "issued_by"  
    ])  
if 'performance' not in st.session_state:  
    st.session_state.performance = load_table("performance", [  
        "review_id", "employee_id", "review_date", "reviewer_id", "score", "comments"  
    ])  
if 'training' not in st.session_state:  
    st.session_state.training = load_table("training", [  
        "training_id", "employee_id", "training_name", "provider",  
        "start_date", "end_date", "status", "certification",  
        "expiration_date", "comments"  
    ])  
  
# -------------------------------  
# 6. Main Navigation  
# -------------------------------  
module = st.selectbox("Select Module", ["Employees", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records"])  
  
# -------------------------------  
# 7. Module: Employees  
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
                        "first_name": [first_name],  
                        "last_name": [last_name],  
                        "employee_number": [employee_number],  
                        "department": [department],  
                        "job_title": [job_title],  
                        "hire_date": [hire_date.strftime("%Y-%m-%d")],  
                        "email": [email],  
                        "phone": [phone],  
                        "address": [address],  
                        "date_of_birth": [date_of_birth.strftime("%Y-%m-%d")],  
                        "manager_id": [manager_id],  
                        "employment_status": [employment_status]  
                    })  
                    st.session_state.employees = pd.concat([st.session_state.employees, new_emp], ignore_index=True)  
                    st.success("Employee added!")  
    with col2:  
        st.subheader("Employees Table")  
        st.dataframe(st.session_state.employees)  
        if st.button("Save Employees Data"):  
            save_table("employees", st.session_state.employees)  
  
# -------------------------------  
# 8. Module: One-on
