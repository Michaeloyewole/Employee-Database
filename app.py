import os    
import streamlit as st    
import pandas as pd    
import matplotlib.pyplot as plt    
import datetime    
import base64  
import sqlite3    
  
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
  
# Initialize SQLite database  
def init_sqlite_db():  
    """Initialize SQLite database with required tables"""  
    conn = sqlite3.connect('employee_database.db')  
    cursor = conn.cursor()  
      
    # Create the employees table  
    cursor.execute('''  
    CREATE TABLE IF NOT EXISTS employees (  
        employee_id TEXT PRIMARY KEY,  
        first_name TEXT,  
        last_name TEXT,  
        department TEXT,  
        job_title TEXT,  
        email TEXT,  
        phone TEXT,  
        employment_status TEXT  
    )  
    ''')  
      
    # Create the meetings table  
    cursor.execute('''  
    CREATE TABLE IF NOT EXISTS meetings (  
        meeting_id TEXT PRIMARY KEY,  
        employee_id TEXT,  
        meeting_date TEXT,  
        meeting_time TEXT,  
        MeetingAgenda TEXT,  
        action_items TEXT,  
        notes TEXT,  
        next_meeting_date TEXT  
    )  
    ''')  
      
    # Create the disciplinary table  
    cursor.execute('''  
    CREATE TABLE IF NOT EXISTS disciplinary (  
        disciplinary_id TEXT PRIMARY KEY,  
        employee_id TEXT,  
        type TEXT,  
        date TEXT,  
        description TEXT  
    )  
    ''')  
      
    # Create the performance table  
    cursor.execute('''  
    CREATE TABLE IF NOT EXISTS performance (  
        review_id TEXT PRIMARY KEY,  
        employee_id TEXT,  
        review_date TEXT,  
        reviewer TEXT,  
        score TEXT,  
        comments TEXT  
    )  
    ''')  
      
    # Create the training table  
    cursor.execute('''  
    CREATE TABLE IF NOT EXISTS training (  
        training_id TEXT PRIMARY KEY,  
        employee_id TEXT,  
        course_name TEXT,  
        start_date TEXT,  
        end_date TEXT,  
        status TEXT,  
        certification TEXT  
    )  
    ''')  
      
    conn.commit()  
    conn.close()  
  
# Initialize the database  
init_sqlite_db()  
    
# -------------------------------    
# 2. CSV Download Helper Function    
# -------------------------------    
def get_csv_download_link(df, filename, label='Download CSV file'):    
    csv = df.to_csv(index=False)    
    b64 = base64.b64encode(csv.encode()).decode()    
    return '<a href="data:file/csv;base64,' + b64 + '" download="' + filename + '">' + label + '</a>'    
    
# -------------------------------    
# 3. Data Persistence Functions    
# -------------------------------    
def load_table(table_name):    
    """Load a table from CSV file"""    
    file_path = os.path.join(DATA_DIR, f"{table_name}.csv")    
    if os.path.exists(file_path):    
        return pd.read_csv(file_path)    
    else:    
        # Return empty DataFrame with appropriate columns    
        if table_name == "employees":    
            return pd.DataFrame(columns=employee_columns)    
        elif table_name == "meetings":    
            return pd.DataFrame(columns=meeting_columns)    
        elif table_name == "disciplinary":    
            return pd.DataFrame(columns=disciplinary_columns)    
        elif table_name == "performance":    
            return pd.DataFrame(columns=performance_columns)    
        elif table_name == "training":    
            return pd.DataFrame(columns=training_columns)    
        else:    
            return pd.DataFrame()    
    
def save_table(table_name, df):    
    """Save a table to CSV file"""    
    if df is None or df.empty:    
        print(f"Not saving {table_name} - data is empty")    
        return    
          
    file_path = os.path.join(DATA_DIR, f"{table_name}.csv")    
    df.to_csv(file_path, index=False)    
    print(f"{table_name.capitalize()} data saved successfully!")    
    
def load_all_data():    
    """Load all data from CSV files"""    
    tables = ["employees", "meetings", "disciplinary", "performance", "training"]    
    for table_name in tables:    
        st.session_state[table_name] = load_table(table_name)    
        print(f"Loaded {table_name} data: {len(st.session_state[table_name])} records")    
    
def save_all_data():    
    """Save all data to CSV files"""    
    tables = ["employees", "meetings", "disciplinary", "performance", "training"]    
    for table_name in tables:    
        if table_name in st.session_state and not st.session_state[table_name].empty:    
            save_table(table_name, st.session_state[table_name])    
    st.success("All data saved successfully!")    
  
# SQLite Data Persistence Functions  
def load_table_from_sqlite(table_name):  
    """Load a table from SQLite database"""  
    try:  
        conn = sqlite3.connect('employee_database.db')  
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)  
        conn.close()  
        return df  
    except Exception as e:  
        print(f"Error loading {table_name} from SQLite: {str(e)}")  
        # Return empty DataFrame with appropriate columns  
        if table_name == "employees":  
            return pd.DataFrame(columns=employee_columns)  
        elif table_name == "meetings":  
            return pd.DataFrame(columns=meeting_columns)  
        elif table_name == "disciplinary":  
            return pd.DataFrame(columns=disciplinary_columns)  
        elif table_name == "performance":  
            return pd.DataFrame(columns=performance_columns)  
        elif table_name == "training":  
            return pd.DataFrame(columns=training_columns)  
        else:  
            return pd.DataFrame()  
  
def save_table_to_sqlite(table_name, df):  
    """Save a table to SQLite database"""  
    if df is None or df.empty:  
        print(f"Not saving {table_name} - data is empty")  
        return  
          
    conn = sqlite3.connect('employee_database.db')  
    df.to_sql(table_name, conn, if_exists='replace', index=False)  
    conn.close()  
    print(f"{table_name.capitalize()} data saved successfully!")  
  
def load_all_data_sqlite():  
    """Load all data from SQLite database"""  
    tables = ["employees", "meetings", "disciplinary", "performance", "training"]  
    for table_name in tables:  
        st.session_state[table_name] = load_table_from_sqlite(table_name)  
        print(f"Loaded {table_name} data: {len(st.session_state[table_name])} records")  
  
def save_all_data_sqlite():  
    """Save all data to SQLite database"""  
    tables = ["employees", "meetings", "disciplinary", "performance", "training"]  
    for table_name in tables:  
        if table_name in st.session_state and not st.session_state[table_name].empty:  
            save_table_to_sqlite(table_name, st.session_state[table_name])  
    st.success("All data saved successfully!")  
    
# -------------------------------    
# 4. Sidebar Navigation    
# -------------------------------    
st.sidebar.title("Navigation")    
page = st.sidebar.radio("Go to", ["Home", "Employees", "Meetings", "Disciplinary", "Performance", "Training", "Reports"])    
    
# -------------------------------    
# 5. Data Upload & Session State    
# -------------------------------    
# Employee Data Upload    
employee_columns = ['employee_id', 'first_name', 'last_name', 'department', 'job_title', 'email', 'phone', 'employment_status']    
uploaded_employees = st.file_uploader("Upload Employees CSV", type="csv")    
if uploaded_employees is not None:    
    try:    
        st.session_state.employees = pd.read_csv(uploaded_employees)    
    except Exception as e:    
        st.error("Error reading uploaded employee file: " + str(e))    
else:    
    if 'employees' not in st.session_state:    
        st.session_state.employees = pd.DataFrame(columns=employee_columns)    
    
# Meeting Data Upload    
meeting_columns = ['meeting_id', 'employee_id', 'meeting_date', 'meeting_time', 'MeetingAgenda', 'action_items', 'notes', 'next_meeting_date']    
uploaded_meetings = st.file_uploader("Upload Meetings CSV", type="csv")    
if uploaded_meetings is not None:    
    try:    
        st.session_state.meetings = pd.read_csv(uploaded_meetings)    
    except Exception as e:    
        st.error("Error reading uploaded meetings file: " + str(e))    
else:    
    if 'meetings' not in st.session_state:    
        st.session_state.meetings = pd.DataFrame(columns=meeting_columns)    
    
# Disciplinary Data Upload    
disciplinary_columns = ['disciplinary_id', 'employee_id', 'type', 'date', 'description']    
uploaded_disciplinary = st.file_uploader("Upload Disciplinary CSV", type="csv")    
if uploaded_disciplinary is not None:    
    try:    
        st.session_state.disciplinary = pd.read_csv(uploaded_disciplinary)    
    except Exception as e:    
        st.error("Error reading uploaded disciplinary file: " + str(e))    
else:    
    if 'disciplinary' not in st.session_state:    
        st.session_state.disciplinary = pd.DataFrame(columns=disciplinary_columns)    
    
# Performance Data Upload    
performance_columns = ['review_id', 'employee_id', 'review_date', 'reviewer', 'score', 'comments']    
uploaded_performance = st.file_uploader("Upload Performance CSV", type="csv")    
if uploaded_performance is not None:    
    try:    
        st.session_state.performance = pd.read_csv(uploaded_performance)    
    except Exception as e:    
        st.error("Error reading uploaded performance file: " + str(e))    
else:    
    if 'performance' not in st.session_state:    
        st.session_state.performance = pd.DataFrame(columns=performance_columns)    
    
# Training Data Upload    
training_columns = ['training_id', 'employee_id', 'course_name', 'start_date', 'end_date', 'status', 'certification']    
uploaded_training = st.file_uploader("Upload Training CSV", type="csv")    
if uploaded_training is not None:    
    try:    
        st.session_state.training = pd.read_csv(uploaded_training)    
    except Exception as e:    
        st.error("Error reading uploaded training file: " + str(e))    
else:    
    if 'training' not in st.session_state:    
        st.session_state.training = pd.DataFrame(columns=training_columns)    
  
# Initialize session state data from SQLite if not loaded already  
if "data_loaded" not in st.session_state:  
    st.session_state.data_loaded = False  
  
if not st.session_state.data_loaded:  
    load_all_data_sqlite()  
    st.session_state.data_loaded = True  
    
# -------------------------------    
# 6. Sidebar: Save Button    
# -------------------------------    
st.sidebar.title("Data Management")    
if st.sidebar.button("Save All Data"):    
    save_all_data_sqlite()    
    
# -------------------------------    
# 7. Search Functionality    
# -------------------------------    
st.sidebar.title("Search")    
search_term = st.sidebar.text_input("Search by ID or Name")    
    
if search_term:    
    # Search in employee data    
    employee_results = st.session_state.employees[    
        st.session_state.employees['employee_id'].astype(str).str.contains(search_term, case=False) |    
        st.session_state.employees['first_name'].astype(str).str.contains(search_term, case=False) |    
        st.session_state.employees['last_name'].astype(str).str.contains(search_term, case=False)    
    ]    
      
    if not employee_results.empty:    
        st.subheader("Employee Results")    
        st.dataframe(employee_results)    
          
        # If only one employee found, show their details    
        if len(employee_results) == 1:    
            employee_id = employee_results.iloc[0]['employee_id']    
            st.subheader(f"Details for {employee_results.iloc[0]['first_name']} {employee_results.iloc[0]['last_name']}")    
              
            # Meetings for this employee    
            meetings = st.session_state.meetings[st.session_state.meetings['employee_id'] == employee_id]    
            if not meetings.empty:    
                st.write("Meetings:")    
                st.dataframe(meetings)    
              
            # Disciplinary records    
            disciplinary = st.session_state.disciplinary[st.session_state.disciplinary['employee_id'] == employee_id]    
            if not disciplinary.empty:    
                st.write("Disciplinary Records:")    
                st.dataframe(disciplinary)    
              
            # Performance reviews    
            performance = st.session_state.performance[st.session_state.performance['employee_id'] == employee_id]    
            if not performance.empty:    
                st.write("Performance Reviews:")    
                st.dataframe(performance)    
              
            # Training records    
            training = st.session_state.training[st.session_state.training['employee_id'] == employee_id]    
            if not training.empty:    
                st.write("Training Records:")    
                st.dataframe(training)    
    else:    
        st.info("No employees found matching your search.")    
    
