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
        return df[columns]  
    except Exception as e:  
        st.error(f"Error loading file: {e}")  
        return pd.DataFrame({col: [] for col in columns})

# New function to auto-populate employee details
def auto_populate_employee_details(employee_id):
    """Auto-populate employee details when an existing ID is entered"""
    if employee_id and not pd.isna(employee_id):
        employee = st.session_state.employees[st.session_state.employees['employee_id'] == employee_id]
        if not employee.empty:
            return {
                'first_name': employee['first_name'].values[0],
                'last_name': employee['last_name'].values[0],
                'department': employee['department'].values[0],
                'position': employee['position'].values[0],
                'hire_date': employee['hire_date'].values[0]
            }
    return None

# -------------------------------  
# 4. Initialize Session State  
# -------------------------------  
if 'employees' not in st.session_state:  
    employee_columns = ['employee_id', 'first_name', 'last_name', 'department', 'position', 'hire_date']  
    st.session_state.employees = load_table('employees', employee_columns)  
  
if 'meetings' not in st.session_state:  
    meeting_columns = ['meeting_id', 'employee_id', 'meeting_date', 'meeting_type', 'notes']  
    st.session_state.meetings = load_table('meetings', meeting_columns)  
  
if 'training' not in st.session_state:  
    training_columns = ['training_id', 'employee_id', 'course_name', 'completion_date', 'status']  
    st.session_state.training = load_table('training', training_columns)  
  
# -------------------------------  
# 5. Sidebar Navigation - CHANGED TO LIST MODULES INSTEAD OF DROPDOWN
# -------------------------------  
st.sidebar.title("Employee Records Tool")

# Modules listed directly in sidebar instead of dropdown
st.sidebar.header("Modules")

# Employee Management Module
if st.sidebar.button("Employee Management", use_container_width=True):
    st.session_state.current_module = "Employee Management"

# Meeting Records Module
if st.sidebar.button("Meeting Records", use_container_width=True):
    st.session_state.current_module = "Meeting Records"

# Training Completion Module
if st.sidebar.button("Training Completion", use_container_width=True):
    st.session_state.current_module = "Training Completion"

# Reports Module
if st.sidebar.button("Reports", use_container_width=True):
    st.session_state.current_module = "Reports"

# Initialize current module if not set
if 'current_module' not in st.session_state:
    st.session_state.current_module = "Employee Management"

# Display current module
st.sidebar.markdown(f"**Current Module:** {st.session_state.current_module}")

# Data Import/Export Section
st.sidebar.header("Data Import/Export")

# File uploader for each table
table_to_import = st.sidebar.selectbox("Select table to import", ["employees", "meetings", "training"])
uploaded_file = st.sidebar.file_uploader(f"Upload {table_to_import} CSV", type=['csv'])

if uploaded_file is not None:
    if table_to_import == "employees":
        st.session_state.employees = load_from_uploaded_file(uploaded_file, st.session_state.employees.columns)
        save_table("employees", st.session_state.employees)
    elif table_to_import == "meetings":
        st.session_state.meetings = load_from_uploaded_file(uploaded_file, st.session_state.meetings.columns)
        save_table("meetings", st.session_state.meetings)
    elif table_to_import == "training":
        st.session_state.training = load_from_uploaded_file(uploaded_file, st.session_state.training.columns)
        save_table("training", st.session_state.training)

# Export data links
st.sidebar.markdown("### Export Data")
st.sidebar.markdown(get_csv_download_link(st.session_state.employees, "employees.csv", "Download Employees"), unsafe_allow_html=True)
st.sidebar.markdown(get_csv_download_link(st.session_state.meetings, "meetings.csv", "Download Meetings"), unsafe_allow_html=True)
st.sidebar.markdown(get_csv_download_link(st.session_state.training, "training.csv", "Download Training"), unsafe_allow_html=True)

