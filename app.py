import os  
import streamlit as st  
import pandas as pd  
import matplotlib.pyplot as plt  
import datetime  
import smtplib  
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart  
  
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
# 3. Admin Settings in Sidebar  
# -------------------------------  
st.sidebar.header("Admin Settings")  
admin_email = st.sidebar.text_input("Admin Email", value="", help="Email used to send notifications to employees.")  
smtp_server = st.sidebar.text_input("SMTP Server", value="smtp.office365.com")  
smtp_port = st.sidebar.number_input("SMTP Port", value=587, step=1)  
smtp_user = st.sidebar.text_input("SMTP Username", value="", help="Your Outlook or Office365 email address.")  
smtp_password = st.sidebar.text_input("SMTP Password", type="password", help="Your SMTP password.")  
  
# CSV Upload and Download Section  
st.sidebar.header("CSV Import/Export")  
upload_table = st.sidebar.selectbox("Select Table to Update", ["employees", "meetings", "disciplinary", "performance", "training"])  
uploaded_file = st.sidebar.file_uploader("Upload CSV", type="csv")  
if uploaded_file is not None:  
    df_upload = pd.read_csv(uploaded_file)  
    # Update corresponding table in session state based on selection:  
    st.session_state[upload_table] = df_upload  
    st.sidebar.success(f"{upload_table.capitalize()} table updated from uploaded CSV!")  
      
def download_link(df, table_name):  
    csv = df.to_csv(index=False)  
    b64 = base64.b64encode(csv.encode()).decode()   
    href = f'<a href="data:file/csv;base64,{b64}" download="{table_name}.csv">Download {table_name.capitalize()} CSV</a>'  
    return href  
  
st.sidebar.markdown(download_link(load_table("employees", ['employee_id', 'first_name', 'last_name', 'employee_number',  
                                                              'department', 'job_title', 'hire_date', 'email', 'phone',  
                                                              'address', 'date_of_birth', 'manager_id', 'employment_status']),  
                                      "employees"), unsafe_allow_html=True)  
st.sidebar.markdown(download_link(load_table("meetings", ['meeting_id', 'employee_id', 'manager_id', 'meeting_date',  
                                                            'meeting_time', 'Meeting Agenda', 'action_items', 'notes',  
                                                            'next_meeting_date']),  
                                    "meetings"), unsafe_allow_html=True)  
  
# -------------------------------  
# 4. Initialize Tables in Session State  
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
        'review_id', 'employee_id', 'review_date', 'reviewer_id',  
        'rating', 'comments'  
    ])  
  
if 'training' not in st.session_state:  
    st.session_state.training = load_table('training', [  
        'training_id', 'employee_id', 'training_date', 'training_type',  
        'completion_status', 'notes'  
    ])  
  
# -------------------------------  
# 5. Helper Functions for Email and Calendar Update  
# -------------------------------  
def send_meeting_email(employee_email, meeting_data):  
    # meeting_data is a dict containing meeting details  
    try:  
        msg = MIMEMultipart()  
        msg['From'] = smtp_user  
        msg['To'] = employee_email  
        msg['Subject'] = "One-on-One Meeting Details"  
        body = f"""Dear Employee,  
  
Here are the details of your one-on-one meeting with your manager:  
  
Meeting Agenda: {meeting_data.get('Meeting Agenda')}  
Action Items: {meeting_data.get('action_items')}  
Next Meeting Date: {meeting_data.get('next_meeting_date')}  
  
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
    # Placeholder for Microsoft calendar update functionality.  
    # This function should integrate with Outlook COM or Exchange Web Services  
    # to create/update a calendar event for the next meeting date.  
    # For now, we simply simulate the behavior.  
    st.info("Microsoft Calendar has been updated with the next meeting date (" + meeting_data.get('next_meeting_date') + ") (simulation).")  
  
# -------------------------------  
# 6. Main App Navigation (Using a Selectbox for the Module)  
# -------------------------------  
module = st.selectbox("Select Module", ["Employees", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records"])  
  
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
      
