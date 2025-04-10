import os  
import streamlit as st  
import pandas as pd  
import matplotlib.pyplot as plt  
import datetime  
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
# 2. CSV Download Helper Function  
# -------------------------------  
def get_csv_download_link(df, filename, label='Download CSV file'):  
    csv = df.to_csv(index=False)  
    b64 = base64.b64encode(csv.encode()).decode()  
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">{label}</a>'  
  
# -------------------------------  
# 3. Data Persistence Functions  
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
  
def get_employee_display_name(employee_id):  
    if employee_id is None or pd.isna(employee_id):  
        return "N/A"  
    employee = st.session_state.employees[st.session_state.employees['employee_id'] == employee_id]  
    if not employee.empty:  
        return f"{employee['first_name'].values[0]} {employee['last_name'].values[0]}"  
    return "Unknown"  
  
def load_from_uploaded_file(uploaded_file, columns):  
    try:  
        df = pd.read_csv(uploaded_file)  
        # Ensure all required columns exist  
        for col in columns:  
            if col not in df.columns:  
                df[col] = ""  
        return df  
    except Exception as e:  
        st.error(f"Error loading file: {e}")  
        return pd.DataFrame({col: [] for col in columns})  
  
# -------------------------------  
# 4. Initialize Session State  
# -------------------------------  
employee_columns = ["employee_id", "first_name", "last_name", "department", "job_title", "email", "phone", "employment_status"]  
meeting_columns = ["meeting_id", "employee_id", "meeting_date", "meeting_time", "Meeting Agenda", "action_items", "notes", "next_meeting_date"]  
disciplinary_columns = ["disciplinary_id", "employee_id", "type", "date", "description"]  
performance_columns = ["review_id", "employee_id", "review_date", "reviewer", "score", "comments"]  
training_columns = ["training_id", "employee_id", "course_name", "start_date", "end_date", "status", "certification"]  
  
if 'employees' not in st.session_state:  
    st.session_state.employees = load_table("employees", employee_columns)  
if 'meetings' not in st.session_state:  
    st.session_state.meetings = load_table("meetings", meeting_columns)  
if 'disciplinary' not in st.session_state:  
    st.session_state.disciplinary = load_table("disciplinary", disciplinary_columns)  
if 'performance' not in st.session_state:  
    st.session_state.performance = load_table("performance", performance_columns)  
if 'training' not in st.session_state:  
    st.session_state.training = load_table("training", training_columns)  
  
