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
  
# -------------------------------  
# 2. CSV Download Helper Function  
# -------------------------------  
def get_csv_download_link(df, filename, label='Download CSV file'):  
    csv = df.to_csv(index=False)  
    b64 = base64.b64encode(csv.encode()).decode()  
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">{label}</a>'  
  
# -------------------------------  
# 3. SQLite Database Functions  
# -------------------------------  
def init_sqlite_db():  
    """Initialize SQLite database with required tables."""  
    conn = sqlite3.connect('employee_database.db')  
    cursor = conn.cursor()  
      
    # Create employees table  
    cursor.execute('''  
    CREATE TABLE IF NOT EXISTS employees (  
        employee_id TEXT PRIMARY KEY,  
        first_name TEXT,  
        last_name TEXT,  
        email TEXT,  
        phone TEXT,  
        department TEXT,  
        job_title TEXT,  
        employment_status TEXT  
    )  
    ''')  
      
    # Create meetings table  
    cursor.execute('''  
    CREATE TABLE IF NOT EXISTS meetings (  
        meeting_id INTEGER PRIMARY KEY AUTOINCREMENT,  
        employee_id TEXT,  
        date TEXT,  
        meeting_type TEXT,  
        notes TEXT  
    )  
    ''')  
      
    # Create disciplinary table  
    cursor.execute('''  
    CREATE TABLE IF NOT EXISTS disciplinary (  
        disciplinary_id INTEGER PRIMARY KEY AUTOINCREMENT,  
        employee_id TEXT,  
        date TEXT,  
        violation_type TEXT,  
        action_taken TEXT,  
        notes TEXT  
    )  
    ''')  
      
    # Create performance table  
    cursor.execute('''  
    CREATE TABLE IF NOT EXISTS performance (  
        performance_id INTEGER PRIMARY KEY AUTOINCREMENT,  
        employee_id TEXT,  
        date TEXT,  
        rating TEXT,  
        strengths TEXT,  
        areas_for_improvement TEXT,  
        goals TEXT,  
        notes TEXT  
    )  
    ''')  
      
    # Create training table  
    cursor.execute('''  
    CREATE TABLE IF NOT EXISTS training (  
        training_id INTEGER PRIMARY KEY AUTOINCREMENT,  
        employee_id TEXT,  
        date TEXT,  
        training_type TEXT,  
        provider TEXT,  
        duration TEXT,  
        certification TEXT,  
        notes TEXT  
    )  
    ''')  
      
    conn.commit()  
    conn.close()  
  
def save_to_sqlite():  
    """Save all dataframes to SQLite database."""  
    conn = sqlite3.connect('employee_database.db')  
      
    # Save employees  
    if 'employees' in st.session_state and not st.session_state.employees.empty:  
        st.session_state.employees.to_sql('employees', conn, if_exists='replace', index=False)  
      
    # Save meetings  
    if 'meetings' in st.session_state and not st.session_state.meetings.empty:  
        st.session_state.meetings.to_sql('meetings', conn, if_exists='replace', index=False)  
      
    # Save disciplinary  
    if 'disciplinary' in st.session_state and not st.session_state.disciplinary.empty:  
        st.session_state.disciplinary.to_sql('disciplinary', conn, if_exists='replace', index=False)  
      
    # Save performance  
    if 'performance' in st.session_state and not st.session_state.performance.empty:  
        st.session_state.performance.to_sql('performance', conn, if_exists='replace', index=False)  
      
    # Save training  
    if 'training' in st.session_state and not st.session_state.training.empty:  
        st.session_state.training.to_sql('training', conn, if_exists='replace', index=False)  
      
    conn.close()  
  
def load_from_sqlite():  
    """Load all dataframes from SQLite database."""  
    conn = sqlite3.connect('employee_database.db')  
      
    # Load employees  
    try:  
        st.session_state.employees = pd.read_sql('SELECT * FROM employees', conn)  
    except:  
        st.session_state.employees = pd.DataFrame()  
      
    # Load meetings  
    try:  
        st.session_state.meetings = pd.read_sql('SELECT * FROM meetings', conn)  
    except:  
        st.session_state.meetings = pd.DataFrame()  
      
    # Load disciplinary  
    try:  
        st.session_state.disciplinary = pd.read_sql('SELECT * FROM disciplinary', conn)  
    except:  
        st.session_state.disciplinary = pd.DataFrame()  
      
    # Load performance  
    try:  
        st.session_state.performance = pd.read_sql('SELECT * FROM performance', conn)  
    except:  
        st.session_state.performance = pd.DataFrame()  
      
    # Load training  
    try:  
        st.session_state.training = pd.read_sql('SELECT * FROM training', conn)  
    except:  
        st.session_state.training = pd.DataFrame()  
      
    conn.close()  
  
# -------------------------------  
# 4. Data Loading Functions  
# -------------------------------  
def load_from_uploaded_file(uploaded_file, columns):  
    """Load data from an uploaded CSV file."""  
    try:  
        df = pd.read_csv(uploaded_file)  
        # Ensure all required columns exist  
        for col in columns:  
            if col not in df.columns:  
                df[col] = ""  
        # Only keep the columns we need  
        df = df[columns]  
        return df  
    except Exception as e:  
        st.error(f"Error loading file: {e}")  
        return pd.DataFrame(columns=columns)  
  
