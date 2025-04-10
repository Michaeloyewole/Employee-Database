import os    
import streamlit as st    
import pandas as pd    
import matplotlib.pyplot as plt    
import datetime    
import base64    
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
def load_table(table_name, columns, encoding="latin1"):    
    path = os.path.join(DATA_DIR, f'{table_name}.csv')    
    try:  
        if os.path.exists(path):  
            return pd.read_csv(path, encoding=encoding)  
        else:  
            # Create an empty DataFrame with the specified columns  
            df = pd.DataFrame({col: [] for col in columns})  
            # Save the empty DataFrame to create the file  
            df.to_csv(path, index=False)  
            return df  
    except Exception as e:  
        st.warning(f"Note: Starting with a new {table_name} file.")  
        df = pd.DataFrame({col: [] for col in columns})  
        df.to_csv(path, index=False)  
        return df  
  
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
    sender_email = "hr@yourcompany.com"  
      
    # Create message  
    msg = MIMEMultipart()  
    msg['From'] = sender_email  
    msg['To'] = employee_email  
    msg['Subject'] = f"One-on-One Meeting Scheduled for {meeting_data['meeting_date']}"  
      
    body = f"""  
    Dear {get_employee_display_name(employee_id)},  
      
    A one-on-one meeting has been scheduled for you on {meeting_data['meeting_date']} at {meeting_data['meeting_time']}.  
      
    Agenda: {meeting_data['Meeting Agenda']}  
      
    Action Items: {meeting_data['action_items']}  
      
    Please be prepared to discuss these items.  
      
    Regards,  
    HR Department  
    """  
      
    msg.attach(MIMEText(body, 'plain'))  
      
    # Placeholder for actual email sending (commented out to avoid errors)  
    # try:  
    #     server = smtplib.SMTP(smtp_server, smtp_port)  
    #     server.starttls()  
    #     server.login(smtp_username, smtp_password)  
    #     server.send_message(msg)  
    #     server.quit()  
    #     st.success("Email notification sent successfully!")  
    #     return True  
    # except Exception as e:  
    #     st.error(f"Failed to send email notification: {str(e)}")  
    #     return False  
      
    # For demo purposes, just show success  
    st.success("Email notification would be sent in production environment.")  
    return True  
  
def add_to_calendar(employee_id, meeting_data):  
    # Placeholder for Microsoft Calendar integration  
    # This would typically use Microsoft Graph API or similar  
    st.success("Meeting added to calendar (placeholder).")  
    return True  
  
# -------------------------------  
# 3. CSV Export Function  
# -------------------------------  
def get_csv_download_link(df, filename, link_text="Download CSV"):  
    csv = df.to_csv(index=False)  
    b64 = base64.b64encode(csv.encode()).decode()  
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'  
    return href  
  
# -------------------------------  
# 4. CSV Upload Function  
# -------------------------------  
def upload_and_process_csv(table_name, required_columns):  
    uploaded_file = st.file_uploader(f"Upload {table_name.capitalize()} CSV", type=["csv"])  
    if uploaded_file is not None:  
        try:  
            df = pd.read_csv(uploaded_file)  
              
            # Check if required columns exist  
            missing_cols = [col for col in required_columns if col not in df.columns]  
            if missing_cols:  
                st.error(f"Missing required columns: {', '.join(missing_cols)}")  
                st.info(f"Required columns are: {', '.join(required_columns)}")  
                return None  
              
            st.success(f"{table_name.capitalize()} data uploaded successfully!")  
            return df  
        except Exception as e:  
            st.error(f"Error uploading file: {str(e)}")  
            return None  
    return None  
  
# -------------------------------  
# 5. Initialize Session State  
# -------------------------------  
if 'employees' not in st.session_state:  
    st.session_state.employees = load_table('employees', ['employee_id', 'first_name', 'last_name', 'department', 'job_title', 'hire_date', 'email', 'phone', 'address', 'date_of_birth', 'manager_id', 'employment_status'])  
  
if 'meetings' not in st.session_state:  
    st.session_state.meetings = load_table('meetings', ['meeting_id', 'employee_id', 'manager_id', 'meeting_date', 'meeting_time', 'Meeting Agenda', 'action_items', 'notes', 'next_meeting_date'])  
  
