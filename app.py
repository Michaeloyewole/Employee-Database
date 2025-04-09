import os  
import streamlit as st  
import pandas as pd  
import matplotlib.pyplot as plt  
import datetime  
import smtplib  
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart  
import base64  
  
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
  
# -------------------------------  
# 3. Initialize Tables in Session State  
# -------------------------------  
if 'employees' not in st.session_state:  
    st.session_state.employees = load_table('employees', [  
        'employee_id', 'first_name', 'last_name', 'employee_number',  
        'department', 'job_title', 'hire_date', 'email', 'phone',  
        'address', 'date_of_birth', 'manager_id', 'employment_status'  
    ])  
  
if 'meetings' not in st.session_state:  
    st.session_state.meetings = load_table('meetings', [  
        'meeting_id', 'employee_id', 'manager_id', 'meeting_date',  
        'meeting_time', 'Meeting Agenda', 'action_items', 'notes',  
        'next_meeting_date'  
    ])  
  
if 'disciplinary' not in st.session_state:  
    st.session_state.disciplinary = load_table('disciplinary', [  
        'disciplinary_id', 'employee_id', 'date', 'type', 'reason',  
        'description', 'documentation', 'issued_by'  
    ])  
  
if 'performance' not in st.session_state:  
    st.session_state.performance = load_table('performance', [  
        'review_id', 'employee_id', 'review_date', 'reviewer', 'score', 'comments'  
    ])  
  
if 'training' not in st.session_state:  
    st.session_state.training = load_table('training', [  
        'training_id', 'employee_id', 'training_date', 'course_name', 'status'  
    ])  
  
# -------------------------------  
# 4. Sidebar: CSV Import/Export and SMTP Settings  
# -------------------------------  
st.sidebar.header("CSV Import/Export")  
  
