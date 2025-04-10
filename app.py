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
  def employees_page():  
    st.title("Employees")  
      
    # Initialize session state for employees if not exists  
    if 'employees' not in st.session_state:  
        st.session_state.employees = load_table('employees', employee_columns)  
      
    # Create tabs for Add/Edit and View  
    tab1, tab2 = st.tabs(["Add/Edit Employee", "View Employees"])  
      
    with tab1:  
        # File uploader for bulk import  
        uploaded_employees = st.file_uploader("Upload Employee CSV", type=['csv'])  
        if uploaded_employees is not None:  
            st.session_state.employees = load_from_uploaded_file(uploaded_employees, employee_columns)  
            st.success("Employee data uploaded successfully!")  
          
        # Employee ID lookup for editing  
        st.subheader("Edit Existing Employee")  
        edit_employee_id = st.text_input("Enter Employee ID to Edit", key="edit_employee_id")  
          
        # Initialize form values  
        employee_data = {col: "" for col in employee_columns}  
        is_edit_mode = False  
          
        # If employee ID is provided, look up the employee data  
        if edit_employee_id:  
            employee_df = st.session_state.employees  
            matching_employee = employee_df[employee_df['employee_id'] == edit_employee_id]  
              
            if not matching_employee.empty:  
                # Populate form with existing data  
                for col in employee_columns:  
                    employee_data[col] = matching_employee[col].values[0]  
                is_edit_mode = True  
                st.success(f"Found employee: {employee_data['first_name']} {employee_data['last_name']}")  
            else:  
                st.warning(f"No employee found with ID: {edit_employee_id}")  
          
        # Employee form  
        st.subheader("Employee Information")  
        with st.form("employee_form"):  
            col1, col2 = st.columns(2)  
              
            with col1:  
                # If in edit mode, display the ID as read-only  
                if is_edit_mode:  
                    st.text_input("Employee ID", value=employee_data['employee_id'], disabled=True)  
                    employee_id = employee_data['employee_id']  # Keep the original ID  
                else:  
                    employee_id = st.text_input("Employee ID (max 6 digits)",   
                                               value=employee_data['employee_id'],   
                                               max_chars=6)  
                  
                first_name = st.text_input("First Name", value=employee_data['first_name'])  
                last_name = st.text_input("Last Name", value=employee_data['last_name'])  
                department = st.text_input("Department", value=employee_data['department'])  
              
            with col2:  
                job_title = st.text_input("Job Title", value=employee_data['job_title'])  
                email = st.text_input("Email", value=employee_data['email'])  
                phone = st.text_input("Phone", value=employee_data['phone'])  
                employment_status = st.selectbox(  
                    "Employment Status",  
                    options=["Full-time", "Part-time", "Contract", "Terminated"],  
                    index=["Full-time", "Part-time", "Contract", "Terminated"].index(employee_data['employment_status'])   
                    if employee_data['employment_status'] in ["Full-time", "Part-time", "Contract", "Terminated"] else 0  
                )  
              
            submit_button = st.form_submit_button("Save Employee")  
              
            if submit_button:  
                if not employee_id or not first_name or not last_name:  
                    st.error("Employee ID, First Name, and Last Name are required!")  
                else:  
                    # Create new employee record  
                    new_employee = {  
                        'employee_id': employee_id,  
                        'first_name': first_name,  
                        'last_name': last_name,  
                        'department': department,  
                        'job_title': job_title,  
                        'email': email,  
                        'phone': phone,  
                        'employment_status': employment_status  
                    }  
                      
                    # If editing, update the existing record  
                    if is_edit_mode:  
                        # Remove the old record  
                        st.session_state.employees = st.session_state.employees[  
                            st.session_state.employees['employee_id'] != employee_id  
                        ]  
                        # Add the updated record  
                        st.session_state.employees = pd.concat([  
                            st.session_state.employees,   
                            pd.DataFrame([new_employee])  
                        ], ignore_index=True)  
                        st.success(f"Employee {employee_id} updated successfully!")  
                    else:  
                        # Check if employee ID already exists  
                        if employee_id in st.session_state.employees['employee_id'].values:  
                            st.error(f"Employee ID {employee_id} already exists!")  
                        else:  
                            # Add new employee  
                            st.session_state.employees = pd.concat([  
                                st.session_state.employees,   
                                pd.DataFrame([new_employee])  
                            ], ignore_index=True)  
                            st.success("New employee added successfully!")  
                      
                    # Save to CSV  
                    save_table('employees', st.session_state.employees)  
                      
                    # Clear the form after successful submission  
                    st.experimental_rerun()  
      
    with tab2:  
        # View and filter employees  
        st.subheader("Employee Records")  
          
        # Filter options  
        col1, col2 = st.columns(2)  
        with col1:  
            filter_dept = st.multiselect(  
                "Filter by Department",  
                options=sorted(st.session_state.employees['department'].unique()),  
                default=[]  
            )  
          
        with col2:  
            filter_status = st.multiselect(  
                "Filter by Employment Status",  
                options=sorted(st.session_state.employees['employment_status'].unique()),  
                default=[]  
            )  
          
        # Apply filters  
        filtered_df = st.session_state.employees  
        if filter_dept:  
            filtered_df = filtered_df[filtered_df['department'].isin(filter_dept)]  
        if filter_status:  
            filtered_df = filtered_df[filtered_df['employment_status'].isin(filter_status)]  
          
        # Display filtered dataframe  
        st.dataframe(filtered_df)  
          
        # Download option  
        st.markdown(  
            get_csv_download_link(filtered_df, "employees.csv", "Download Filtered Employee Data"),  
            unsafe_allow_html=True  
        )  
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
    # ["Period (Date)", "disciplinary_id", "ID", "Job Title",  
    #  "Violation", "Interview Date", "Reason", "Comments", "Interviewer", "Decision"]  
      
    # CSV Upload option  
    uploaded_disciplinary = st.file_uploader("Upload Disciplinary CSV", type="csv", key="disciplinary_upload")  
    if uploaded_disciplinary is not None:  
        # When uploading, ensure the file has at least the required columns (if missing, fill with empty string)  
        required_cols = ["Period (Date)", "disciplinary_id", "ID",  
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
        with col2:  
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
st.sidebar.subheader("Filter Period")  
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2025-03-16"))  
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2025-03-15"))  
  
if start_date > end_date:  
    st.sidebar.error("Error: Start date must be before or equal to End date.")  
  
# Report Type Selection  
report_options = [  
    "Employees by Employment Status",  
    "Disciplinary Actions by Violations",  
    "Disciplinary Actions per Employee",  
    "Training per Employee",  
    "Training Completion",  
    "Performance per Employee",  
    "Meeting Frequency"  # Example of a time-based report  
]  
  
report_type = st.selectbox("Select Report Type", report_options)  
  
# Each report below uses the date filter if the underlying data is time-based.  
# Ensure your data contains a date column if needed (e.g. meeting_date, completion_date)  
  
if report_type == "Employees by Employment Status":  
    st.subheader("Employees by Employment Status")  
    # Assuming st.session_state.employees exists with column 'employment_status'  
    emp_status = st.session_state.employees['employment_status'].value_counts().reset_index()  
    emp_status.columns = ['Employment Status', 'Count']  
      
    st.dataframe(emp_status)  
      
    fig, ax = plt.subplots(figsize=(12, 8))  
    ax.bar(emp_status['Employment Status'], emp_status['Count'], color='#2563EB')  
    ax.set_xlabel("Employment Status", labelpad=10)  
    ax.set_ylabel("Count", labelpad=10)  
    ax.set_title("Employees by Employment Status", pad=15)  
    ax.set_axisbelow(True)  
    plt.xticks(rotation=45, ha='right')  
    plt.tight_layout()  
    st.pyplot(fig)  
      
    st.markdown(get_csv_download_link(emp_status, "employees_by_employment_status.csv", "Download Employees by Employment Status"), unsafe_allow_html=True)  
  
elif report_type == "Disciplinary Actions by Violations":  
    st.subheader("Disciplinary Actions by Violations")  
    # Assuming st.session_state.disciplinary exists with column 'violation'  
    disciplinary_violations = st.session_state.disciplinary['violation'].value_counts().reset_index()  
    disciplinary_violations.columns = ['Violation', 'Count']  
      
    st.dataframe(disciplinary_violations)  
      
    fig, ax = plt.subplots(figsize=(12, 8))  
    ax.bar(disciplinary_violations['Violation'], disciplinary_violations['Count'], color='#24EB84')  
    ax.set_xlabel("Violation", labelpad=10)  
    ax.set_ylabel("Count", labelpad=10)  
    ax.set_title("Disciplinary Actions by Violations", pad=15)  
    ax.set_axisbelow(True)  
    plt.xticks(rotation=45, ha='right')  
    plt.tight_layout()  
    st.pyplot(fig)  
      
    st.markdown(get_csv_download_link(disciplinary_violations, "disciplinary_by_violations.csv", "Download Disciplinary Actions by Violations"), unsafe_allow_html=True)  
  
elif report_type == "Disciplinary Actions per Employee":  
    st.subheader("Disciplinary Actions per Employee")  
    # Assuming st.session_state.disciplinary exists with column 'employee_id'  
    disp_per_emp = st.session_state.disciplinary.groupby('employee_id').size().reset_index(name='Count')  
    # Helper method to get employee names  
    disp_per_emp['Employee Name'] = disp_per_emp['employee_id'].apply(lambda x: get_employee_display_name(x))  
      
    st.dataframe(disp_per_emp[['Employee Name', 'Count']])  
      
    fig, ax = plt.subplots(figsize=(12, 8))  
    ax.bar(disp_per_emp['Employee Name'], disp_per_emp['Count'], color='#B2EB24')  
    ax.set_xlabel("Employee", labelpad=10)  
    ax.set_ylabel("Disciplinary Actions Count", labelpad=10)  
    ax.set_title("Disciplinary Actions per Employee", pad=15)  
    ax.set_axisbelow(True)  
    plt.xticks(rotation=45, ha='right')  
    plt.tight_layout()  
    st.pyplot(fig)  
      
    st.markdown(get_csv_download_link(disp_per_emp, "disciplinary_per_employee.csv", "Download Disciplinary Actions per Employee"), unsafe_allow_html=True)  
  
elif report_type == "Training per Employee":  
    st.subheader("Training per Employee")  
    # Assuming st.session_state.training exists with a 'completion_date' column (if applicable) and 'employee_id'  
    training_df = st.session_state.training.copy()  
      
    # If your training data has a date column (e.g. 'completion_date'), then you can filter by date:  
    if 'completion_date' in training_df.columns:  
        training_df['completion_date'] = pd.to_datetime(training_df['completion_date'], errors='coerce')  
        date_mask = (training_df['completion_date'] >= pd.to_datetime(start_date)) & (training_df['completion_date'] <= pd.to_datetime(end_date))  
        training_df = training_df.loc[date_mask]  
      
    training_per_emp = training_df.groupby('employee_id').size().reset_index(name='Count')  
    training_per_emp['Employee Name'] = training_per_emp['employee_id'].apply(lambda x: get_employee_display_name(x))  
      
    st.dataframe(training_per_emp[['Employee Name', 'Count']])  
      
    fig, ax = plt.subplots(figsize=(12, 8))  
    ax.bar(training_per_emp['Employee Name'], training_per_emp['Count'], color='#D324EB')  
    ax.set_xlabel("Employee", labelpad=10)  
    ax.set_ylabel("Training Sessions Count", labelpad=10)  
    ax.set_title("Training per Employee", pad=15)  
    ax.set_axisbelow(True)  
    plt.xticks(rotation=45, ha='right')  
    plt.tight_layout()  
    st.pyplot(fig)  
      
    st.markdown(get_csv_download_link(training_per_emp, "training_per_employee.csv", "Download Training per Employee"), unsafe_allow_html=True)  
  
elif report_type == "Training Completion":  
    st.subheader("Training Completion")  
    # Assuming st.session_state.training has 'course_name' and 'status' columns  
    training_status = pd.crosstab(st.session_state.training['course_name'], st.session_state.training['status'])  
      
    st.dataframe(training_status)  
      
    fig, ax = plt.subplots(figsize=(12, 8))  
    training_status.plot(kind='bar', stacked=True, ax=ax)  
    ax.set_xlabel('Course', labelpad=10)  
    ax.set_ylabel('Count', labelpad=10)  
    ax.set_title('Training Status by Course', pad=15)  
    ax.set_axisbelow(True)  
    plt.xticks(rotation=45, ha='right')  
    plt.tight_layout()  
    st.pyplot(fig)  
      
    st.markdown(get_csv_download_link(training_status.reset_index(), "training_completion.csv", "Download Training Completion"), unsafe_allow_html=True)  
  
elif report_type == "Performance per Employee":  
    st.subheader("Performance per Employee")  
    # Assuming st.session_state.performance exists with columns 'employee_id' and 'performance_rating'  
    perf_per_emp = st.session_state.performance.groupby('employee_id')['performance_rating'].mean().reset_index()  
    perf_per_emp['Employee Name'] = perf_per_emp['employee_id'].apply(lambda x: get_employee_display_name(x))  
      
    st.dataframe(perf_per_emp[['Employee Name', 'performance_rating']])  
      
    fig, ax = plt.subplots(figsize=(12, 8))  
    ax.bar(perf_per_emp['Employee Name'], perf_per_emp['performance_rating'], color='#EB3424')  
    ax.set_xlabel("Employee", labelpad=10)  
    ax.set_ylabel("Average Performance Rating", labelpad=10)  
    ax.set_title("Performance per Employee", pad=15)  
    ax.set_axisbelow(True)  
    plt.xticks(rotation=45, ha='right')  
    plt.tight_layout()  
    st.pyplot(fig)  
      
    st.markdown(get_csv_download_link(perf_per_emp, "performance_per_employee.csv", "Download Performance per Employee"), unsafe_allow_html=True)  
  
elif report_type == "Meeting Frequency":  
    st.subheader("Meeting Frequency")  
    # Assuming st.session_state.meetings exists and has a 'meeting_date' column  
    meetings_df = st.session_state.meetings.copy()  
    if meetings_df['meeting_date'].dtype == 'object':  
        meetings_df['meeting_date'] = pd.to_datetime(meetings_df['meeting_date'], errors='coerce')  
      
    # Filter meetings by selected date range  
    date_mask = (meetings_df['meeting_date'] >= pd.to_datetime(start_date)) & (meetings_df['meeting_date'] <= pd.to_datetime(end_date))  
    meetings_df = meetings_df.loc[date_mask]  
      
    # Group by month (or appropriate period)  
    meeting_freq = meetings_df.groupby(pd.Grouper(key='meeting_date', freq='M')).size().reset_index(name='Count')  
    meeting_freq['Month'] = meeting_freq['meeting_date'].dt.strftime('%Y-%m')  
      
    st.dataframe(meeting_freq)  
      
    fig, ax = plt.subplots(figsize=(12, 8))  
    ax.bar(meeting_freq['Month'], meeting_freq['Count'], color='coral')  
    ax.set_xlabel("Month", labelpad=10)  
    ax.set_ylabel("Number of Meetings", labelpad=10)  
    ax.set_title("Meeting Frequency by Month", pad=15)  
    ax.set_axisbelow(True)  
    plt.xticks(rotation=45, ha='right')  
    plt.tight_layout()  
    st.pyplot(fig)  
      
    st.markdown(get_csv_download_link(meeting_freq, "meeting_frequency.csv", "Download Meeting Frequency"), unsafe_allow_html=True)  
  
else:  
    st.info("No data available for the selected report or the report type is not implemented.")  
      
print('Reports module updated with date filtering and all report options.')  