# -------------------------------  
# 6. Main Content Area  
# -------------------------------  
if st.session_state.current_module == "Employee Management":
    st.title("Employee Management")
    
    # Display employee table
    st.subheader("Employee Records")
    st.dataframe(st.session_state.employees)
    
    # Form for adding/editing employees
    st.subheader("Add/Edit Employee")
    with st.form(key="employee_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            employee_id = st.text_input("Employee ID")
            
            # Auto-populate fields if employee ID exists - NEW FEATURE
            existing_details = auto_populate_employee_details(employee_id)
            
            if existing_details:
                st.info(f"Existing employee found: {get_employee_display_name(employee_id)}")
                first_name = st.text_input("First Name", value=existing_details['first_name'])
                last_name = st.text_input("Last Name", value=existing_details['last_name'])
            else:
                first_name = st.text_input("First Name")
                last_name = st.text_input("Last Name")
        
        with col2:
            if existing_details:
                department = st.text_input("Department", value=existing_details['department'])
                position = st.text_input("Position", value=existing_details['position'])
                hire_date = st.text_input("Hire Date", value=existing_details['hire_date'])
            else:
                department = st.text_input("Department")
                position = st.text_input("Position")
                hire_date = st.text_input("Hire Date", placeholder="YYYY-MM-DD")
        
        submit_button = st.form_submit_button("Save Employee")
    
    if submit_button:
        # Check if we're updating an existing employee
        if employee_id in st.session_state.employees['employee_id'].values:
            # Update existing employee
            idx = st.session_state.employees.index[st.session_state.employees['employee_id'] == employee_id].tolist()[0]
            st.session_state.employees.at[idx, 'first_name'] = first_name
            st.session_state.employees.at[idx, 'last_name'] = last_name
            st.session_state.employees.at[idx, 'department'] = department
            st.session_state.employees.at[idx, 'position'] = position
            st.session_state.employees.at[idx, 'hire_date'] = hire_date
            st.success(f"Updated employee: {first_name} {last_name}")
        else:
            # Add new employee
            new_employee = pd.DataFrame({
                'employee_id': [employee_id],
                'first_name': [first_name],
                'last_name': [last_name],
                'department': [department],
                'position': [position],
                'hire_date': [hire_date]
            })
            st.session_state.employees = pd.concat([st.session_state.employees, new_employee], ignore_index=True)
            st.success(f"Added new employee: {first_name} {last_name}")
        
        save_table("employees", st.session_state.employees)

elif st.session_state.current_module == "Meeting Records":
    st.title("Meeting Records")
    
    # Display meeting records
    st.subheader("Meeting Records")
    
    # Add employee names to meetings for display
    if not st.session_state.meetings.empty:
        meetings_display = st.session_state.meetings.copy()
        meetings_display['employee_name'] = meetings_display['employee_id'].apply(get_employee_display_name)
        st.dataframe(meetings_display)
    else:
        st.dataframe(st.session_state.meetings)
    
    # Form for adding meeting records
    st.subheader("Add Meeting Record")
    with st.form(key="meeting_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            meeting_id = st.text_input("Meeting ID")
            employee_options = [""] + st.session_state.employees['employee_id'].tolist()
            employee_id = st.selectbox("Employee", employee_options)
            meeting_date = st.date_input("Meeting Date")
        
        with col2:
            meeting_type = st.selectbox("Meeting Type", ["", "One-on-One", "Performance Review", "Project Discussion", "Other"])
            notes = st.text_area("Notes")
        
        submit_button = st.form_submit_button("Save Meeting")
    
    if submit_button:
        new_meeting = pd.DataFrame({
            'meeting_id': [meeting_id],
            'employee_id': [employee_id],
            'meeting_date': [meeting_date.strftime("%Y-%m-%d")],
            'meeting_type': [meeting_type],
            'notes': [notes]
        })
        st.session_state.meetings = pd.concat([st.session_state.meetings, new_meeting], ignore_index=True)
        save_table("meetings", st.session_state.meetings)
        st.success("Meeting record added successfully!")

elif st.session_state.current_module == "Training Completion":
    st.title("Training Completion")
    
    # Display training records
    st.subheader("Training Records")
    
    # Add employee names to training for display
    if not st.session_state.training.empty:
        training_display = st.session_state.training.copy()
        training_display['employee_name'] = training_display['employee_id'].apply(get_employee_display_name)
        st.dataframe(training_display)
    else:
        st.dataframe(st.session_state.training)
    
    # Form for adding training records
    st.subheader("Add Training Record")
    with st.form(key="training_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            training_id = st.text_input("Training ID")
            employee_options = [""] + st.session_state.employees['employee_id'].tolist()
            employee_id = st.selectbox("Employee", employee_options)
            course_name = st.text_input("Course Name")
        
        with col2:
            completion_date = st.date_input("Completion Date")
            status = st.selectbox("Status", ["", "Completed", "In Progress", "Not Started"])
        
        submit_button = st.form_submit_button("Save Training")
    
    if submit_button:
        new_training = pd.DataFrame({
            'training_id': [training_id],
            'employee_id': [employee_id],
            'course_name': [course_name],
            'completion_date': [completion_date.strftime("%Y-%m-%d")],
            'status': [status]
        })
        st.session_state.training = pd.concat([st.session_state.training, new_training], ignore_index=True)
        save_table("training", st.session_state.training)
        st.success("Training record added successfully!")

elif st.session_state.current_module == "Reports":
    st.title("Reports")
    
    report_type = st.selectbox("Select Report Type", ["", "Department Distribution", "Training Completion", "Meeting Frequency"])
    
    if report_type == "Department Distribution" and not st.session_state.employees.empty:
        st.subheader("Department Distribution")
        
        dept_counts = st.session_state.employees['department'].value_counts().reset_index()
        dept_counts.columns = ['Department', 'Count']
        
        st.dataframe(dept_counts)
        
        # Plot
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(dept_counts['Department'], dept_counts['Count'], color='skyblue')
        ax.set_xlabel('Department')
        ax.set_ylabel('Number of Employees')
        ax.set_title('Employee Distribution by Department')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
        
        # Export option
        st.markdown(get_csv_download_link(dept_counts, "department_distribution.csv", "Download Department Distribution"), unsafe_allow_html=True)
        
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
        st.markdown(get_csv_download_link(training_status.reset_index(), "training_completion.csv", "Download Training Completion"), unsafe_allow_html=True)  
          
    elif report_type == "Meeting Frequency" and not st.session_state.meetings.empty:  
        st.subheader("Meeting Frequency")  
          
        # Convert meeting_date to datetime if it's not already  
        if st.session_state.meetings['meeting_date'].dtype == 'object':  
            st.session_state.meetings['meeting_date'] = pd.to_datetime(st.session_state.meetings['meeting_date'])  
          
        # Group by month and count  
        meeting_freq = st.session_state.meetings.groupby(pd.Grouper(key='meeting_date', freq='M')).size().reset_index()  
        meeting_freq.columns = ['Month', 'Count']  
        meeting_freq['Month'] = meeting_freq['Month'].dt.strftime('%Y-%m')  
          
        st.dataframe(meeting_freq)  
          
        # Plot  
        fig, ax = plt.subplots(figsize=(10, 6))  
        ax.bar(meeting_freq['Month'], meeting_freq['Count'], color='coral')  
        ax.set_xlabel('Month')  
        ax.set_ylabel('Number of Meetings')  
        ax.set_title('Meeting Frequency by Month')  
        plt.xticks(rotation=45, ha='right')  
        st.pyplot(fig)  
          
        # Export option  
        st.markdown(get_csv_download_link(meeting_freq, "meeting_frequency.csv", "Download Meeting Frequency"), unsafe_allow_html=True)