# -------------------------------    
# 8. Page Content    
# -------------------------------    
if page == "Home":    
    st.title("Employee Records Management")    
    st.write("Welcome to the Employee Records Management System. Use the sidebar to navigate to different sections.")    
      
    # Display summary statistics    
    st.subheader("Summary Statistics")    
    col1, col2, col3, col4, col5 = st.columns(5)    
      
    with col1:    
        st.metric("Employees", len(st.session_state.employees))    
    with col2:    
        st.metric("Meetings", len(st.session_state.meetings))    
    with col3:    
        st.metric("Disciplinary Records", len(st.session_state.disciplinary))    
    with col4:    
        st.metric("Performance Reviews", len(st.session_state.performance))    
    with col5:    
        st.metric("Training Records", len(st.session_state.training))    
      
    # Display recent activity    
    st.subheader("Recent Activity")    
      
    # Recent meetings    
    if not st.session_state.meetings.empty:    
        st.write("Recent Meetings:")    
        recent_meetings = st.session_state.meetings.copy()    
        if 'meeting_date' in recent_meetings.columns:    
            recent_meetings['meeting_date'] = pd.to_datetime(recent_meetings['meeting_date'], errors='coerce')    
            recent_meetings = recent_meetings.sort_values('meeting_date', ascending=False).head(5)    
        st.dataframe(recent_meetings)    
      
    # Recent performance reviews    
    if not st.session_state.performance.empty:    
        st.write("Recent Performance Reviews:")    
        recent_performance = st.session_state.performance.copy()    
        if 'review_date' in recent_performance.columns:    
            recent_performance['review_date'] = pd.to_datetime(recent_performance['review_date'], errors='coerce')    
            recent_performance = recent_performance.sort_values('review_date', ascending=False).head(5)    
        st.dataframe(recent_performance)    
    
