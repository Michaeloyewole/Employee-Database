import os  
import io  
import streamlit as st  
import pandas as pd  
import matplotlib.pyplot as plt  
import datetime  
import smtplib  
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart  
import requests  
  
# --------------------------------------------------  
# 1. Page Config & Data Directory  
# --------------------------------------------------  
st.set_page_config(  
    page_title="Employee Records Tool",  
    page_icon="👥",  
    layout="wide",  
    initial_sidebar_state="expanded"  
)  
  
DATA_DIR = 'data'  
if not os.path.exists(DATA_DIR):  
    os.makedirs(DATA_DIR)  
  
# --------------------------------------------------  
# 2. Data Persistence Functions  
# --------------------------------------------------  
def load_table(table_name, columns):  
    path = os.path.join(DATA_DIR, f'{table_name}.csv')  
    if os.path.exists(path):  
        return pd.read_csv(path, dtype=str)  
    else:  
        return pd.DataFrame({col: [] for col in columns})  
  
def save_table(table_name, df):  
    path = os.path.join(DATA_DIR, f'{table_name}.csv')  
    df.to_csv(path, index=False)  
    st.success(f"{table_name.capitalize()} data saved successfully!")  
  
# --------------------------------------------------  
# 3. Utilities for Employee Lookup  
# --------------------------------------------------  
def get_employee_display_name(emp_id):  
    if not emp_id:  
        return "N/A"  
    df = st.session_state.employees  
    employee = df[df['employee_id'] == str(emp_id)]  
    if not employee.empty:  
        return employee.iloc[0]['first_name'] + " " + employee.iloc[0]['last_name']  
    return "Unknown"  
  
def get_employee_email(emp_id):  
    if not emp_id:  
        return None  
    df = st.session_state.employees  
    employee = df[df['employee_id'] == str(emp_id)]  
    if not employee.empty:  
        return employee.iloc[0]['email']  
    return None  
  
# --------------------------------------------------  
# 4. Email and Calendar Integration Functions  
# --------------------------------------------------  
def send_meeting_email(admin_email, admin_password, employee_id, meeting_date, meeting_time, agenda, action_items, next_meeting_date):  
    receiver_email = get_employee_email(employee_id)  
    if not receiver_email:  
        st.warning("Employee email not found; email not sent.")  
        return  
    subject = "Your Upcoming Meeting Details"  
    # Use triple quotes with proper formatting (avoid escaping backslashes unnecessarily)  
    body = f"""Dear {get_employee_display_name(employee_id)},  
  
This is an automated message with your meeting details.  
  
Meeting Date: {meeting_date.strftime('%Y-%m-%d')}  
Meeting Time: {meeting_time.strftime('%H:%M')}  
Meeting Agenda:  
{agenda}  
  
Action Items:  
{action_items}  
  
Your next meeting is scheduled on: {next_meeting_date.strftime('%Y-%m-%d')}  
  
Regards,  
Admin  
"""  
    try:  
        msg = MIMEMultipart()  
        msg['From'] = admin_email  
        msg['To'] = receiver_email  
        msg['Subject'] = subject  
        msg.attach(MIMEText(body, 'plain'))  
          
        # Setup Outlook SMTP server, update as needed  
        server = smtplib.SMTP('smtp.office365.com', 587)  
        server.starttls()  
        server.login(admin_email, admin_password)  
        text = msg.as_string()  
        server.sendmail(admin_email, receiver_email, text)  
        server.quit()  
        st.success("Meeting email sent successfully!")  
    except Exception as e:  
        st.error("Error sending email: " + str(e))  
  
def update_ms_calendar(employee_id, meeting_date, meeting_time, next_meeting_date):  
    # Placeholder function: Integrate with Microsoft Graph API here.  
    # You must implement OAuth, get an access token, and then update the calendar.  
    # This is a stub function.  
    st.info("MS Calendar updated (placeholder).")  
    return  
  
# --------------------------------------------------  
# 5. Sidebar: CSV Import & Export and Admin Credentials  
# --------------------------------------------------  
st.sidebar.header("Data Management and Admin Settings")  
  
