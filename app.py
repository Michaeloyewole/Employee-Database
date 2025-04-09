import os  
import io  
import base64  
import streamlit as st  
import pandas as pd  
import matplotlib.pyplot as plt  
import datetime  
import smtplib  
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart  
import requests  
  
# --------------------------------------------------  
# 1. Page Configuration & Data Directory  
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
# 3. CSV Import/Export Utility Functions  
# --------------------------------------------------  
def get_csv_download_link(df, filename="data.csv"):  
    csv = df.to_csv(index=False).encode('utf-8')  
    b64 = base64.b64encode(csv).decode("utf-8")  
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'  
  
def import_csv_to_table(df, table_name):  
    # Save imported CSV to data directory  
    save_table(table_name, df)  
    st.success(f"Imported CSV to {table_name} table successfully!")  
  
# --------------------------------------------------  
# 4. Utilities for Employee Lookup  
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
# 5. Email and Calendar Integration Functions  
# --------------------------------------------------  
def send_meeting_email(employee_id, meeting_date, meeting_time, meeting_agenda, action_items, next_meeting_date):  
    employee_email = get_employee_email(employee_id)  
    if not employee_email:  
        st.warning("Could not find employee email. Email notification not sent.")  
        return False  
      
    # Retrieve admin credentials (set in sidebar)  
    admin_email = st.session_state.get('admin_email', '')  
    admin_password = st.session_state.get('admin_password', '')  
      
    if not admin_email or not admin_password:  
        st.warning("Admin email credentials not set. Email notification not sent.")  
        return False  
      
    subject = "One-on-One Meeting Summary"  
      
    # Build the email body without escape issues  
    body = "Dear " + get_employee_display_name(employee_id) + ",\n\n"  
    body += "This is a summary of your recent one-on-one meeting:\n\n"  
    body += "Date: " + meeting_date + "\n"  
    body += "Time: " + meeting_time + "\n\n"  
    body += "Meeting Agenda:\n" + meeting_agenda + "\n\n"  
    body += "Action Items:\n" + action_items + "\n\n"  
    body += "Next Meeting Date: " + next_meeting_date + "\n\n"  
    body += "Please let me know if you have any questions.\n\n"  
    body += "Regards,\nYour Manager"  
      
    try:  
        msg = MIMEMultipart()  
        msg['From'] = admin_email  
        msg['To'] = employee_email  
        msg['Subject'] = subject  
        msg.attach(MIMEText(body, 'plain'))  
          
        # Outlook SMTP settings (adjust as needed)  
        server = smtplib.SMTP('smtp-mail.outlook.com', 587)  
        server.starttls()  
        server.login(admin_email, admin_password)  
        server.send_message(msg)  
        server.quit()  
          
        st.success("Meeting summary email sent to employee.")  
        return True  
    except Exception as e:  
        st.error("Failed to send email: " + str(e))  
        return False  
  
def update_ms_calendar(employee_id, meeting_date, meeting_time, next_meeting_date):  
    # Placeholder for Microsoft Graph API integration.  
    # To fully implement, supply your credentials and complete the API call.  
    st.info("MS Calendar update called for employee " + str(employee_id))  
    # Example: requests.post('https://graph.microsoft.com/v1.0/me/events', json=event_data)  
    return True  
  
# --------------------------------------------------  
# 6. Sidebar: CSV Upload/Download & Admin Credentials  
# --------------------------------------------------  
st.sidebar.header("Data Management")  
table_to_update = st.sidebar.selectbox("Select table to update", ["employees", "meetings", "disciplinary", "performance", "training"])  
csv_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])  
if csv_file is not None:  
    try:  
        df_csv = pd.read_csv(csv_file, dtype=str)  
        import_csv_to_table(df_csv, table_to_update)  
        if table_to_update == "employees":  
            st.session_state.employees = df_csv  
        elif table_to_update == "meetings":  
            st.session_state.meetings = df_csv  
        # Add similar handling for other tables if necessary.  
    except Exception as e:  
        st.error("Error reading CSV: " + str(e))  
  
st.sidebar.header("Download Data")  
if st.sidebar.button("Download Employees CSV"):  
    if 'employees' in st.session_state and not st.session_state.employees.empty:  
        tmp_download_link = get_csv_download_link(st.session_state.employees, "employees.csv")  
        st.sidebar.markdown(tmp_download_link, unsafe_allow_html=True)  
    else:  
        st.sidebar.warning("Employees data is empty.")  
  
# Admin email settings for automatic email notifications  
st.sidebar.header("Admin Email Settings (Outlook)")  
st.session_state.admin_email = st.sidebar.text_input("Admin Email")  
st.session_state.admin_password = st.sidebar.text_input("Admin Password", type="password")  
  
# --------------------------------------------------  
# 7. Main Navigation  
# --------------------------------------------------  
module = st.selectbox("Select Module", ["Employees", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records"])  
  
# --------------------------------------------------  
# 8. Module: Employees  
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
                    if 'employees' in st.session_state and not st.session_state.employees.empty:  
                        st.session_state.employees = pd.concat([st.session_state.employees, new_emp], ignore_index=True)  
                    else:  
                        st.session_state.employees = new_emp  
                    st.success("Employee added!")  
    with col2:  
        st.subheader("Employees Table")  
        if 'employees' in st.session_state:  
            st.dataframe(st.session_state.employees)  
            if st.button("Save Employees Data"):  
                save_table("employees", st.session_state.employees)  
        else:  
            st.info("No employee records to display.")  
  
# --------------------------------------------------  
# 9. Module: One-on-One Meetings  
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