elif page == "Employees":    
    st.title("Employee Management")    
      
    # Add new employee button    
    if st.button("Add New Employee"):    
        st.session_state.add_employee = True    
      
    # Add new employee form    
    if 'add_employee' in st.session_state and st.session_state.add_employee:    
        st.subheader("Add New Employee")    
        with st.form("new_employee_form"):    
            new_employee_id = st.text_input("Employee ID")    
            col1, col2 = st.columns(2)    
            with col1:    
                new_first_name = st.text_input("First Name")    
                new_department = st.text_input("Department")    
                new_email = st.text_input("Email")    
                new_employment_status = st.selectbox("Employment Status", ["Active", "On Leave", "Terminated"])    
            with col2:    
                new_last_name = st.text_input("Last Name")    
                new_job_title = st.text_input("Job Title")    
                new_phone = st.text_input("Phone")    
              
            submitted = st.form_submit_button("Save Employee")    
            if submitted:    
                # Check if employee ID already exists    
                if new_employee_id in st.session_state.employees['employee_id'].values:    
                    st.error("Employee ID already exists. Please use a unique ID.")    
                else:    
                    # Add new employee to dataframe    
                    new_employee = pd.DataFrame({    
                        'employee_id': [new_employee_id],    
                        'first_name': [new_first_name],    
                        'last_name': [new_last_name],    
                        'department': [new_department],    
                        'job_title': [new_job_title],    
                        'email': [new_email],    
                        'phone': [new_phone],    
                        'employment_status': [new_employment_status]    
                    })    
                    st.session_state.employees = pd.concat([st.session_state.employees, new_employee], ignore_index=True)    
                    st.success("Employee added successfully!")    
                    st.session_state.add_employee = False    
                    st.experimental_rerun()    
      
    # Display employee data    
    if not st.session_state.employees.empty:    
        st.subheader("Employee List")    
        st.dataframe(st.session_state.employees)    
          
        # Edit employee    
        st.subheader("Edit Employee")    
        employee_to_edit = st.selectbox("Select Employee", st.session_state.employees['employee_id'].tolist())    
        if st.button("Edit Selected Employee"):    
            st.session_state.edit_employee = employee_to_edit    
          
        if 'edit_employee' in st.session_state and st.session_state.edit_employee:    
            employee_data = st.session_state.employees[st.session_state.employees['employee_id'] == st.session_state.edit_employee].iloc[0]    
              
            st.subheader(f"Edit Employee: {employee_data['first_name']} {employee_data['last_name']}")    
            with st.form("edit_employee_form"):    
                col1, col2 = st.columns(2)    
                with col1:    
                    new_first_name = st.text_input("First Name", value=employee_data['first_name'])    
                    new_department = st.text_input("Department", value=employee_data['department'])    
                    new_email = st.text_input("Email", value=employee_data['email'])    
                    new_employment_status = st.selectbox("Employment Status", ["Active", "On Leave", "Terminated"], index=["Active", "On Leave", "Terminated"].index(employee_data['employment_status']) if employee_data['employment_status'] in ["Active", "On Leave", "Terminated"] else 0)    
                with col2:    
                    new_last_name = st.text_input("Last Name", value=employee_data['last_name'])    
                    new_job_title = st.text_input("Job Title", value=employee_data['job_title'])    
                    new_phone = st.text_input("Phone", value=employee_data['phone'])    
                  
                submitted = st.form_submit_button("Update Employee")    
                if submitted:    
                    # Update employee data    
                    st.session_state.employees.loc[st.session_state.employees['employee_id'] == st.session_state.edit_employee, 'first_name'] = new_first_name    
                    st.session_state.employees.loc[st.session_state.employees['employee_id'] == st.session_state.edit_employee, 'last_name'] = new_last_name    
                    st.session_state.employees.loc[st.session_state.employees['employee_id'] == st.session_state.edit_employee, 'department'] = new_department    
                    st.session_state.employees.loc[st.session_state.employees['employee_id'] == st.session_state.edit_employee, 'job_title'] = new_job_title    
                    st.session_state.employees.loc[st.session_state.employees['employee_id'] == st.session_state.edit_employee, 'email'] = new_email    
                    st.session_state.employees.loc[st.session_state.employees['employee_id'] == st.session_state.edit_employee, 'phone'] = new_phone    
                    st.session_state.employees.loc[st.session_state.employees['employee_id'] == st.session_state.edit_employee, 'employment_status'] = new_employment_status    
                      
                    st.success("Employee updated successfully!")    
                    st.session_state.edit_employee = None    
                    st.experimental_rerun()    
          
        # Delete employee    
        st.subheader("Delete Employee")    
        employee_to_delete = st.selectbox("Select Employee to Delete", st.session_state.employees['employee_id'].tolist(), key="delete_employee")    
        if st.button("Delete Selected Employee"):    
            # Check if employee has related records    
            has_meetings = employee_to_delete in st.session_state.meetings['employee_id'].values    
            has_disciplinary = employee_to_delete in st.session_state.disciplinary['employee_id'].values    
            has_performance = employee_to_delete in st.session_state.performance['employee_id'].values    
            has_training = employee_to_delete in st.session_state.training['employee_id'].values    
              
            if has_meetings or has_disciplinary or has_performance or has_training:    
                st.warning("This employee has related records. Deleting will also remove all related records.")    
                if st.button("Confirm Delete"):    
                    # Delete employee and related records    
                    st.session_state.employees = st.session_state.employees[st.session_state.employees['employee_id'] != employee_to_delete]    
                    st.session_state.meetings = st.session_state.meetings[st.session_state.meetings['employee_id'] != employee_to_delete]    
                    st.session_state.disciplinary = st.session_state.disciplinary[st.session_state.disciplinary['employee_id'] != employee_to_delete]    
                    st.session_state.performance = st.session_state.performance[st.session_state.performance['employee_id'] != employee_to_delete]    
                    st.session_state.training = st.session_state.training[st.session_state.training['employee_id'] != employee_to_delete]    
                      
                    st.success("Employee and related records deleted successfully!")    
                    st.experimental_rerun()    
            else:    
                # Delete employee    
                st.session_state.employees = st.session_state.employees[st.session_state.employees['employee_id'] != employee_to_delete]    
                st.success("Employee deleted successfully!")    
                st.experimental_rerun()    
    else:    
        st.info("No employee data available. Please add employees or upload a CSV file.")    
    