# -------------------------------  
# 5. Initialize Session State  
# -------------------------------  
# Define column structures  
employee_columns = ["employee_id", "first_name", "last_name", "email", "phone", "department", "job_title", "employment_status"]  
meeting_columns = ["employee_id", "date", "meeting_type", "notes"]  
disciplinary_columns = ["employee_id", "date", "violation_type", "action_taken", "notes"]  
performance_columns = ["employee_id", "date", "rating", "strengths", "areas_for_improvement", "goals", "notes"]  
training_columns = ["employee_id", "date", "training_type", "provider", "duration", "certification", "notes"]  
  
# Initialize database  
init_sqlite_db()  
  
# Initialize session state variables if they don't exist  
if 'employees' not in st.session_state:  
    st.session_state.employees = pd.DataFrame(columns=employee_columns)  
if 'meetings' not in st.session_state:  
    st.session_state.meetings = pd.DataFrame(columns=meeting_columns)  
if 'disciplinary' not in st.session_state:  
    st.session_state.disciplinary = pd.DataFrame(columns=disciplinary_columns)  
if 'performance' not in st.session_state:  
    st.session_state.performance = pd.DataFrame(columns=performance_columns)  
if 'training' not in st.session_state:  
    st.session_state.training = pd.DataFrame(columns=training_columns)  
  
# Load data from SQLite on startup  
load_from_sqlite()  
  
# -------------------------------  
# 6. Sidebar  
# -------------------------------  
st.sidebar.title("Employee Records Tool")  
  
