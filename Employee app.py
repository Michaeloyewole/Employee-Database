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
    try:  
        return pd.read_csv(path)  
    except Exception as e:  
        st.error("Error loading {}: ".format(table_name) + str(e))  
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
    if not employee.empty and 'email' in employee.columns:  
        return employee['email'].values[0]  
    return None  
  
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
        'disciplinary_id', 'employee_id', 'type', 'date', 'description'  
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
# 4. Sidebar Navigation  
# -------------------------------  
st.sidebar.header("Navigation")  
module = st.sidebar.radio("Select Module", [  
    "Employee Management",  
    "One-on-One Meetings",  
    "Disciplinary Actions",  
    "Performance Reviews",  
    "Training Records",  
    "Reports"  
])  
  
# -------------------------------  
# 5. Module: Employee Management  
# -------------------------------  
if module == "Employee Management":  
    st.header("Employee Management")  
    with st.form("employee_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            first_name = st.text_input("First Name")  
            last_name = st.text_input("Last Name")  
            employee_number = st.text_input("Employee Number")  
            department = st.text_input("Department")  
            job_title = st.text_input("Job Title")  
        with col2:  
            hire_date = st.date_input("Hire Date", datetime.date.today())  
            email = st.text_input("Email")  
            phone = st.text_input("Phone")  
            address = st.text_input("Address")  
            date_of_birth = st.date_input("Date of Birth", datetime.date(1990,1,1))  
            manager_id = st.text_input("Manager ID (max 6 digits)", max_chars=6)  
        employment_status = st.selectbox("Employment Status", ["Active", "Inactive", "Terminated"])  
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
# 6. Module: One-on-One Meetings  
# -------------------------------  
elif module == "One-on-One Meetings":  
    st.header("One-on-One Meetings")  
    with st.form("meeting_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            meeting_id = st.text_input("Meeting ID (max 6 digits)", max_chars=6)  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            meeting_date = st.date_input("Meeting Date", datetime.date.today())  
            meeting_agenda = st.text_area("Meeting Agenda")  
            notes = st.text_area("Notes")  
        with col2:  
            manager_id = st.text_input("Manager ID (max 6 digits)", max_chars=6)  
            meeting_time = st.time_input("Meeting Time", datetime.datetime.now().time())  
            action_items = st.text_area("Action Items")  
            next_meeting_date = st.date_input("Next Meeting Date", datetime.date.today())  
        submitted_meeting = st.form_submit_button("Record Meeting")  
        if submitted_meeting:  
            if meeting_id == "" or not meeting_id.isdigit():  
                st.error("Please enter a valid numeric Meeting ID (up to 6 digits).")  
            elif employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            elif manager_id == "" or not manager_id.isdigit():  
                st.error("Please enter a valid numeric Manager ID (up to 6 digits).")  
            else:  
                new_meeting = pd.DataFrame({  
                    "meeting_id": [meeting_id],  
                    "employee_id": [employee_id],  
                    "manager_id": [manager_id],  
                    "meeting_date": [meeting_date.strftime('%Y-%m-%d')],  
                    "meeting_time": [meeting_time.strftime('%H:%M:%S')],  
                    "Meeting Agenda": [meeting_agenda],  
                    "action_items": [action_items],  
                    "notes": [notes],  
                    "next_meeting_date": [next_meeting_date.strftime('%Y-%m-%d')]  
                })  
                st.session_state.meetings = pd.concat([st.session_state.meetings, new_meeting], ignore_index=True)  
                st.success("Meeting recorded successfully!")  
    st.subheader("Meetings Table")  
    st.dataframe(st.session_state.meetings)  
    if st.button("Save Meetings Data"):  
        save_table("meetings", st.session_state.meetings)  
  
# -------------------------------  
# 7. Module: Disciplinary Actions  
# -------------------------------  
elif module == "Disciplinary Actions":  
    st.header("Disciplinary Actions")  
    with st.form("disciplinary_form"):  
        disciplinary_id = st.text_input("Disciplinary ID (max 6 digits)", max_chars=6)  
        employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
        dtype = st.text_input("Type")  
        date = st.date_input("Date", datetime.date.today())  
        description = st.text_area("Description")  
        submitted_disciplinary = st.form_submit_button("Record Disciplinary Action")  
        if submitted_disciplinary:  
            if disciplinary_id == "" or not disciplinary_id.isdigit():  
                st.error("Please enter a valid numeric Disciplinary ID (up to 6 digits).")  
            elif employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID
