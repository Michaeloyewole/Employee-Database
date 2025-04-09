import os    
import streamlit as st    
import pandas as pd    
import matplotlib.pyplot as plt    
import datetime    
import base64    
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
  
def get_employee_display_name(employee_id):    
    if employee_id is None or pd.isna(employee_id):    
        return "N/A"    
    employee = st.session_state.employees[st.session_state.employees['employee_id'] == employee_id]    
    if not employee.empty:    
        return f"{employee['first_name'].values[0]} {employee['last_name'].values[0]}"    
    return "Unknown"    
  
def get_employee_email(employee_id):  
    if employee_id is None or pd.isna(employee_id):  
        return None  
    employee = st.session_state.employees[st.session_state.employees['employee_id'] == employee_id]  
    if not employee.empty and 'email' in employee.columns:  
        return employee['email'].values[0]  
    return None  
  
def send_email_notification(employee_id, meeting_data):  
    employee_email = get_employee_email(employee_id)  
    if not employee_email:  
        st.warning("Could not find employee email to send notification.")  
        return False  
  
    # SMTP configuration placeholder (update with your SMTP server details)  
    smtp_server = "smtp.example.com"  
    smtp_port = 587  
    smtp_username = "your_username"  
    smtp_password = "your_password"  
    sender_email = "notifications@yourcompany.com"  
  
    # Create message  
    msg = MIMEMultipart()  
    msg['From'] = sender_email  
    msg['To'] = employee_email  
    msg['Subject'] = f"One-on-One Meeting Scheduled for {meeting_data['meeting_date']}"  
  
    # Email body  
    body = f"""  
    Dear {get_employee_display_name(employee_id)},  
  
    A one-on-one meeting has been scheduled with {get_employee_display_name(meeting_data['manager_id'])}:  
  
    Date: {meeting_data['meeting_date']}  
    Time: {meeting_data['meeting_time']}  
    Agenda: {meeting_data['Meeting Agenda']}  
  
    Please prepare for this meeting accordingly.  
  
    Regards,  
    HR Department  
    """  
    msg.attach(MIMEText(body, 'plain'))  
  
    # Placeholder for actual email sending (commented out for safety)  
    """  
    try:  
        server = smtplib.SMTP(smtp_server, smtp_port)  
        server.starttls()  
        server.login(smtp_username, smtp_password)  
        server.send_message(msg)  
        server.quit()  
        return True  
    except Exception as e:  
        st.error(f"Failed to send email notification: {str(e)}")  
        return False  
    """  
      
    # For now, just simulate success  
    st.info(f"Email notification would be sent to {employee_email}")  
    return True  
  
def add_to_calendar(employee_id, manager_id, meeting_data):  
    # Placeholder for Microsoft Calendar integration  
    st.info("Calendar integration would add this meeting to Microsoft Calendar")  
    return True  
  
# -------------------------------    
# 3. Initialize Tables in Session State    
# -------------------------------    
# 1. Employees Table    
if 'employees' not in st.session_state:    
    st.session_state.employees = load_table('employees', [    
        'employee_id', 'first_name', 'last_name', 'employee_number',    
        'department', 'job_title', 'hire_date', 'email', 'phone',    
        'address', 'date_of_birth', 'manager_id', 'employment_status'    
    ])    
  
# 2. One-on-One Meetings Table    
if 'meetings' not in st.session_state:    
    st.session_state.meetings = load_table('meetings', [    
        'meeting_id', 'employee_id', 'manager_id', 'meeting_date',    
        'meeting_time', 'Meeting Agenda', 'action_items', 'notes', 'next_meeting_date'    
    ])    
  
# 3. Disciplinary Actions Table    
if 'disciplinary' not in st.session_state:    
    st.session_state.disciplinary = load_table('disciplinary', [    
        'disciplinary_id', 'employee_id', 'd_type', 'd_date', 'description'    
    ])    
  
# 4. Performance Reviews Table    
if 'performance' not in st.session_state:    
    st.session_state.performance = load_table('performance', [    
        'review_id', 'employee_id', 'review_date', 'reviewer', 'score', 'comments'    
    ])    
  
# 5. Training Records Table    
if 'training' not in st.session_state:    
    st.session_state.training = load_table('training', [    
        'training_id', 'employee_id', 'training_date', 'course_name', 'status'    
    ])    
  
# -------------------------------    
# 4. Sidebar Navigation    
# -------------------------------    
st.sidebar.title("Employee Records Tool")    
module = st.sidebar.radio(    
    "Select Module",    
    ["Employee Management", "One-on-One Meetings", "Disciplinary Actions",    
     "Performance Reviews", "Training Records", "Reports"]    
)    
  
# -------------------------------    
# 5. Module: Employee Management    
# -------------------------------    
if module == "Employee Management":    
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
        date_of_birth = st.date_input("Date of Birth", datetime.date.today() - datetime.timedelta(days=365*25))    
        manager_id = st.text_input("Manager ID (max 6 digits)", max_chars=6)    
        employment_status = st.selectbox("Employment Status", ["Active", "Terminated", "On Leave", "Retired"])    
        submitted_employee = st.form_submit_button("Add/Update Employee")    
        if submitted_employee:    
            if employee_id == "" or not employee_id.isdigit():    
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")    
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
                    "employment_status": [employment_status],    
                })    
                st.session_state.employees = pd.concat([st.session_state.employees, new_employee], ignore_index=True)    
                st.success("Employee added/updated successfully!")    
    st.subheader("Employees Table")    
    st.dataframe(st.session_state.employees)    
    if st.button("Save Employees Data"):    
        save_table("employees", st.session_state.employees)    
  
# -------------------------------    
# 6. Module: One-on-One Meetings    
# -------------------------------    
elif module == "One-on-One Meetings":    
    st.header("One-on-One Meetings")    
    with st.form("meetings_form"):    
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
                # Email notification placeholder  
                send_email_notification(employee_id, new_meeting.to_dict(orient="records")[0])  
                # Calendar integration placeholder  
                add_to_calendar(employee_id, manager_id, new_meeting.to_dict(orient="records")[0])  
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
        col1, col2 = st.columns(2)  
        with col1:  
            disciplinary_id = st.text_input("Disciplinary ID (max 6 digits)", max_chars=6)    
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)    
            d_type = st.text_input("Type")    
        with col2:  
            d_date = st.date_input("Date", datetime.date.today())    
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
                    "d_type": [d_type],    
                    "d_date": [d_date.strftime('%Y-%m-%d')],    
                    "description": [description]    
                })    
                st.session_state.disciplinary = pd.concat([st.session_state.disciplinary, new_disc], ignore_index=True)    
                st.success("Disciplinary action recorded successfully!")    
    st.subheader("Disciplinary Actions Table")    
    st.dataframe(st.session_state.disciplinary)    
    if st.button("Save Disciplinary Data"):    
        save_table("disciplinary", st.session_state.disciplinary)    
  
# -------------------------------    
# 8. Module: Performance Reviews    
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
# 9. Module: Training Records    
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
  
# -------------------------------    
# 10. Module: Reports    
# -------------------------------    
elif module == "Reports":    
    st.header("Reports")    
    report_type = st.selectbox(    
        "Select Report Type",    
        ["Department Summary", "Performance Overview", "Training Completion", "Meeting Frequency"]    
    )    
      
    if report_type == "Department Summary":    
        if not st.session_state.employees.empty and 'department' in st.session_state.employees.columns:    
            dept_counts = st.session_state.employees['department'].value_counts()    
              
            st.subheader("Employees by Department")    
            fig, ax = plt.subplots(figsize=(10, 6))    
            dept_counts.plot(kind='bar', ax=ax)    
            ax.set_ylabel('Number of Employees')    
            ax.set_title('Employee Count by Department')    
            st.pyplot(fig)    
              
            st.subheader("Department Data")    
            st.dataframe(dept_counts.reset_index().rename(columns={'index': 'Department', 'department': 'Count'}))    
        else:    
            st.warning("No department data available. Please add employees with department information.")    
      
    elif report_type == "Performance Overview":    
        if not st.session_state.performance.empty and 'score' in st.session_state.performance.columns:    
            score_counts = st.session_state.performance['score'].value_counts().sort_index()    
              
            st.subheader("Performance Score Distribution")    
            fig, ax = plt.subplots(figsize=(10, 6))    
            score_counts.plot(kind='bar', ax=ax)    
            ax.set_xlabel('Performance Score')    
            ax.set_ylabel('Number of Reviews')    
            ax.set_title('Performance Score Distribution')    
            st.pyplot(fig)    
              
            st.subheader("Average Performance by Employee")    
            if 'employee_id' in st.session_state.performance.columns:    
                avg_performance = st.session_state.performance.groupby('employee_id')['score'].mean().reset_index()    
                avg_performance['employee_name'] = avg_performance['employee_id'].apply(get_employee_display_name)    
                avg_performance = avg_performance.sort_values('score', ascending=False)    
                st.dataframe(avg_performance.rename(columns={'score': 'Average Score'}))    
        else:    
            st.warning("No performance data available. Please add performance reviews.")    
      
    elif report_type == "Training Completion":    
        if not st.session_state.training.empty and 'status' in st.session_state.training.columns:    
            status_counts = st.session_state.training['status'].value_counts()    
              
            st.subheader("Training Status Overview")    
            fig, ax = plt.subplots(figsize=(10, 6))    
            status_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)    
            ax.set_ylabel('')    
            ax.set_title('Training Status Distribution')    
            st.pyplot(fig)    
              
            st.subheader("Training Status by Course")    
            if 'course_name' in st.session_state.training.columns:    
                course_status = pd.crosstab(st.session_state.training['course_name'], st.session_state.training['status'])    
                st.dataframe(course_status)    
        else:    
            st.warning("No training data available. Please add training records.")    
      
    elif report_type == "Meeting Frequency":    
        if not st.session_state.meetings.empty and 'meeting_date' in st.session_state.meetings.columns:    
            # Convert date strings to datetime objects    
            st.session_state.meetings['meeting_date'] = pd.to_datetime(st.session_state.meetings['meeting_date'])    
              
            # Group by month and count    
            meetings_by_month = st.session_state.meetings.groupby(st.session_state.meetings['meeting_date'].dt.to_period('M')).size()    
            meetings_by_month = meetings_by_month.reset_index()    
            meetings_by_month.columns = ['Month', 'Count']    
            meetings_by_month['Month'] = meetings_by_month['Month'].astype(str)    
              
            st.subheader("Meeting Frequency by Month")    
            fig, ax = plt.subplots(figsize=(12, 6))    
            ax.bar(meetings_by_month['Month'], meetings_by_month['Count'])    
            plt.xticks(rotation=45)    
            ax.set_xlabel('Month')    
            ax.set_ylabel('Number of Meetings')    
            ax.set_title('One-on-One Meetings by Month')    
            st.pyplot(fig)    
              
            st.subheader("Meeting Data by Month")    
            st.dataframe(meetings_by_month)    
        else:    
            st.warning("No meeting data available. Please add one-on-one meetings.")    
  
    # Export report as CSV  
    if st.button("Export Report Data"):  
        if report_type == "Department Summary" and not st.session_state.employees.empty:  
            export_data = st.session_state.employees['department'].value_counts().reset_index()  
            export_data.columns = ['Department', 'Count']  
            export_data.to_csv(os.path.join(DATA_DIR, 'department_summary_report.csv'), index=False)  
            st.success("Department Summary exported to department_summary_report.csv")  
        elif report_type == "Performance Overview" and not st.session_state.performance.empty:  
            export_data = st.session_state.performance.groupby('employee_id')['score'].mean().reset_index()  
            export_data['employee_name'] = export_data['employee_id'].apply(get_employee_display_name)  
            export_data.to_csv(os.path.join(DATA_DIR, 'performance_overview_report.csv'), index=False)  
            st.success("Performance Overview exported to performance_overview_report.csv")  
        elif report_type == "Training Completion" and not st.session_state.training.empty:  
            export_data = pd.crosstab(st.session_state.training['course_name'], st.session_state.training['status'])  
            export_data.to_csv(os.path.join(DATA_DIR, 'training_completion_report.csv'))  
            st.success("Training Completion exported to training_completion_report.csv")  
        elif report_type == "Meeting Frequency" and not st.session_state.meetings.empty:  
            st.session_state.meetings['meeting_date'] = pd.to_datetime(st.session_state.meetings['meeting_date'])  
            export_data = st.session_state.meetings.groupby(st.session_state.meetings['meeting_date'].dt.to_period('M')).size().reset_index()  
            export_data.columns = ['Month', 'Count']  
            export_data['Month'] = export_data['Month'].astype(str)  
            export_data.to_csv(os.path.join(DATA_DIR, 'meeting_frequency_report.csv'), index=False)  
            st.success("Meeting Frequency exported to meeting_frequency_report.csv")  
