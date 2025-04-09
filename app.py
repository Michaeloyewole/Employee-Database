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
def load_table(table_name, columns, encoding="latin1"):  
    path = os.path.join(DATA_DIR, f'{table_name}.csv')  
    try:  
        return pd.read_csv(path, encoding=encoding)  
    except Exception as e:  
        st.error(f"Error loading {table_name}: {str(e)}")  
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
  
def send_email_notification(employee_id, meeting_data):  
    employee_email = get_employee_email(employee_id)  
    if not employee_email:  
        st.warning("Could not find employee email to send notification.")  
        return False  
      
    try:  
        # Configure these with your actual SMTP settings  
        smtp_server = "smtp.example.com"  
        smtp_port = 587  
        smtp_username = "your_email@example.com"  
        smtp_password = "your_password"  
          
        msg = MIMEMultipart()  
        msg['From'] = smtp_username  
        msg['To'] = employee_email  
        msg['Subject'] = f"One-on-One Meeting Scheduled for {meeting_data['meeting_date']}"  
          
        body = f"""  
        Hello {get_employee_display_name(employee_id)},  
          
        A one-on-one meeting has been scheduled with {get_employee_display_name(meeting_data['manager_id'])} on {meeting_data['meeting_date']} at {meeting_data['meeting_time']}.  
          
        Meeting Agenda: {meeting_data['Meeting Agenda']}  
          
        Please prepare for the meeting.  
          
        Regards,  
        HR Department  
        """  
          
        msg.attach(MIMEText(body, 'plain'))  
          
        # Uncomment to actually send emails  
        # server = smtplib.SMTP(smtp_server, smtp_port)  
        # server.starttls()  
        # server.login(smtp_username, smtp_password)  
        # server.send_message(msg)  
        # server.quit()  
          
        st.success("Email notification would be sent (SMTP functionality is commented out)")  
        return True  
    except Exception as e:  
        st.error(f"Error sending email: {str(e)}")  
        return False  
  
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
        'meeting_time', 'Meeting Agenda', 'action_items', 'notes', 'next_meeting_date'  
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
# 4. Sidebar Navigation and Import/Export  
# -------------------------------  
st.sidebar.title("Navigation")  
module = st.sidebar.radio(  
    "Select Module",  
    ["Employee Management", "One-on-One Meetings", "Disciplinary Actions",   
     "Performance Reviews", "Training Records", "Reports"]  
)  
  
# CSV Import/Export in Sidebar  
st.sidebar.header("Import/Export Data")  
import_export_option = st.sidebar.selectbox(  
    "Select Option",  
    ["Import CSV", "Export CSV"]  
)  
  
if import_export_option == "Import CSV":  
    table_to_import = st.sidebar.selectbox(  
        "Select Table to Import",  
        ["employees", "meetings", "disciplinary", "performance", "training"]  
    )  
    uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])  
    if uploaded_file is not None:  
        try:  
            df_uploaded = pd.read_csv(uploaded_file, encoding="latin1")  
            if st.sidebar.button("Import Data"):  
                if table_to_import == "employees":  
                    st.session_state.employees = df_uploaded  
                elif table_to_import == "meetings":  
                    st.session_state.meetings = df_uploaded  
                elif table_to_import == "disciplinary":  
                    st.session_state.disciplinary = df_uploaded  
                elif table_to_import == "performance":  
                    st.session_state.performance = df_uploaded  
                elif table_to_import == "training":  
                    st.session_state.training = df_uploaded  
                save_table(table_to_import, df_uploaded)  
                st.sidebar.success(f"Data imported to {table_to_import} successfully!")  
        except Exception as e:  
            st.sidebar.error(f"Error uploading CSV: {str(e)}")  
  
elif import_export_option == "Export CSV":  
    table_to_export = st.sidebar.selectbox(  
        "Select Table to Export",  
        ["employees", "meetings", "disciplinary", "performance", "training"]  
    )  
    if st.sidebar.button("Export Data"):  
        if table_to_export == "employees":  
            csv = st.session_state.employees.to_csv(index=False)  
        elif table_to_export == "meetings":  
            csv = st.session_state.meetings.to_csv(index=False)  
        elif table_to_export == "disciplinary":  
            csv = st.session_state.disciplinary.to_csv(index=False)  
        elif table_to_export == "performance":  
            csv = st.session_state.performance.to_csv(index=False)  
        elif table_to_export == "training":  
            csv = st.session_state.training.to_csv(index=False)  
          
        b64 = base64.b64encode(csv.encode()).decode()  
        href = f'<a href="data:file/csv;base64,{b64}" download="{table_to_export}.csv">Download {table_to_export}.csv</a>'  
        st.sidebar.markdown(href, unsafe_allow_html=True)  
        st.sidebar.success(f"{table_to_export.capitalize()} data ready for download!")  
  