# CSV Import  
import_option = st.sidebar.file_uploader("Import CSV (select file)", type=["csv"])  
table_option = st.sidebar.selectbox("Select table to update", ("employees", "meetings", "disciplinary", "performance", "training"))  
if import_option is not None:  
    try:  
        df_import = pd.read_csv(import_option, dtype=str)  
        if table_option == "employees":  
            st.session_state.employees = df_import  
        elif table_option == "meetings":  
            st.session_state.meetings = df_import  
        elif table_option == "disciplinary":  
            st.session_state.disciplinary = df_import  
        elif table_option == "performance":  
            st.session_state.performance = df_import  
        elif table_option == "training":  
            st.session_state.training = df_import  
        st.sidebar.success(f"Updated {table_option} table successfully!")  
    except Exception as e:  
        st.sidebar.error("Failed to load CSV: " + str(e))  
  
# CSV Download links  
def get_csv_download_link(df, table_name):  
    csv = df.to_csv(index=False).encode('utf-8')  
    b64 = base64.b64encode(csv).decode()  
    href = f'<a href="data:file/csv;base64,{b64}" download="{table_name}.csv">Download {table_name} data as CSV</a>'  
    return href  
  
st.sidebar.markdown(get_csv_download_link(load_table("employees", [  
    'employee_id', 'first_name', 'last_name', 'employee_number',  
    'department', 'job_title', 'hire_date', 'email', 'phone',  
    'address', 'date_of_birth', 'manager_id', 'employment_status'  
]), "employees"), unsafe_allow_html=True)  
  
# Admin Credentials for Email and Calendar  
st.sidebar.header("Admin Settings")  
admin_email = st.sidebar.text_input("Admin Email (for sending notifications)")  
admin_password = st.sidebar.text_input("Admin Email Password", type="password")  
  
# --------------------------------------------------  
# 6. Tabs for Different Modules  
# --------------------------------------------------  
module = st.sidebar.selectbox("Select Module", ("Employees", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records"))  
  
# --------------------------------------------------  
# 7. Module: Employees  
# --------------------------------------------------  
if module == "Employees":  
    st.header("Employees")  
    col1, col2 = st.columns(2)  
    with col1:  
        st.subheader("Add New Employee")  
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
            date_of_birth = st.date_input("Date of Birth", datetime.date(1990,1,1))  
            manager_id = st.text_input("Manager ID (max 6 digits)", max_chars=6)  
            employment_status = st.selectbox("Employment Status", ["Active", "Inactive", "Terminated"])  
            submitted = st.form_submit_button("Add Employee")  
            if submitted:  
                if employee_id == "" or not employee_id.isdigit():  
                    st.error("Invalid Employee ID.")  
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
                    st.success("Employee added!")  
    with col2:  
        st.subheader("Employees Table")  
        st.dataframe(st.session_state.employees)  
        if st.button("Save Employees Data"):  
            save_table("employees", st.session_state.employees)  
  
# --------------------------------------------------  
# 8. Module: One-on-One Meetings  
# --------------------------------------------------  
elif module == "One-on-One Meetings":  
    st.header("One-on-One Meetings")  
    tab1, tab2 = st.tabs(["View Meetings", "Add Meeting"])  
    with tab1:  
        st.subheader("Meeting Records")  
        if 'meetings' in st.session_state and not st.session_state.meetings.empty:  
            st.dataframe(st.session_state.meetings)  
            if st.button("Save Meetings Data"):  
                save_table("meetings", st.session_state.meetings)  
        else:  
            st.info("No meeting records found.")  
    with tab2:  
        st.subheader("Add New Meeting")  
        with st.form("meeting_form"):  
            meeting_id = st.text_input("Meeting ID (max 6 digits)", max_chars=6)  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            manager_id = st.text_input("Manager ID (max 6 digits)", max_chars=6)  
            meeting_date = st.date_input("Meeting Date", datetime.date.today())  
            meeting_time = st.time_input("Meeting Time", datetime.time(9, 0))  
            # Renamed field  
            meeting_agenda = st.text_area("Meeting Agenda")  
            action_items = st.text_area("Action Items")  
            notes = st.text_area("Notes")  
            next_meeting_date = st.date_input("Next Meeting Date", datetime.date.today() + datetime.timedelta(days=30))  
            submitted_meeting = st.form_submit_button("Add Meeting")  
            if submitted_meeting:  
                if meeting_id == "" or not meeting_id.isdigit():  
                    st.error("Invalid Meeting ID.")  
                elif employee_id == "" or not employee_id.isdigit():  
                    st.error("Invalid Employee ID.")  
                elif manager_id == "" or not manager_id.isdigit():  
                    st.error