# Module selection  
module = st.sidebar.selectbox(  
    "Select Module",  
    ["Employee Management", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records", "Reports"]  
)  
  
# Save All Data button  
if st.sidebar.button("Save All Data"):  
    save_to_sqlite()  
    st.sidebar.success("All data saved successfully!")  
  
# -------------------------------  
# 7. Module: Employee Management  
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
        with col2:  
            last_name = st.text_input("Last Name")  
            email = st.text_input("Email")  
        phone = st.text_input("Phone")  
        department = st.text_input("Department")  
        job_title = st.text_input("Job Title")  
        employment_status = st.selectbox("Employment Status", ["Active", "Inactive", "Terminated"])  
        submit_button = st.form_submit_button("Add Employee")  
          
        if submit_button:  
            if not employee_id:  
                st.error("Employee ID is required!")  
            else:  
                new_employee = {  
                    "employee_id": employee_id,  
                    "first_name": first_name,  
                    "last_name": last_name,  
                    "email": email,  
                    "phone": phone,  
                    "department": department,  
                    "job_title": job_title,  
                    "employment_status": employment_status  
                }  
                if st.session_state.employees.empty:  
                    st.session_state.employees = pd.DataFrame([new_employee])  
                else:  
                    st.session_state.employees = pd.concat([st.session_state.employees, pd.DataFrame([new_employee])], ignore_index=True)  
                st.success("Employee " + employee_id + " added successfully!")  
  
# -------------------------------  
# 8. Module: One-on-One Meetings  
# -------------------------------  
elif module == "One-on-One Meetings":  
    st.header("One-on-One Meetings")  
      
    with st.form("meeting_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            meeting_employee_id = st.text_input("Employee ID")  
            meeting_date = st.date_input("Meeting Date", datetime.datetime.now())  
        with col2:  
            meeting_type = st.text_input("Meeting Type")  
            meeting_notes = st.text_area("Notes")  
        meeting_submit = st.form_submit_button("Add Meeting")  
          
        if meeting_submit:  
            new_meeting = {  
                "employee_id": meeting_employee_id,  
                "date": meeting_date.strftime("%Y-%m-%d"),  
                "meeting_type": meeting_type,  
                "notes": meeting_notes  
            }  
            if st.session_state.meetings.empty:  
                st.session_state.meetings = pd.DataFrame([new_meeting])  
            else:  
                st.session_state.meetings = pd.concat([st.session_state.meetings, pd.DataFrame([new_meeting])], ignore_index=True)  
            st.success("Meeting added successfully!")  
  
# -------------------------------  
# 9. Module: Disciplinary Actions  
# -------------------------------  
elif module == "Disciplinary Actions":  
    st.header("Disciplinary Actions")  
      
    with st.form("disciplinary_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            disciplinary_employee_id = st.text_input("Employee ID")  
            disciplinary_date = st.date_input("Date", datetime.datetime.now())  
        with col2:  
            violation_type = st.text_input("Violation Type")  
            action_taken = st.text_input("Action Taken")  
        disciplinary_notes = st.text_area("Notes")  
        disciplinary_submit = st.form_submit_button("Add Disciplinary Action")  
          
        if disciplinary_submit:  
            new_disciplinary = {  
                "employee_id": disciplinary_employee_id,  
                "date": disciplinary_date.strftime("%Y-%m-%d"),  
                "violation_type": violation_type,  
                "action_taken": action_taken,  
                "notes": disciplinary_notes  
            }  
            if st.session_state.disciplinary.empty:  
                st.session_state.disciplinary = pd.DataFrame([new_disciplinary])  
            else:  
                st.session_state.disciplinary = pd.concat([st.session_state.disciplinary, pd.DataFrame([new_disciplinary])], ignore_index=True)  
            st.success("Disciplinary action added successfully!")  
  
# -------------------------------  
# 10. Module: Performance Reviews  
# -------------------------------  
elif module == "Performance Reviews":  
    st.header("Performance Reviews")  
      
    with st.form("performance_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            performance_employee_id = st.text_input("Employee ID")  
            performance_date = st.date_input("Review Date", datetime.datetime.now())  
            rating = st.selectbox("Rating", ["Excellent", "Good", "Satisfactory", "Needs Improvement", "Poor"])  
        with col2:  
            strengths = st.text_area("Strengths")  
            areas_for_improvement = st.text_area("Areas for Improvement")  
        goals = st.text_area("Goals")  
        performance_notes = st.text_area("Additional Notes")  
        performance_submit = st.form_submit_button("Add Performance Review")  
          
        if performance_submit:  
            new_performance = {  
                "employee_id": performance_employee_id,  
                "date": performance_date.strftime("%Y-%m-%d"),  
                "rating": rating,  
                "strengths": strengths,  
                "areas_for_improvement": areas_for_improvement,  
                "goals": goals,  
                "notes": performance_notes  
            }  
            if st.session_state.performance.empty:  
                st.session_state.performance = pd.DataFrame([new_performance])  
            else:  
                st.session_state.performance = pd.concat([st.session_state.performance, pd.DataFrame([new_performance])], ignore_index=True)  
            st.success("Performance review added successfully!")  
  
# -------------------------------  
# 11. Module: Training Records  
# -------------------------------  
elif module == "Training Records":  
    st.header("Training Records")  
      
    with st.form("training_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            training_employee_id = st.text_input("Employee ID")  
            training_date = st.date_input("Training Date", datetime.datetime.now())  
            training_type = st.text_input("Training Type")  
        with col2:  
            provider = st.text_input("Provider")  
            duration = st.text_input("Duration")  
            certification = st.text_input("Certification")  
        training_notes = st.text_area("Notes")  
        training_submit = st.form_submit_button("Add Training Record")  
          
        if training_submit:  
            new_training = {  
                "employee_id": training_employee_id,  
                "date": training_date.strftime("%Y-%m-%d"),  
                "training_type": training_type,  
                "provider": provider,  
                "duration": duration,  
                "certification": certification,  
                "notes": training_notes  
            }  
            if st.session_state.training.empty:  
                st.session_state.training = pd.DataFrame([new_training])  
            else:  
                st.session_state.training = pd.concat([st.session_state.training, pd.DataFrame([new_training])], ignore_index=True)  
            st.success("Training record added successfully!")  
  
# -------------------------------  
# 12. Module: Reports  
# -------------------------------  
elif module == "Reports":  
    st.header("Reports")  
      
    report_type = st.selectbox("Select Report Type", ["Employees", "Meetings", "Disciplinary", "Performance", "Training"])  
      
    if report_type == "Employees":  
        if not st.session_state.employees.empty:  
            st.dataframe(st.session_state.employees)  
            st.markdown(get_csv_download_link(st.session_state.employees, "employees_report.csv"), unsafe_allow_html=True)  
        else:  
            st.info("No employee data available.")  
    elif report_type == "Meetings":  
        if not st.session_state.meetings.empty:  
            st.dataframe(st.session_state.meetings)  
            st.markdown(get_csv_download_link(st.session_state.meetings, "meetings_report.csv"), unsafe_allow_html=True)  
        else:  
            st.info("No meeting data available.")  
    elif report_type == "Disciplinary":  
        if not st.session_state.disciplinary.empty:  
            st.dataframe(st.session_state.disciplinary)  
            st.markdown(get_csv_download_link(st.session_state.disciplinary, "disciplinary_report.csv"), unsafe_allow_html=True)  
        else:  
            st.info("No disciplinary records available.")  
    elif report_type == "Performance":  
        if not st.session_state.performance.empty:  
            st.dataframe(st.session_state.performance)  
            st.markdown(get_csv_download_link(st.session_state.performance, "performance_report.csv"), unsafe_allow_html=True)  
        else:  
            st.info("No performance reviews available.")  
    elif report_type == "Training":  
        if not st.session_state.training.empty:  
            st.dataframe(st.session_state.training)  
            st.markdown(get_csv_download_link(st.session_state.training, "training_report.csv"), unsafe_allow_html=True)  
        else:  
            st.info("No training records available.")  
      
    # Export options  
    st.subheader("Export Report")  
    if st.button("Export to CSV"):  
        if 'report_df' in locals() and report_df is not None:  
            csv = report_df.to_csv(index=False)  
            b64 = base64.b64encode(csv.encode()).decode()  
            href = f'<a href="data:file/csv;base64,{b64}" download="report.csv">Download CSV File</a>'  
            st.markdown(href, unsafe_allow_html=True)  
        else:  
            st.error("No report data to export.")  