# CSV Import  
upload_option = st.sidebar.selectbox("Select table to update via CSV upload",   
                                     ["Employees", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records"])  
uploaded_file = st.sidebar.file_uploader("Upload CSV for " + upload_option, type=["csv"])  
if uploaded_file is not None:  
    try:  
        df_uploaded = pd.read_csv(uploaded_file)  
        if upload_option == "Employees":  
            st.session_state.employees = df_uploaded  
        elif upload_option == "One-on-One Meetings":  
            st.session_state.meetings = df_uploaded  
        elif upload_option == "Disciplinary Actions":  
            st.session_state.disciplinary = df_uploaded  
        elif upload_option == "Performance Reviews":  
            st.session_state.performance = df_uploaded  
        elif upload_option == "Training Records":  
            st.session_state.training = df_uploaded  
        st.sidebar.success(upload_option + " data uploaded successfully!")  
    except Exception as e:  
        st.sidebar.error("Error uploading CSV: " + str(e))  
  
# CSV Download  
st.sidebar.header("Download CSV Data")  
def get_csv_download_link(df, table_name):  
    csv = df.to_csv(index=False)  
    b64 = base64.b64encode(csv.encode()).decode()   
    href = f'<a href="data:file/csv;base64,{b64}" download="{table_name}.csv">Download {table_name.capitalize()} CSV File</a>'  
    return href  
  
selected_download = st.sidebar.selectbox("Select table to download CSV",   
                                           ["Employees", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records"])  
if selected_download == "Employees":  
    st.sidebar.markdown(get_csv_download_link(st.session_state.employees, "employees"), unsafe_allow_html=True)  
elif selected_download == "One-on-One Meetings":  
    st.sidebar.markdown(get_csv_download_link(st.session_state.meetings, "meetings"), unsafe_allow_html=True)  
elif selected_download == "Disciplinary Actions":  
    st.sidebar.markdown(get_csv_download_link(st.session_state.disciplinary, "disciplinary"), unsafe_allow_html=True)  
elif selected_download == "Performance Reviews":  
    st.sidebar.markdown(get_csv_download_link(st.session_state.performance, "performance"), unsafe_allow_html=True)  
elif selected_download == "Training Records":  
    st.sidebar.markdown(get_csv_download_link(st.session_state.training, "training"), unsafe_allow_html=True)  
  
# SMTP Settings for sending emails via Outlook  
st.sidebar.header("SMTP Email Settings")  
smtp_server = st.sidebar.text_input("SMTP Server (e.g., smtp.office365.com)", value="smtp.office365.com")  
smtp_port = st.sidebar.number_input("SMTP Port", value=587, step=1)  
smtp_user = st.sidebar.text_input("Admin Email", value="your_admin@yourdomain.com")  
smtp_password = st.sidebar.text_input("SMTP Password", type="password")  
  
# -------------------------------  
# 5. Functions for Email and Calendar Integration  
# -------------------------------  
def send_meeting_email(meeting_data, employee_email):  
    try:  
        msg = MIMEMultipart()  
        msg["From"] = smtp_user  
        msg["To"] = employee_email  
        msg["Subject"] = "One-on-One Meeting Details"  
        body = f"""  
Dear {get_employee_display_name(meeting_data.get('employee_id'))},  
  
Here are the details of your upcoming one-on-one meeting:  
  
Meeting Agenda: {meeting_data.get('Meeting Agenda')}  
Action Items: {meeting_data.get('action_items')}  
Next Meeting Date: {meeting_data.get('next_meeting_date')}  
  
Please prepare accordingly.  
  
Best regards,  
Admin  
"""  
        msg.attach(MIMEText(body, 'plain'))  
        server = smtplib.SMTP(smtp_server, smtp_port)  
        server.starttls()  
        server.login(smtp_user, smtp_password)  
        server.send_message(msg)  
        server.quit()  
        st.success("Email notification sent successfully!")  
    except Exception as e:  
        st.error("Failed to send email: " + str(e))  
  
def update_microsoft_calendar(meeting_data):  
    # Placeholder: Integrate with Outlook/Exchange to update calendar.  
    st.info("Microsoft Calendar updated for next meeting date: " + str(meeting_data.get('next_meeting_date')))  
  
# -------------------------------  
# 6. Main App Navigation (Module Selection)  
# -------------------------------  
module = st.selectbox("Select Module",   
                      ["Employees", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records"])  
  
# -------------------------------  
# Module: Employees  
# -------------------------------  
if module == "Employees":  
    st.header("Employee Management")  
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
        date_of_birth = st.date_input("Date of Birth", datetime.date(1990, 1, 1))  
        manager_id = st.text_input("Manager ID (max 6 digits)", max_chars=6)  
        employment_status = st.selectbox("Employment Status", ["Active", "Inactive", "Terminated"])  
        submitted_emp = st.form_submit_button("Add Employee")  
        if submitted_emp:  
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
                    "address": [address],  
                    "date_of_birth": [date_of_birth.strftime('%Y-%m-%d')],  
                    "manager_id": [manager_id],  
                    "employment_status": [employment_status]  
                })  
                st.session_state.employees = pd.concat([st.session_state.employees, new_emp], ignore_index=True)  
                st.success("Employee added successfully!")  
    st.subheader("Employees Table")  
    st.dataframe(st.session_state.employees)  
    if st.button("Save Employees Data"):  
        save_table("employees", st.session_state.employees)  
  
# -------------------------------  
# Module: One-on-One Meetings  
# -------------------------------  
elif module == "One-on-One Meetings":  
    st.header("One-on-One Meetings")  
    with st.form("meeting_form"):  
        meeting_id = st.text_input("Meeting ID (max 6 digits)", max_chars=6)  
        employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
        manager_id = st.text_input("Manager ID (max 6 digits)", max_chars=6)  
        meeting_date = st.date_input("Meeting Date", datetime.date.today())  
        meeting_time = st.time_input("Meeting Time", datetime.datetime.now().time())  
        meeting_agenda = st.text_area("Meeting Agenda")  
        action_items = st.text_area("Action Items")  
        notes = st.text_area("Notes")  
        next_meeting_date = st.date_input("Next Meeting Date", datetime.date.today())  
        submitted_meeting = st.form_submit_button("Record Meeting")  
        if submitted_meeting:  
            if meeting_id == "" or not meeting_id.isdigit():  
                st.error("Please enter a valid numeric Meeting ID (up to 6 digits).")  
            elif employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            elif manager_id == "" or not manager