# -------------------------------  
# 5. Sidebar Navigation  
# -------------------------------  
st.sidebar.title("Employee Records Tool")  
module = st.sidebar.selectbox(  
    "Select Module",  
    ["Employee Management", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records", "Reports"]  
)  
  
# -------------------------------  
# 6. Module: Employee Management  
# -------------------------------  
if module == "Employee Management":  
    st.header("Employee Management")  
      
    # CSV Upload option  
    uploaded_employees = st.file_uploader("Upload Employees CSV", type="csv", key="employee_upload")  
    if uploaded_employees is not None:  
        st.session_state.employees = load_from_uploaded_file(uploaded_employees, employee_columns)  
        st.success("Employee data uploaded successfully!")  
      
    with st.form("employee_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            first_name = st.text_input("First Name")  
            last_name = st.text_input("Last Name")  
            department = st.text_input("Department")  
        with col2:  
            job_title = st.text_input("Job Title")  
            email = st.text_input("Email")  
            phone = st.text_input("Phone")  
            employment_status = st.selectbox("Employment Status", ["Active", "Inactive", "On Leave", "Terminated"])  
          
        submitted_employee = st.form_submit_button("Add/Update Employee")  
        if submitted_employee:  
            if employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            else:  
                new_employee = pd.DataFrame({  
                    "employee_id": [employee_id],  
                    "first_name": [first_name],  
                    "last_name": [last_name],  
                    "department": [department],  
                    "job_title": [job_title],  
                    "email": [email],  
                    "phone": [phone],  
                    "employment_status": [employment_status],  
                })  
                  
                # Check if employee already exists  
                if int(employee_id) in st.session_state.employees['employee_id'].values:  
                    st.session_state.employees = st.session_state.employees[st.session_state.employees['employee_id'] != int(employee_id)]  
                  
                st.session_state.employees = pd.concat([st.session_state.employees, new_employee], ignore_index=True)  
                st.success("Employee added/updated successfully!")  
      
    st.subheader("Employees Table")  
    st.dataframe(st.session_state.employees)  
    st.markdown(get_csv_download_link(st.session_state.employees, "employees.csv", "Download Employees CSV"), unsafe_allow_html=True)  
    if st.button("Save Employee Data"):  
        save_table("employees", st.session_state.employees)  
  
# -------------------------------  
# 7. Module: One-on-One Meetings  
# -------------------------------  
elif module == "One-on-One Meetings":  
    st.header("One-on-One Meetings")  
      
    # CSV Upload option  
    uploaded_meetings = st.file_uploader("Upload Meetings CSV", type="csv", key="meetings_upload")  
    if uploaded_meetings is not None:  
        st.session_state.meetings = load_from_uploaded_file(uploaded_meetings, meeting_columns)  
        st.success("Meetings data uploaded successfully!")  
      
    with st.form("meeting_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            meeting_id = st.text_input("Meeting ID (max 6 digits)", max_chars=6)  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            meeting_date = st.date_input("Meeting Date", datetime.date.today())  
            meeting_time = st.time_input("Meeting Time", datetime.time(9, 0))  
        with col2:  
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
            else:  
                new_meeting = pd.DataFrame({  
                    "meeting_id": [meeting_id],  
                    "employee_id": [employee_id],  
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
    st.markdown(get_csv_download_link(st.session_state.meetings, "meetings.csv", "Download Meetings CSV"), unsafe_allow_html=True)  
    if st.button("Save Meetings Data"):  
        save_table("meetings", st.session_state.meetings)  
  
# -------------------------------  
# 8. Module: Disciplinary Actions  
# -------------------------------  
elif module == "Disciplinary Actions":  
    st.header("Disciplinary Actions")  
    # Updated column structure for disciplinary actions:  
    # ["Period (Date)", "disciplinary_id", "ID", "First Name", "Last Name", "Job Title",  
    #  "Violation", "Interview Date", "Reason", "Comments", "Interviewer", "Decision"]  
      
    # CSV Upload option  
    uploaded_disciplinary = st.file_uploader("Upload Disciplinary CSV", type="csv", key="disciplinary_upload")  
    if uploaded_disciplinary is not None:  
        # When uploading, ensure the file has at least the required columns (if missing, fill with empty string)  
        required_cols = ["Period (Date)", "disciplinary_id", "ID", "First Name", "Last Name",  
                         "Job Title", "Violation", "Interview Date", "Reason", "Comments", "Interviewer", "Decision"]  
        st.session_state.disciplinary = load_from_uploaded_file(uploaded_disciplinary, required_cols)  
        st.success("Disciplinary data uploaded successfully!")  
      
    # Updated Form for Disciplinary Actions  
    with st.form("disciplinary_form"):  
        st.subheader("Record Disciplinary Action")  
          
        col1, col2, col3 = st.columns(3)  
        with col1:  
            period_date = st.date_input("Period (Date)", datetime.date.today())  
            disciplinary_id = st.text_input("Disciplinary ID (max 6 digits)", max_chars=6)  
            emp_id = st.text_input("ID (Employee ID - max 6 digits)", max_chars=6)  
            first_name = st.text_input("First Name")  
        with col2:  
            last_name = st.text_input("Last Name")  
            job_title = st.text_input("Job Title")  
            violation = st.text_input("Violation")  
            interview_date = st.date_input("Interview Date", datetime.date.today())  
        with col3:  
            reason = st.text_area("Reason")  
            comments = st.text_area("Comments")  
            interviewer = st.text_input("Interviewer")  
            decision = st.text_input("Decision")  
          
        submitted_disc = st.form_submit_button("Record Disciplinary Action")  
        if submitted_disc:  
            # Validate numeric inputs for IDs  
            if disciplinary_id == "" or not disciplinary_id.isdigit():  
                st.error("Please enter a valid numeric Disciplinary ID (up to 6 digits).")  
            elif emp_id == "" or not emp_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            else:  
                new_disc = pd.DataFrame({  
                    "Period (Date)": [period_date.strftime('%Y-%m-%d')],  
                    "disciplinary_id": [disciplinary_id],  
                    "ID": [emp_id],  
                    "First Name": [first_name],  
                    "Last Name": [last_name],  
                    "Job Title": [job_title],  
                    "Violation": [violation],  
                    "Interview Date": [interview_date.strftime('%Y-%m-%d')],  
                    "Reason": [reason],  
                    "Comments": [comments],  
                    "Interviewer": [interviewer],  
                    "Decision": [decision]  
                })  
                st.session_state.disciplinary = pd.concat([st.session_state.disciplinary, new_disc], ignore_index=True)  
                st.success("Disciplinary action recorded successfully!")  
      
    st.subheader("Disciplinary Actions Table")  
    st.dataframe(st.session_state.disciplinary)  
    st.markdown(get_csv_download_link(st.session_state.disciplinary, "disciplinary.csv", "Download Disciplinary CSV"), unsafe_allow_html=True)  
    if st.button("Save Disciplinary Data"):  
        save_table("disciplinary", st.session_state.disciplinary)  
# -------------------------------  
# 9. Module: Performance Reviews  
# -------------------------------  
elif module == "Performance Reviews":  
    st.header("Performance Reviews")  
      
    # CSV Upload option  
    uploaded_performance = st.file_uploader("Upload Performance CSV", type="csv", key="performance_upload")  
    if uploaded_performance is not None:  
        st.session_state.performance = load_from_uploaded_file(uploaded_performance, performance_columns)  
        st.success("Performance data uploaded successfully!")  
      
    with st.form("performance_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            review_id = st.text_input("Review ID (max 6 digits)", max_chars=6)  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            review_date = st.date_input("Review Date", datetime.date.today())  
        with col2:  
            reviewer = st.text_input("Reviewer")  
            score = st.slider("Score", 1, 5, 3)  
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
    st.markdown(get_csv_download_link(st.session_state.performance, "performance.csv", "Download Performance CSV"), unsafe_allow_html=True)  
    if st.button("Save Performance Data"):  
        save_table("performance", st.session_state.performance)  
  
# -------------------------------  
# 10. Module: Training Records  
# -------------------------------  
elif module == "Training Records":  
    st.header("Training Records")  
      
    # CSV Upload option  
    uploaded_training = st.file_uploader("Upload Training CSV", type="csv", key="training_upload")  
    if uploaded_training is not None:  
        st.session_state.training = load_from_uploaded_file(uploaded_training, training_columns)  
        st.success("Training data uploaded successfully!")  
      
    with st.form("training_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            training_id = st.text_input("Training ID (max 6 digits)", max_chars=6)  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            course_name = st.text_input("Course Name")  
        with col2:  
            start_date = st.date_input("Start Date", datetime.date.today())  
            end_date = st.date_input("End Date", datetime.date.today() + datetime.timedelta(days=30))  
            status = st.selectbox("Status", ["Not Started", "In Progress", "Completed", "Failed"])  
            certification = st.text_input("Certification")  
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
                    "start_date": [start_date.strftime('%Y-%m-%d')],  
                    "end_date": [end_date.strftime('%Y-%m-%d')],  
                    "status": [status],  
                    "certification": [certification]  
                })  
                st.session_state.training = pd.concat([st.session_state.training, new_training], ignore_index=True)  
                st.success("Training record added successfully!")  
      
    st.subheader("Training Records Table")  
    st.dataframe(st.session_state.training)  
    st.markdown(get_csv_download_link(st.session_state.training, "training.csv", "Download Training CSV"), unsafe_allow_html=True)  
    if st.button("Save Training Data"):  
        save_table("training", st.session_state.training)  
  
# -------------------------------  
# 11. Module: Reports  
# -------------------------------  
elif module == "Reports":
    st.header("Reports")
    
    report_type = st.selectbox(
        "Select Report Type",
        ["Employees by Department", 
         "Employees by Employment Status", 
         "Performance Scores by Employee", 
         "One-on-One Meeting Timelines", 
         "Training Completion Status", 
         "Disciplinary Actions by Type"]
    )
    
    # 1. Employees by Department
    if report_type == "Employees by Department" and not st.session_state.employees.empty:
        st.subheader("Employees by Department")
        
        # Create summary
        dept_summary = st.session_state.employees['department'].value_counts().reset_index()
        dept_summary.columns = ['Department', 'Count']
        
        # Display table
        st.dataframe(dept_summary)
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(dept_summary['Department'], dept_summary['Count'], color='skyblue')
        ax.set_xlabel('Department')
        ax.set_ylabel('Number of Employees')
        ax.set_title('Employees by Department')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
        
        # Export option
        st.markdown(get_csv_download_link(dept_summary, "employees_by_department.csv", "Download Department Summary"), unsafe_allow_html=True)
    
    # 2. Employees by Employment Status
    elif report_type == "Employees by Employment Status" and not st.session_state.employees.empty:
        st.subheader("Employees by Employment Status")
        
        # Create summary
        status_summary = st.session_state.employees['employment_status'].value_counts().reset_index()
        status_summary.columns = ['Employment Status', 'Count']
        
        # Display table
        st.dataframe(status_summary)
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(status_summary['Employment Status'], status_summary['Count'], color='lightgreen')
        ax.set_xlabel('Employment Status')
        ax.set_ylabel('Number of Employees')
        ax.set_title('Employees by Employment Status')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
        
        # Export option
        st.markdown(get_csv_download_link(status_summary, "employees_by_status.csv", "Download Status Summary"), unsafe_allow_html=True)
    
    # 3. Performance Scores by Employee
    elif report_type == "Performance Scores by Employee" and not st.session_state.reviews.empty:
        st.subheader("Performance Scores by Employee")
        
        # Merge with employee data to get names if available
        if not st.session_state.employees.empty:
            employee_names = st.session_state.employees[['employee_id', 'first_name', 'last_name']]
            performance_data = pd.merge(
                st.session_state.reviews,
                employee_names,
                on='employee_id',
                how='left'
            )
            performance_data['employee_name'] = performance_data['first_name'] + ' ' + performance_data['last_name']
        else:
            performance_data = st.session_state.reviews.copy()
            performance_data['employee_name'] = 'Employee ' + performance_data['employee_id'].astype(str)
        
        # Create summary - average score by employee
        performance_summary = performance_data.groupby('employee_id').agg({
            'score': 'mean',
            'employee_name': 'first',
            'review_date': 'count'
        }).reset_index()
        performance_summary.columns = ['Employee ID', 'Average Score', 'Employee Name', 'Number of Reviews']
        performance_summary = performance_summary.sort_values('Average Score', ascending=False)
        
        # Display table
        st.dataframe(performance_summary)
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(performance_summary['Employee Name'], performance_summary['Average Score'], color='coral')
        ax.set_xlabel('Employee')
        ax.set_ylabel('Average Performance Score')
        ax.set_title('Average Performance Scores by Employee')
        plt.xticks(rotation=45, ha='right')
        ax.set_ylim(0, 100)  # Assuming scores are out of 100
        st.pyplot(fig)
        
        # Export option
        st.markdown(get_csv_download_link(performance_summary, "performance_by_employee.csv", "Download Performance Summary"), unsafe_allow_html=True)
    
    # 4. One-on-One Meeting Timelines
    elif report_type == "One-on-One Meeting Timelines" and not st.session_state.meetings.empty:
        st.subheader("One-on-One Meeting Timelines")
        
        # Ensure meeting_date is datetime
        meetings_data = st.session_state.meetings.copy()
        meetings_data['meeting_date'] = pd.to_datetime(meetings_data['meeting_date'])
        
        # Merge with employee data to get names if available
        if not st.session_state.employees.empty:
            employee_names = st.session_state.employees[['employee_id', 'first_name', 'last_name']]
            meetings_data = pd.merge(
                meetings_data,
                employee_names,
                on='employee_id',
                how='left'
            )
            meetings_data['employee_name'] = meetings_data['first_name'] + ' ' + meetings_data['last_name']
        else:
            meetings_data['employee_name'] = 'Employee ' + meetings_data['employee_id'].astype(str)
        
        # Sort by date
        meetings_data = meetings_data.sort_values('meeting_date')
        
        # Display table with relevant columns
        timeline_view = meetings_data[['employee_name', 'meeting_date', 'meeting_time', 'meeting_agenda', 'action_items']]
        timeline_view.columns = ['Employee', 'Meeting Date', 'Meeting Time', 'Agenda', 'Action Items']
        st.dataframe(timeline_view)
        
        # Create visualization - meetings per month
        meetings_data['month'] = meetings_data['meeting_date'].dt.strftime('%Y-%m')
        meeting_counts = meetings_data.groupby('month').size().reset_index()
        meeting_counts.columns = ['Month', 'Number of Meetings']
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(meeting_counts['Month'], meeting_counts['Number of Meetings'], color='purple')
        ax.set_xlabel('Month')
        ax.set_ylabel('Number of Meetings')
        ax.set_title('One-on-One Meetings per Month')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
        
        # Export option
        st.markdown(get_csv_download_link(timeline_view, "meeting_timeline.csv", "Download Meeting Timeline"), unsafe_allow_html=True)
    
    # 5. Training Completion Status
    elif report_type == "Training Completion Status" and not st.session_state.training.empty:
        st.subheader("Training Completion Status")
        
        # Create summary by status
        training_status = st.session_state.training['status'].value_counts().reset_index()
        training_status.columns = ['Status', 'Count']
        
        # Display table
        st.dataframe(training_status)
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.pie(training_status['Count'], labels=training_status['Status'], autopct='%1.1f%%', startangle=90, colors=['lightgreen', 'orange', 'lightblue'])
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        ax.set_title('Training Completion Status')
        st.pyplot(fig)
        
        # Show detailed training records
        st.subheader("Detailed Training Records")
        
        # Merge with employee data to get names if available
        if not st.session_state.employees.empty:
            employee_names = st.session_state.employees[['employee_id', 'first_name', 'last_name']]
            training_details = pd.merge(
                st.session_state.training,
                employee_names,
                on='employee_id',
                how='left'
            )
            training_details['employee_name'] = training_details['first_name'] + ' ' + training_details['last_name']
        else:
            training_details = st.session_state.training.copy()
            training_details['employee_name'] = 'Employee ' + training_details['employee_id'].astype(str)
        
        # Display detailed view
        training_view = training_details[['employee_name', 'course_name', 'start_date', 'end_date', 'status', 'certification']]
        training_view.columns = ['Employee', 'Course', 'Start Date', 'End Date', 'Status', 'Certification']
        st.dataframe(training_view)
        
        # Export option
        st.markdown(get_csv_download_link(training_view, "training_status.csv", "Download Training Status"), unsafe_allow_html=True)
    
    # 6. Disciplinary Actions by Type
    elif report_type == "Disciplinary Actions by Type" and not st.session_state.disciplinary.empty:
        st.subheader("Disciplinary Actions by Type")
        
        # Create summary by type
        disciplinary_types = st.session_state.disciplinary['type'].value_counts().reset_index()
        disciplinary_types.columns = ['Action Type', 'Count']
        
        # Display table
        st.dataframe(disciplinary_types)
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(disciplinary_types['Action Type'], disciplinary_types['Count'], color='salmon')
        ax.set_xlabel('Action Type')
        ax.set_ylabel('Count')
        ax.set_title('Disciplinary Actions by Type')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
        
        # Show detailed records
        st.subheader("Detailed Disciplinary Records")
        
        # Merge with employee data to get names if available
        if not st.session_state.employees.empty:
            employee_names = st.session_state.employees[['employee_id', 'first_name', 'last_name']]
            disciplinary_details = pd.merge(
                st.session_state.disciplinary,
                employee_names,
                on='employee_id',
                how='left'
            )
            disciplinary_details['employee_name'] = disciplinary_details['first_name'] + ' ' + disciplinary_details['last_name']
        else:
            disciplinary_details = st.session_state.disciplinary.copy()
            disciplinary_details['employee_name'] = 'Employee ' + disciplinary_details['employee_id'].astype(str)
        
        # Display detailed view
        disciplinary_view = disciplinary_details[['employee_name', 'type', 'date', 'description']]
        disciplinary_view.columns = ['Employee', 'Action Type', 'Date', 'Description']
        st.dataframe(disciplinary_view)
        
        # Export option
        st.markdown(get_csv_download_link(disciplinary_view, "disciplinary_actions.csv", "Download Disciplinary Actions"), unsafe_allow_html=True)
    
    else:
        st.info("Please select a report type and ensure the relevant data is available.")