elif page == "Meetings":    
    st.title("Meeting Management")    
      
    # Add new meeting button    
    if st.button("Add New Meeting"):    
        st.session_state.add_meeting = True    
      
    # Add new meeting form    
    if 'add_meeting' in st.session_state and st.session_state.add_meeting:    
        st.subheader("Add New Meeting")    
        with st.form("new_meeting_form"):    
            new_meeting_id = st.text_input("Meeting ID")    
              
            # Employee selection    
            if not st.session_state.employees.empty:    
                employee_options = st.session_state.employees.copy()    
                employee_options['employee_name'] = employee_options['first_name'] + ' ' + employee_options['last_name']    
                employee_dict = dict(zip(employee_options['employee_id'], employee_options['employee_name']))    
                selected_employee_name = st.selectbox("Employee", employee_options['employee_name'].tolist())    
                new_employee_id = employee_options[employee_options['employee_name'] == selected_employee_name]['employee_id'].iloc[0]    
            else:    
                new_employee_id = st.text_input("Employee ID")    
              
            col1, col2 = st.columns(2)    
            with col1:    
                new_meeting_date = st.date_input("Meeting Date")    
                new_meeting_time = st.text_input("Meeting Time")    
                new_next_meeting_date = st.date_input("Next Meeting Date")    
            with col2:    
                new_agenda = st.text_input("Agenda")    
                new_action_items = st.text_input("Action Items")    
              
            new_notes = st.text_area("Notes")    
              
            submitted = st.form_submit_button("Save Meeting")    
            if submitted:    
                # Check if meeting ID already exists    
                if new_meeting_id in st.session_state.meetings['meeting_id'].values:    
                    st.error("Meeting ID already exists. Please use a unique ID.")    
                else:    
                    # Add new meeting to dataframe    
                    new_meeting = pd.DataFrame({    
                        'meeting_id': [new_meeting_id],    
                        'employee_id': [new_employee_id],    
                        'meeting_date': [new_meeting_date.strftime('%Y-%m-%d')],    
                        'meeting_time': [new_meeting_time],    
                        'MeetingAgenda': [new_agenda],    
                        'action_items': [new_action_items],    
                        'notes': [new_notes],    
                        'next_meeting_date': [new_next_meeting_date.strftime('%Y-%m-%d')]    
                    })    
                    st.session_state.meetings = pd.concat([st.session_state.meetings, new_meeting], ignore_index=True)    
                    st.success("Meeting added successfully!")    
                    st.session_state.add_meeting = False    
                    st.experimental_rerun()    
      
    # Display meeting data    
    if not st.session_state.meetings.empty:    
        st.subheader("Meeting List")    
          
        # Join with employee data to show names    
        if not st.session_state.employees.empty:    
            meetings_with_names = st.session_state.meetings.merge(    
                st.session_state.employees[['employee_id', 'first_name', 'last_name']],    
                on='employee_id',    
                how='left'    
            )    
            meetings_with_names['employee_name'] = meetings_with_names['first_name'] + ' ' + meetings_with_names['last_name']    
            display_cols = ['meeting_id', 'employee_name', 'meeting_date', 'meeting_time', 'MeetingAgenda']    
            st.dataframe(meetings_with_names[display_cols])    
        else:    
            st.dataframe(st.session_state.meetings)    
          
        # Edit meeting    
        st.subheader("Edit Meeting")    
        meeting_to_edit = st.selectbox("Select Meeting", st.session_state.meetings['meeting_id'].tolist())    
        if st.button("Edit Selected Meeting"):    
            st.session_state.edit_meeting = meeting_to_edit    
          
        if 'edit_meeting' in st.session_state and st.session_state.edit_meeting:    
            meeting_data = st.session_state.meetings[st.session_state.meetings['meeting_id'] == st.session_state.edit_meeting].iloc[0]    
              
            st.subheader(f"Edit Meeting: {meeting_data['meeting_id']}")    
            with st.form("edit_meeting_form"):    
                # Employee selection    
                if not st.session_state.employees.empty:    
                    employee_options = st.session_state.employees.copy()    
                    employee_options['employee_name'] = employee_options['first_name'] + ' ' + employee_options['last_name']    
                    employee_dict = dict(zip(employee_options['employee_id'], employee_options['employee_name']))    
                      
                    current_employee_name = employee_dict.get(meeting_data['employee_id'], "Unknown")    
                    selected_employee_name = st.selectbox("Employee", employee_options['employee_name'].tolist(), index=employee_options['employee_name'].tolist().index(current_employee_name) if current_employee_name in employee_options['employee_name'].tolist() else 0)    
                    new_employee_id = employee_options[employee_options['employee_name'] == selected_employee_name]['employee_id'].iloc[0]    
                else:    
                    new_employee_id = st.text_input("Employee ID", value=meeting_data['employee_id'])    
                  
                col1, col2 = st.columns(2)    
                with col1:    
                    new_meeting_date = st.date_input("Meeting Date", value=pd.to_datetime(meeting_data['meeting_date']) if pd.notna(meeting_data['meeting_date']) else datetime.datetime.now())    
                    new_meeting_time = st.text_input("Meeting Time", value=meeting_data['meeting_time'])    
                    new_next_meeting_date = st.date_input("Next Meeting Date", value=pd.to_datetime(meeting_data['next_meeting_date']) if pd.notna(meeting_data['next_meeting_date']) else None)    
                with col2
