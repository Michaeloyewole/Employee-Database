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
# 4. Email and Calendar Functions  
# -------------------------------  
def send_meeting_email(employee_id, meeting_date, meeting_time, meeting_agenda, action_items, next_meeting_date):  
    employee_email = get_employee_email(employee_id)  
    if not employee_email:  
        st.warning("Could not find employee email. Email notification not sent.")  
        return False  
  
    # Retrieve SMTP details from sidebar settings (set via session state)  
    admin_email = st.session_state.get("admin_email", None)  
    smtp_server = st.session_state.get("smtp_server", None)  
    smtp_port = st.session_state.get("smtp_port", None)  
    smtp_password = st.session_state.get("smtp_password", None)  
      
    if not (admin_email and smtp_server and smtp_port and smtp_password):  
        st.warning("SMTP settings are incomplete. Email not sent.")  
        return False  
  
    msg = MIMEMultipart("alternative")  
    msg["Subject"] = "One-on-One Meeting Details"  
    msg["From"] = admin_email  
    msg["To"] = employee_email  
  
    text = f"""\  
Hi,  
  
A new one-on-one meeting has been scheduled.  
  
Meeting Date & Time: {meeting_date} {meeting_time}  
Meeting Agenda: {meeting_agenda}  
Action Items: {action_items}  
Next Meeting Date: {next_meeting_date}  
  
Regards,  
Admin  
"""  
    part = MIMEText(text, "plain")  
    msg.attach(part)  
  
    try:  
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:  
            server.starttls()  
            server.login(admin_email, smtp_password)  
            server.sendmail(admin_email, employee_email, msg.as_string())  
        st.success("Meeting email sent successfully!")  
        return True  
    except Exception as e:  
        st.error("Failed to send email: " + str(e))  
        return False  
  
def update_ms_calendar(employee_id, next_meeting_date):  
    # Placeholder: add code to connect to Microsoft Graph API or your calendar system here.  
    st.info("Calendar update for employee " + str(employee_id) + " with next meeting date " + str(next_meeting_date))  
    return True  
  
# -------------------------------  
# 5. Sidebar: CSV Import, Export & Admin Settings  
# -------------------------------  
st.sidebar.header("Admin Settings & Data Import/Export")  
  
# CSV Import/Export  
table_choice = st.sidebar.selectbox("Select Table", ["employees", "meetings", "disciplinary", "performance", "training"])  
if st.sidebar.button("Download CSV for " + table_choice):  
    # Download the CSV for the chosen table  
    columns = []  
    if table_choice == "employees":  
        columns = ['employee_id', 'first_name', 'last_name', 'employee_number', 'department',  
                   'job_title', 'hire_date', 'email', 'phone', 'address', 'date_of_birth', 'manager_id', 'employment_status']  
        df_temp = st.session_state.get("employees", pd.DataFrame())  
    elif table_choice == "meetings":  
        columns = ['meeting_id', 'employee_id', 'manager_id', 'meeting_date', 'meeting_time',  
                   'meeting_agenda', 'action_items', 'notes', 'next_meeting_date']  
        df_temp = st.session_state.get("meetings", pd.DataFrame())  
    # Extend for other tables as needed.  
    csv = df_temp.to_csv(index=False)  
    b64 = base64.b64encode(csv.encode()).decode('utf-8')  
    href = f'<a href="data:file/csv;base64,{b64}" download="{table_choice}.csv">Download {table_choice}.csv</a>'  
    st.sidebar.markdown(href, unsafe_allow_html=True)  
  
uploaded_file = st.sidebar.file_uploader("Import CSV to update table", type=["csv"])  
if uploaded_file is not None:  
    try:  
        df_upload = pd.read_csv(uploaded_file)  
        if table_choice == "employees":  
            st.session_state.employees = df_upload  
        elif table_choice == "meetings":  
            st.session_state.meetings = df_upload  
        # Extend for other tables as needed.  
        st.sidebar.success("CSV imported successfully for " + table_choice)  
    except Exception as e:  
        st.sidebar.error("Error reading CSV: " + str(e))  
  
# Admin Email & SMTP Settings  
st.sidebar.header("Email & Calendar Settings")  
admin_email = st.sidebar.text_input("Admin Email (for Outlook SMTP)")  
smtp_server = st.sidebar.text_input("SMTP Server", "smtp.office365.com")  
smtp_port = st.sidebar.text_input("SMTP Port", "587")  
smtp_password = st.sidebar.text_input("SMTP Password", type="password")  
if admin_email and smtp_server and smtp_port and smtp_password:  
    st.session_state.admin_email = admin_email  
    st.session_state.smtp_server = smtp_server  
    st.session_state.smtp_port = smtp_port  
    st.session_state.smtp_password = smtp_password  
  
# -------------------------------  
# 6. Initialize Data in Session State  
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
# Module: Employees  
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
                        "hire_date": [hire_date.strftime('%Y-%m-%d')],  
                        "email": [email],  
                        "phone": [phone],  
                        "address": [address]
