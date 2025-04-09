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
    path = os.path.join(DATA_DIR, f'{table_name}.csv')  
    if os.path.exists(path):  
        return pd.read_csv(path)  
    else:  
        return pd.DataFrame({col: [] for col in columns})  
  
def save_table(table_name, df):  
    path = os.path.join(DATA_DIR, f'{table_name}.csv')  
    df.to_csv(path, index=False)  
    st.success(f"{table_name.capitalize()} data saved successfully!")  
  
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
# 3. Email and Calendar Functions  
# -------------------------------  
def send_meeting_email(employee_id, meeting_date, meeting_time, meeting_agenda, action_items, next_meeting_date):  
    employee_email = get_employee_email(employee_id)  
    if not employee_email:  
        st.warning("Employee email not found. Email notification not sent.")  
        return False  
  
    # Get admin email and SMTP credentials from session state (set via Sidebar)  
    admin_email = st.session_state.get('admin_email', None)  
    smtp_server = st.session_state.get('smtp_server', None)  
    smtp_port = st.session_state.get('smtp_port', 587)  
    smtp_password = st.session_state.get('smtp_password', None)  
  
    if None in [admin_email, smtp_server, smtp_password]:  
        st.warning("Admin email SMTP credentials not set. Email notification not sent.")  
        return False  
  
    subject = "Meeting Notification: Your one-on-one meeting details"  
    body = f"""  
    Dear {get_employee_display_name(employee_id)},  
      
    Your one-on-one meeting has been scheduled.  
      
    Meeting Agenda: {meeting_agenda}  
      
    Action Items: {action_items}  
      
    Next Meeting Date: {next_meeting_date.strftime('%Y-%m-%d')}  
      
    Regards,  
    Admin  
    """  
  
    message = MIMEMultipart()  
    message["From"] = admin_email  
    message["To"] = employee_email  
    message["Subject"] = subject  
    message.attach(MIMEText(body, "plain"))  
    try:  
        server = smtplib.SMTP(smtp_server, smtp_port)  
        server.starttls()  
        server.login(admin_email, smtp_password)  
        server.sendmail(admin_email, employee_email, message.as_string())  
        server.quit()  
        st.success("Email notification sent to employee!")  
        return True  
    except Exception as e:  
        st.error("Failed to send email: " + str(e))  
        return False  
  
def update_ms_calendar(employee_id, meeting_date, meeting_time, next_meeting_date):  
    """  
    Placeholder function to update Microsoft Calendar.  
    Implement using Microsoft Graph API calls with the required authentication.  
    """  
    # Example (pseudocode):  
    # token = get_ms_graph_token(client_id, client_secret, tenant_id)  
    # endpoint = "https://graph.microsoft.com/v1.0/me/events"  
    # meeting_payload = { ... }  
    # response = requests.post(endpoint, headers={...}, json=meeting_payload)  
    # if response.ok:  
    #     st.success("Calendar updated successfully!")  
    # else:  
    #     st.warning("Failed to update calendar.")  
    st.info("Calendar update functionality is not fully implemented. Please integrate with Microsoft Graph API.")  
    return  
  
# -------------------------------  
# 4. Sidebar: CSV Import/Export & Admin Credentials  
# -------------------------------  
st.sidebar.header("CSV Import/Export")  
csv_import_table = st.sidebar.selectbox("Select table to update", ["employees", "meetings", "disciplinary", "performance", "training"])  
uploaded_file = st.sidebar.file_uploader("Upload CSV File", type="csv")  
if uploaded_file is not None:  
    try:  
        df_import = pd.read_csv(uploaded_file)  
        if csv_import_table == "employees":  
            st.session_state.employees = df_import  
        elif csv_import_table == "meetings":  
            st.session_state.meetings = df_import  
        elif csv_import_table == "disciplinary":  
            st.session_state.disciplinary = df_import  
        elif csv_import_table == "performance":  
            st.session_state.performance = df_import  
        elif csv_import_table == "training":  
            st.session_state.training = df_import  
        st.sidebar.success("Data imported for " + csv_import_table)  
    except Exception as e:  
        st.sidebar.error("Failed to import CSV: " + str(e))  
          
st.sidebar.header("Download CSV")  
download_table = st.sidebar.selectbox("Select table to download", ["employees", "meetings", "disciplinary", "performance", "training"])  
download_button = st.sidebar.button("Download CSV")  
if download_button:  
    if download_table == "employees":  
        csv = st.session_state.employees.to_csv(index=False)  
    elif download_table == "meetings":  
        csv = st.session_state.meetings.to_csv(index=False)  
    elif download_table == "disciplinary":  
        csv = st.session_state.disciplinary.to_csv(index=False)  
    elif download_table == "performance":  
        csv = st.session_state.performance.to_csv(index=False)  
    elif download_table == "training":  
        csv = st.session_state.training.to_csv(index=False)  
    b64 = base64.b64encode(csv.encode()).decode()  # some strings  
    href = f'<a href="data:file/csv;base64,{b64}" download="{download_table}.csv">Download {download_table} CSV File</a>'  
    st.sidebar.markdown(href, unsafe_allow_html=True)  
  
st.sidebar.header("Admin Email Settings")  
admin_email = st.sidebar.text_input("Admin Email (Outlook)")  
smtp_server = st.sidebar.text_input("SMTP Server", value="smtp.office365.com")  
smtp_port = st.sidebar.number_input("SMTP Port", value=587)  
smtp_password = st.sidebar.text_input("SMTP Password", type="password")  
if admin_email and smtp_server and smtp_password:  
    st.session_state.admin_email = admin_email  
    st.session_state.smtp_server = smtp_server  
    st.session_state.smtp_port = smtp_port  
    st.session_state.smtp_password = smtp_password  
  
# -------------------------------  
# 5. Initialize Remaining Tables in Session State  
# -------------------------------  
# For brevity, only employees and meetings are fully shown. Extend similarly for disciplinary,  
# performance, and training.  
if 'disciplinary' not in st.session_state:  
    st.session_state.disciplinary = load_table('disciplinary', [  
        'disciplinary_id', 'employee_id', 'date', 'type', 'reason', 'description', 'documentation', 'issued_by'  
    ])  
if 'performance' not in st.session_state:  
    st.session_state.performance = load_table('performance', [  
        'review_id', 'employee_id', 'review_date', 'reviewer_id', 'score', 'comments'  
    ])  
if 'training' not in st.session_state:  
    st.session_state.training = load_table('training', [  
        'training_id', 'employee_id', 'training_name', 'provider', 'start_date', 'end_date', 'status', 'certification', 'expiration_date', 'comments'  
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
            date_of_birth = st.date_input("Birth Date", datetime