if 'disciplinary' not in st.session_state:  
    st.session_state.disciplinary = load_table('disciplinary', ['disciplinary_id', 'employee_id', 'type', 'date', 'description'])  
  
if 'performance' not in st.session_state:  
    st.session_state.performance = load_table('performance', ['review_id', 'employee_id', 'reviewer_id', 'review_date', 'period_start', 'period_end', 'score', 'strengths', 'areas_for_improvement', 'goals', 'comments'])  
  
if 'training' not in st.session_state:  
    st.session_state.training = load_table('training', ['training_id', 'employee_id', 'course_name', 'provider', 'start_date', 'end_date', 'status', 'certification', 'expiry_date', 'comments'])  
  
# -------------------------------  
# 6. Sidebar Navigation  
# -------------------------------  
st.sidebar.title("Employee Records Tool")  
module = st.sidebar.radio("Navigation", ["Employee Management", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records", "Reports"])  
  
# -------------------------------  
# 7. Module: Employee Management  
# -------------------------------  
if module == "Employee Management":  
    st.header("Employee Management")  
      
    # Add CSV upload option  
    st.subheader("Upload Employee Data")  
    uploaded_employees = upload_and_process_csv('employees', ['employee_id', 'first_name', 'last_name'])  
    if uploaded_employees is not None:  
        if st.button("Replace existing employee data"):  
            st.session_state.employees = uploaded_employees  
            save_table('employees', st.session_state.employees)  
        elif st.button("Append to existing employee data"):  
            st.session_state.employees = pd.concat([st.session_state.employees, uploaded_employees], ignore_index=True)  
            save_table('employees', st.session_state.employees)  
      
    st.subheader("Add/Edit Employee")  
    with st.form("employee_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            first_name = st.text_input("First Name")  
            last_name = st.text_input("Last Name")  
            department = st.text_input("Department")  
            job_title = st.text_input("Job Title")  
            hire_date = st.date_input("Hire Date", datetime.date.today())  
        with col2:  
            email = st.text_input("Email")  
            phone = st.text_input("Phone")  
            address = st.text_area("Address")  
            date_of_birth = st.date_input("Date of Birth", datetime.date.today())  
            manager_id = st.text_input("Manager ID (max 6 digits)", max_chars=6)  
            employment_status = st.selectbox("Employment Status", ["Active", "On Leave", "Terminated"])  
          
        submitted_employee = st.form_submit_button("Add/Update Employee")  
        if submitted_employee:  
            if employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            else:  
                # Check if employee exists  
                existing_employee = st.session_state.employees[st.session_state.employees['employee_id'] == employee_id]  
                if not existing_employee.empty:  
                    # Update existing employee  
                    st.session_state.employees.loc[st.session_state.employees['employee_id'] == employee_id, 'first_name'] = first_name  
                    st.session_state.employees.loc[st.session_state.employees['employee_id'] == employee_id, 'last_name'] = last_name  
                    st.session_state.employees.loc[st.session_state.employees['employee_id'] == employee_id, 'department'] = department  
                    st.session_state.employees.loc[st.session_state.employees['employee_id'] == employee_id, 'job_title'] = job_title  
                    st.session_state.employees.loc[st.session_state.employees['employee_id'] == employee_id, 'hire_date'] = hire_date.strftime('%Y-%m-%d')  
                    st.session_state.employees.loc[st.session_state.employees['employee_id'] == employee_id, 'email'] = email  
                    st.session_state.employees.loc[st.session_state.employees['employee_id'] == employee_id, 'phone'] = phone  
                    st.session_state.employees.loc[st.session_state.employees['employee_id'] == employee_id, 'address'] = address  
                    st.session_state.employees.loc[st.session_state.employees['employee_id'] == employee_id, 'date_of_birth'] = date_of_birth.strftime('%Y-%m-%d')  
                    st.session_state.employees.loc[st.session_state.employees['employee_id'] == employee_id, 'manager_id'] = manager_id  
                    st.session_state.employees.loc[st.session_state.employees['employee_id'] == employee_id, 'employment_status'] = employment_status  
                    st.success("Employee updated successfully!")  
                else:  
                    # Add new employee  
                    new_employee = pd.DataFrame({  
                        "employee_id": [employee_id],  
                        "first_name": [first_name],  
                        "last_name": [last_name],  
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
                    st.success("Employee added successfully!")  
      
    st.subheader("Employees Table")  
    st.dataframe(st.session_state.employees)  
      
    # Add CSV export option  
    if not st.session_state.employees.empty:  
        st.markdown(get_csv_download_link(st.session_state.employees, "employees.csv"), unsafe_allow_html=True)  
      
    if st.button("Save Employees Data"):  
        save_table("employees", st.session_state.employees)  
  
# -------------------------------  
# 8. Module: One-on-One Meetings  
# -------------------------------  
elif module == "One-on-One Meetings":  
    st.header("One-on-One Meetings")  
      
    # Add CSV upload option  
    st.subheader("Upload Meetings Data")  
    uploaded_meetings = upload_and_process_csv('meetings', ['meeting_id', 'employee_id', 'manager_id'])  
    if uploaded_meetings is not None:  
        if st.button("Replace existing meetings data"):  
            st.session_state.meetings = uploaded_meetings  
            save_table('meetings', st.session_state.meetings)  
        elif st.button("Append to existing meetings data"):  
            st.session_state.meetings = pd.concat([st.session_state.meetings, uploaded_meetings], ignore_index=True)  
            save_table('meetings', st.session_state.meetings)  
      
    st.subheader("Record One-on-One Meeting")  
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
            next_meeting_date = st.date_input("Next Meeting Date", datetime.date.today())  
            notify = st.checkbox("Send email notification")  
            add_calendar = st.checkbox("Add to Microsoft Calendar")  
          
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
                  
                # Email notification if requested  
                if notify:  
                    send_email_notification(employee_id, new_meeting.to_dict(orient="records")[0])  
                  
                # Calendar integration if requested  
                if add_calendar:  
                    add_to_calendar(employee_id, new_meeting.to_dict(orient="records")[0])  
      
    st.subheader("Meetings Table")  
    st.dataframe(st.session_state.meetings)  
      
    # Add CSV export option  
    if not st.session_state.meetings.empty:  
        st.markdown(get_csv_download_link(st.session_state.meetings, "meetings.csv"), unsafe_allow_html=True)  
      
    if st.button("Save Meetings Data"):  
        save_table("meetings", st.session_state.meetings)  
  
# -------------------------------  
# 9. Module: Disciplinary Actions  
# -------------------------------  
elif module == "Disciplinary Actions":  
    st.header("Disciplinary Actions")  
      
    # Add CSV upload option  
    st.subheader("Upload Disciplinary Actions Data")  
    uploaded_disciplinary = upload_and_process_csv('disciplinary', ['disciplinary_id', 'employee_id'])  
    if uploaded_disciplinary is not None:  
        if st.button("Replace existing disciplinary data"):  
            st.session_state.disciplinary = uploaded_disciplinary  
            save_table('disciplinary', st.session_state.disciplinary)  
        elif st.button("Append to existing disciplinary data"):  
            st.session_state.disciplinary = pd.concat([st.session_state.disciplinary, uploaded_disciplinary], ignore_index=True)  
            save_table('disciplinary', st.session_state.disciplinary)  
      
    st.subheader("Record Disciplinary Action")  
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
                    "type": [d_type],  
                    "date": [d_date.strftime('%Y-%m-%d')],  
                    "description": [description]  
                })  
                st.session_state.disciplinary = pd.concat([st.session_state.disciplinary, new_disc], ignore_index=True)  
                st.success("Disciplinary action recorded successfully!")  
      
    st.subheader("Disciplinary Actions Table")  
    st.dataframe(st.session_state.disciplinary)  
      
    # Add CSV export option  
    if not st.session_state.disciplinary.empty:  
        st.markdown(get_csv_download_link(st.session_state.disciplinary, "disciplinary.csv"), unsafe_allow_html=True)  
      
    if st.button("Save Disciplinary Data"):  
        save_table("disciplinary", st.session_state.disciplinary)  
  
# -------------------------------  
# 10. Module: Performance Reviews  
# -------------------------------  
elif module == "Performance Reviews":  
    st.header("Performance Reviews")  
      
    # Add CSV upload option  
    st.subheader("Upload Performance Reviews Data")  
    uploaded_performance = upload_and_process_csv('performance', ['review_id', 'employee_id'])  
    if uploaded_performance is not None:  
        if st.button("Replace existing performance data"):  
            st.session_state.performance = uploaded_performance  
            save_table('performance', st.session_state.performance)  
        elif st.button("Append to existing performance data"):  
            st.session_state.performance = pd.concat([st.session_state.performance, uploaded_performance], ignore_index=True)  
            save_table('performance', st.session_state.performance)  
      
    st.subheader("Record Performance Review")  
    with st.form("performance_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            review_id = st.text_input("Review ID (max 6 digits)", max_chars=6)  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            reviewer_id = st.text_input("Reviewer ID (max 6 digits)", max_chars=6)  
            review_date = st.date_input("Review Date", datetime.date.today())  
            period_start = st.date_input("Period Start", datetime.date.today() - datetime.timedelta(days=365))  
        with col2:  
            period_end = st.date_input("Period End", datetime.date.today())  
            score = st.slider("Score", 1, 5, 3)  
            strengths = st.text_area("Strengths")  
            areas_for_improvement = st.text_area("Areas for Improvement")  
            goals = st.text_area("Goals")  
            comments = st.text_area("Comments")  
          
        submitted_review = st.form_submit_button("Record Performance Review")  
        if submitted_review:  
            if review_id == "" or not review_id.isdigit():  
                st.error("Please enter a valid numeric Review ID (up to 6 digits).")  
            elif employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            elif reviewer_id == "" or not reviewer_id.isdigit():  
                st.error("Please enter a valid numeric Reviewer ID (up to 6 digits).")  
            else:  
                new_review = pd.DataFrame({  
                    "review_id": [review_id],  
                    "employee_id": [employee_id],  
                    "reviewer_id": [reviewer_id],  
                    "review_date": [review_date.strftime('%Y-%m-%d')],  
                    "period_start": [period_start.strftime('%Y-%m-%d')],  
                    "period_end": [period_end.strftime('%Y-%m-%d')],  
                    "score": [score],  
                    "strengths": [strengths],  
                    "areas_for_improvement": [areas_for_improvement],  
                    "goals": [goals],  
                    "comments": [comments]  
                })  
                st.session_state.performance = pd.concat([st.session_state.performance, new_review], ignore_index=True)  
                st.success("Performance review recorded successfully!")  
      
    st.subheader("Performance Reviews Table")  
    st.dataframe(st.session_state.performance)  
      
    # Add CSV export option  
    if not st.session_state.performance.empty:  
        st.markdown(get_csv_download_link(st.session_state.performance, "performance.csv"), unsafe_allow_html=True)  
      
    if st.button("Save Performance Data"):  
        save_table("performance", st.session_state.performance)  
  
# -------------------------------  
# 11. Module: Training Records  
# -------------------------------  
elif module == "Training Records":  
    st.header("Training Records")  
      
    # Add CSV upload option  
    st.subheader("Upload Training Records Data")  
    uploaded_training = upload_and_process_csv('training', ['training_id', 'employee_id'])  
    if uploaded_training is not None:  
        if st.button("Replace existing training data"):  
            st.session_state.training = uploaded_training  
            save_table('training', st.session_state.training)  
        elif st.button("Append to existing training data"):  
            st.session_state.training = pd.concat([st.session_state.training, uploaded_training], ignore_index=True)  
            save_table('training', st.session_state.training)  
      
    st.subheader("Record Training")  
    with st.form("training_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            training_id = st.text_input("Training ID (max 6 digits)", max_chars=6)  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            course_name = st.text_input("Course Name")  
            provider = st.text_input("Provider")  
            start_date = st.date_input("Start Date", datetime.date.today())  
        with col2:  
            end_date = st.date_input("End Date", datetime.date.today() + datetime.timedelta(days=30))  
            status = st.selectbox("Status", ["Scheduled", "In Progress", "Completed", "Cancelled"])  
            certification = st.text_input("Certification")  
            expiry_date = st.date_input("Expiry Date", datetime.date.today() + datetime.timedelta(days=365))  
            comments = st.text_area("Comments")  
          
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
                    "course_name": [course_name],  
                    "provider": [provider],  
                    "start_date": [start_date.strftime('%Y-%m-%d')],  
                    "end_date": [end_date.strftime('%Y-%m-%d')],  
                    "status": [status],  
                    "certification": [certification],  
                    "expiry_date": [expiry_date.strftime('%Y-%m-%d')],  
                    "comments": [comments]  
                })  
                st.session_state.training = pd.concat([st.session_state.training, new_training], ignore_index=True)  
                st.success("Training record added successfully!")  
      
    st.subheader("Training Records Table")  
    st.dataframe(st.session_state.training)  
      
    # Add CSV export option  
    if not st.session_state.training.empty:  
        st.markdown(get_csv_download_link(st.session_state.training, "training.csv"), unsafe_allow_html=True)  
      
    if st.button("Save Training Data"):  
        save_table("training", st.session_state.training)  
  
# -------------------------------  
# 12. Module: Reports  
# -------------------------------  
elif module == "Reports":  
    st.header("Reports")  
      
    report_type = st.selectbox(  
        "Select Report Type",  
        ["Department Summary", "Performance Overview", "Training Completion", "Meeting Frequency"]  
    )  
      
    if report_type == "Department Summary" and not st.session_state.employees.empty:  
        st.subheader("Department Summary")  
        dept_summary = st.session_state.employees['department'].value_counts().reset_index()  
        dept_summary.columns = ['Department', 'Count']  
          
        st.dataframe(dept_summary)  
          
        # Plot  
        fig, ax = plt.subplots(figsize=(10, 6))  
        ax.bar(dept_summary['Department'], dept_summary['Count'], color='skyblue')  
        ax.set_xlabel('Department')  
        ax.set_ylabel('Number of Employees')  
        ax.set_title('Employees by Department')  
        plt.xticks(rotation=45, ha='right')  
        st.pyplot(fig)  
          
        # Export option  
        st.markdown(get_csv_download_link(dept_summary, "department_summary.csv"), unsafe_allow_html=True)  
          
    elif report_type == "Performance Overview" and not st.session_state.performance.empty:  
        st.subheader("Performance Overview")  
        perf_overview = st.session_state.performance.groupby('employee_id')['score'].mean().reset_index()  
        perf_overview['employee_name'] = perf_overview['employee_id'].apply(get_employee_display_name)  
          
        st.dataframe(perf_overview)  
          
        # Plot  
        fig, ax = plt.subplots(figsize=(10, 6))  
        ax.bar(perf_overview['employee_name'], perf_overview['score'], color='lightgreen')  
        ax.set_xlabel('Employee')  
        ax.set_ylabel('Average Performance Score')  
        ax.set_title('Average Performance by Employee')  
        plt.xticks(rotation=45, ha='right')  
        plt.ylim(0, 5)  
        st.pyplot(fig)  
          
        # Export option  
        st.markdown(get_csv_download_link(perf_overview, "performance_overview.csv"), unsafe_allow_html=True)  
          
    elif report_type == "Training Completion" and not st.session_state.training.empty:  
        st.subheader("Training Completion")  
        training_status = pd.crosstab(st.session_state.training['course_name'], st.session_state.training['status'])  
          
        st.dataframe(training_status)  
          
        # Plot  
        fig, ax = plt.subplots(figsize=(10, 6))  
        training_status.plot(kind='bar', stacked=True, ax=ax)  
        ax.set_xlabel('Course')  
        ax.set_ylabel('Count')  
        ax.set_title('Training Status by Course')  
        plt.xticks(rotation=45, ha='right')  
        plt.legend(title='Status')  
        st.pyplot(fig)  
          
        # Export option  
        st.markdown(get_csv_download_link(training_status.reset_index(), "training_completion.csv"), unsafe_allow_html=