# -------------------------------  
# 5. Employee Management Module  
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
            address = st.text_area("Address")  
            date_of_birth = st.date_input("Date of Birth", datetime.date(1990, 1, 1))  
            manager_id = st.text_input("Manager ID (max 6 digits)", max_chars=6)  
            employment_status = st.selectbox("Employment Status", ["Active", "Terminated", "On Leave", "Retired"])  
          
        submitted_employee = st.form_submit_button("Add Employee")  
          
        if submitted_employee:  
            if employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            elif manager_id != "" and not manager_id.isdigit():  
                st.error("Please enter a valid numeric Manager ID (up to 6 digits).")  
            else:  
                new_employee = pd.DataFrame({  
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
                st.session_state.employees = pd.concat([st.session_state.employees, new_employee], ignore_index=True)  
                st.success("Employee added successfully!")  
      
    st.subheader("Employees Table")  
    st.dataframe(st.session_state.employees)  
    if st.button("Save Employee Data"):  
        save_table("employees", st.session_state.employees)  
  
# -------------------------------  
# 6. One-on-One Meetings Module  
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
            next_meeting_date = st.date_input("Next Meeting Date", datetime.date.today() + datetime.timedelta(days=30))  
              
            # Microsoft Calendar Integration Placeholder  
            ms_calendar_integration = st.checkbox("Add to Microsoft Calendar")  
            if ms_calendar_integration:  
                st.info("Microsoft Calendar integration will be implemented here.")  
                  
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
                  
                # Send email notification  
                meeting_data = {  
                    "meeting_date": meeting_date.strftime('%Y-%m-%d'),  
                    "meeting_time": meeting_time.strftime('%H:%M:%S'),  
                    "manager_id": manager_id,  
                    "Meeting Agenda": meeting_agenda  
                }  
                send_email_notification(employee_id, meeting_data)  
                  
                st.success("Meeting recorded successfully!")  
    st.subheader("Meetings Table")  
    st.dataframe(st.session_state.meetings)  
    if st.button("Save Meetings Data"):  
        save_table("meetings", st.session_state.meetings)  
  
# -------------------------------  
# 7. Disciplinary Actions Module  
# -------------------------------  
elif module == "Disciplinary Actions":  
    st.header("Disciplinary Actions")  
    with st.form("disciplinary_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            disciplinary_id = st.text_input("Disciplinary ID (max 6 digits)", max_chars=6)  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            dtype = st.text_input("Type")  
        with col2:  
            date = st.date_input("Date", datetime.date.today())  
            description = st.text_area("Description")  
        submitted_disciplinary = st.form_submit_button("Record Disciplinary Action")  
        if submitted_disciplinary:  
            if disciplinary_id == "" or not disciplinary_id.isdigit():  
                st.error("Please enter a valid numeric Disciplinary ID (up to 6 digits).")  
            elif employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            else:  
                new_disc = pd.DataFrame({  
                    "disciplinary_id": [disciplinary_id],  
                    "employee_id": [employee_id],  
                    "type": [dtype],  
                    "date": [date.strftime('%Y-%m-%d')],  
                    "description": [description]  
                })  
                st.session_state.disciplinary = pd.concat([st.session_state.disciplinary, new_disc], ignore_index=True)  
                st.success("Disciplinary action recorded successfully!")  
    st.subheader("Disciplinary Actions Table")  
    st.dataframe(st.session_state.disciplinary)  
    if st.button("Save Disciplinary Data"):  
        save_table("disciplinary", st.session_state.disciplinary)  
  
# -------------------------------  
# 8. Performance Reviews Module  
# -------------------------------  
elif module == "Performance Reviews":  
    st.header("Performance Reviews")  
    with st.form("performance_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            review_id = st.text_input("Review ID (max 6 digits)", max_chars=6)  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            review_date = st.date_input("Review Date", datetime.date.today())  
        with col2:  
            reviewer = st.text_input("Reviewer")  
            score = st.number_input("Score", min_value=1, max_value=5, value=3)  
            comments = st.text_area("Comments")  
        submitted_review = st.form_submit_button("Record Performance Review")  
        if submitted_review:  
            if review_id == "" or not review_id.isdigit():  
                st.error("Please enter a valid numeric Review ID (up to 6 digits).")  
            elif employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            else:  
                new_review = pd.DataFrame({  
                    "review_id": [review_id],  
                    "employee_id": [employee_id],  
                    "review_date": [review_date.strftime('%Y-%m-%d')],  
                    "reviewer": [reviewer],  
                    "score": [score],  
                    "comments": [comments]  
                })  
                st.session_state.performance = pd.concat([st.session_state.performance, new_review], ignore_index=True)  
                st.success("Performance review recorded successfully!")  
    st.subheader("Performance Reviews Table")  
    st.dataframe(st.session_state.performance)  
    if st.button("Save Performance Data"):  
        save_table("performance", st.session_state.performance)  
  
# -------------------------------  
# 9. Training Records Module  
# -------------------------------  
elif module == "Training Records":  
    st.header("Training Records")  
    with st.form("training_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            training_id = st.text_input("Training ID (max 6 digits)", max_chars=6)  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            training_date = st.date_input("Training Date", datetime.date.today())  
        with col2:  
            course_name = st.text_input("Course Name")  
            status = st.selectbox("Status", ["Completed", "In Progress", "Not Started", "Failed"])  
        submitted_training = st.form_submit_button("Record Training")  
        if submitted_training:  
            if training_id == "" or not training_id.isdigit():  
                st.error("Please enter a valid numeric Training ID (up to 6 digits).")  
            elif employee_
