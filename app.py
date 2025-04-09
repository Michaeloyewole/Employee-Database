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
  
# CSV Import functionality  
upload_table = st.sidebar.selectbox("Select Table to Import CSV",   
                                   ["Employees", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records"])  
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])  
if uploaded_file is not None:  
    try:  
        df_uploaded = pd.read_csv(uploaded_file)  
        if upload_table == "Employees":  
            st.session_state.employees = df_uploaded  
        elif upload_table == "One-on-One Meetings":  
            st.session_state.meetings = df_uploaded  
        elif upload_table == "Disciplinary Actions":  
            st.session_state.disciplinary = df_uploaded  
        elif upload_table == "Performance Reviews":  
            st.session_state.performance = df_uploaded  
        elif upload_table == "Training Records":  
            st.session_state.training = df_uploaded  
        st.sidebar.success(f"{upload_table} table updated successfully from CSV!")  
    except Exception as e:  
        st.sidebar.error("Error uploading CSV: " + str(e))  
  
# CSV Export functionality  
export_table = st.sidebar.selectbox("Select Table to Export CSV",   
                                   ["Employees", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records"])  
if st.sidebar.button("Download CSV"):  
    if export_table == "Employees":  
        csv = st.session_state.employees.to_csv(index=False).encode('utf-8')  
    elif export_table == "One-on-One Meetings":  
        csv = st.session_state.meetings.to_csv(index=False).encode('utf-8')  
    elif export_table == "Disciplinary Actions":  
        csv = st.session_state.disciplinary.to_csv(index=False).encode('utf-8')  
    elif export_table == "Performance Reviews":  
        csv = st.session_state.performance.to_csv(index=False).encode('utf-8')  
    elif export_table == "Training Records":  
        csv = st.session_state.training.to_csv(index=False).encode('utf-8')  
    b64 = base64.b64encode(csv).decode('utf-8')  
    href = f'<a href="data:file/csv;base64,{b64}" download="{export_table}.csv">Download CSV File</a>'  
    st.sidebar.markdown(href, unsafe_allow_html=True)  
  
# SMTP Settings for Email Notifications  
st.sidebar.header("SMTP Email Settings")  
smtp_server = st.sidebar.text_input("SMTP Server", value="smtp.office365.com")  
smtp_port = st.sidebar.number_input("SMTP Port", value=587, step=1)  
smtp_user = st.sidebar.text_input("Admin Email", value="admin@example.com")  
smtp_password = st.sidebar.text_input("Email Password", type="password")  
  
# -------------------------------  
# 5. Email and Calendar Functions  
# -------------------------------  
def send_meeting_email(meeting_data):  
    try:  
        employee_email = get_employee_email(meeting_data.get('employee_id'))  
        if not employee_email:  
            st.warning("No email found for this employee. Email notification not sent.")  
            return  
              
        msg = MIMEMultipart()  
        msg['From'] = smtp_user  
        msg['To'] = employee_email  
        msg['Subject'] = "One-on-One Meeting Details"  
          
        body = f"""  
Dear {get_employee_display_name(meeting_data.get('employee_id'))},  
  
Here is a summary of your recent one-on-one meeting with your manager:  
  
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
  
elif module == "One-on-One Meetings":  
    st.header("One-on-One Meetings")  
    with st.form("meeting_form"):  
        meeting_id = st.text_input("Meeting ID (max 6 digits)", max_chars=6)  
        employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
        manager_id = st.text_input("Manager ID (max 6 digits)", max_chars=6)  
        meeting_date = st.date_input("Meeting Date", datetime.date.today())  
        meeting_time = st.time_input("Meeting Time", datetime.datetime.now().time())  
        meeting_agenda = st.text_area("Meeting Agenda")  # Changed from "Topics Discussed" to "Meeting Agenda"  
        action_items = st.text_area("Action Items")  
        notes = st.text_area("Notes")  
        next_meeting_date = st.date_input("Next Meeting Date", datetime.date.today() + datetime.timedelta(days=30))  
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
                    "Meeting Agenda": [meeting_agenda],  # Changed from "topics_discussed" to "Meeting Agenda"  
                    "action_items": [action_items],  
                    "notes": [notes],  
                    "next_meeting_date": [next_meeting_date.strftime('%Y-%m-%d')]  
                })  
                st.session_state.meetings = pd.concat([st.session_state.meetings, new_meeting], ignore_index=True)  
                st.success("Meeting recorded successfully!")  
                  
                # Send email notification  
                meeting_data = {  
                    "employee_id": employee_id,  
                    "Meeting Agenda": meeting_agenda,  
                    "action_items": action_items,  
                    "next_meeting_date": next_meeting_date.strftime('%Y-%m-%d')  
                }  
                send_meeting_email(meeting_data)  
                  
                # Update Microsoft Calendar  
                update_microsoft_calendar(meeting_data)  
                  
    st.subheader("One-on-One Meetings Table")  
    st.dataframe(st.session_state.meetings)  
    if st.button("Save Meetings Data"):  
        save_table("meetings", st.session_state.meetings)  
  
elif module == "Disciplinary Actions":  
    st.header("Disciplinary Actions")  
    with st.form("disciplinary_form"):  
        disciplinary_id = st.text_input("Disciplinary Action ID (max 6 digits)", max_chars=6)  
        employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
        date = st.date_input("Date", datetime.date.today())  
        action_type = st.selectbox("Type", ["Verbal Warning", "Written Warning", "Final Warning", "Suspension", "Termination"])  
        reason = st.text_input("Reason")  
        description = st.text_area("Description")  
        documentation = st.text_area("Documentation")  
        issued_by = st.text_input("Issued By (max 6 digits)", max_chars=6)  
        submitted_disc = st.form_submit_button("Record Disciplinary Action")  
        if submitted_disc:  
            if disciplinary_id == "" or not disciplinary_id.isdigit():  
                st.error("Please enter a valid numeric Disciplinary Action ID (up to 6 digits).")  
            elif employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            elif issued_by == "" or not issued_by.isdigit():  
                st.error("Please enter a valid numeric Issued By ID (up to 6 digits).")  
            else:  
                new_disc = pd.DataFrame({  
                    "disciplinary_id": [disciplinary_id],  
                    "employee_id": [employee_id],  
                    "date": [date.strftime('%Y-%m-%d')],  
                    "type": [action_type],  
                    "reason": [reason],  
                    "description": [description],  
                    "documentation": [documentation],  
                    "issued_by": [issued_by]  
                })  
                st.session_state.disciplinary = pd.concat([st.session_state.disciplinary, new_disc], ignore_index=True)  
                st.success("Disciplinary action recorded successfully!")  
    st.subheader("Disciplinary Actions Table")  
    st.dataframe(st.session_state.disciplinary)  
    if st.button("Save Disciplinary Data"):  
        save_table("disciplinary", st.session_state.disciplinary)  
  
elif module == "Performance Reviews":  
    st.header("Performance Reviews")  
    with st.form("performance_form"):  
        review_id = st.text_input("Review ID (max 6 digits)", max_chars=6)  
        employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
        review_date = st.date_input("Review Date", datetime.date.today())  
        reviewer = st.text_input("Reviewer ID (max 6 digits)", max_chars=6)  
        score = st.slider("Score", 1, 5, 3)  
        comments = st.text_area("Comments")  
        submitted_review = st.form_submit_button("Record Performance Review")  
        if submitted_review:  
            if review_id == "" or not review_id.isdigit():  
                st.error("Please enter a valid numeric Review ID (up to 6 digits).")  
            elif employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            elif reviewer == "" or not reviewer.isdigit():  
                st.error("Please enter a valid numeric Reviewer ID (up to 6 digits).")  
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
  
elif module == "Training Records":  
    st.header("Training Records")  
    with st.form("training_form"):  
        training_id = st.text_input("Training ID (max 6 digits)", max_chars=6)  
        employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
        training_date = st.date_input("Training Date", datetime.date.today())  
        course_name = st.text_input("Course Name")  
        status = st.selectbox("Status", ["Completed", "In Progress", "Not Started", "Failed"])  
        submitted_training = st.form_submit_button("Record Training")  
        if submitted_training:  
            if training_id == "" or not training_id.isdigit():  
                st.error("Please enter a valid numeric Training ID (up to 6 digits).")  
            elif employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            else:  
                new_training = pd.DataFrame({  
                    "training_id": [training_id],  
                    "employee_id": [employee_id],  
                    "training_date": [training_date.strftime('%Y-%m-%d')],  
                    "course_name": [course_name],  
                    "status": [status]  
                })  
                st.session_state.training = pd.concat([st.session_state.training, new_training], ignore_index=True)  
                st.success("Training record added successfully!")  
    st.subheader("Training Records Table")  
    st.dataframe(st.session_state.training)  
    if st.button("Save Training Data"):  
        save_table("training", st.session_state.training)  
