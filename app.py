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
    return '<a href="data:file/csv;base64,' + b64 + '" download="' + filename + '">' + label + '</a>'  
  
# -------------------------------  
# 3. Data Persistence Functions  
# -------------------------------  
def load_table(table_name, columns):  
    path = os.path.join(DATA_DIR, f"{table_name}.csv")  
    if os.path.exists(path):  
        return pd.read_csv(path)  
    else:  
        # return an empty DataFrame with the specific columns  
        return pd.DataFrame({col: [] for col in columns})  
  
def save_table(table_name, df):  
    path = os.path.join(DATA_DIR, f"{table_name}.csv")  
    df.to_csv(path, index=False)  
    st.success(table_name.capitalize() + " data saved successfully!")  
  
def get_employee_display_name(employee_id):  
    if employee_id is None or pd.isna(employee_id):  
        return "N/A"  
    employee = st.session_state.employees[st.session_state.employees["employee_id"] == employee_id]  
    if not employee.empty:  
        return employee["first_name"].values[0] + " " + employee["last_name"].values[0]  
    return "Unknown"  
  
def load_from_uploaded_file(uploaded_file, columns):  
    try:  
        df = pd.read_csv(uploaded_file)  
        # ensure column names are stripped  
        df.columns = [col.strip() for col in df.columns]  
        # enforce only the needed columns (if not, data is ignored)  
        return df[[col for col in columns if col in df.columns]]  
    except Exception as e:  
        st.error("Error loading uploaded file: " + str(e))  
        return pd.DataFrame({col: [] for col in columns})  
  
# -------------------------------  
# 4. Sidebar Module Selection (List Module)  
# -------------------------------  
module_options = [  
    "Employee Management",  
    "One-on-One Meetings",  
    "Disciplinary Actions",  
    "Performance Reviews",  
    "Training Records",  
    "Reports"  
]  
# Using radio buttons for a list-like module selection  
selected_module = st.sidebar.radio("Select Module", module_options)  
  
# -------------------------------  
# 5. Main Application Sections  
# -------------------------------  
# Example: Employee management module (empty table structure example)  
  
if selected_module == "Employee Management":  
    st.header("Employee Management")  
    # Define the table structure for employees  
    employee_columns = ["employee_id", "first_name", "last_name", "department", "position"]   
    # load the employees table (will be empty if file not present)  
    if "employees" not in st.session_state:  
        st.session_state.employees = load_table("employees", employee_columns)  
  
    # Form that adapts to the table structure  
    with st.form("employee_form"):  
        st.subheader("Add New Employee")  
        # Create a form input for each column in the table structure.  
        new_employee = {}  
        # You might want the employee_id to be auto-generated or input manually.  
        for col in employee_columns:  
            if col == "employee_id":  
                new_employee[col] = st.text_input("Employee ID")  
            elif col == "first_name":  
                new_employee[col] = st.text_input("First Name")  
            elif col == "last_name":  
                new_employee[col] = st.text_input("Last Name")  
            elif col == "department":  
                new_employee[col] = st.text_input("Department")  
            elif col == "position":  
                new_employee[col] = st.text_input("Position")  
        submitted = st.form_submit_button("Save Employee")  
        if submitted:  
            # Append the new employee record to the DataFrame without any preset data  
            st.session_state.employees = st.session_state.employees.append(new_employee, ignore_index=True)  
            save_table("employees", st.session_state.employees)  
      
    st.subheader("Employee Records")  
    st.dataframe(st.session_state.employees)  
  
# Further modules such as One-on-One Meetings, Disciplinary Actions, etc.  
# can be built similarly, where the table structure and form input adapt to the respective data as needed.  
  
# Example: One-on-One Meetings module (structure without preset data)  
if selected_module == "One-on-One Meetings":  
    st.header("One-on-One Meetings")  
    meeting_columns = ["meeting_id", "employee_id", "meeting_date", "notes"]  
    if "meetings" not in st.session_state:  
        st.session_state.meetings = load_table("meetings", meeting_columns)  
      
    with st.form("meeting_form"):  
        st.subheader("Record a Meeting")  
        new_meeting = {}  
        for col in meeting_columns:  
            if col == "meeting_id":  
                new_meeting[col] = st.text_input("Meeting ID")  
            elif col == "employee_id":  
                new_meeting[col] = st.text_input("Employee ID")  
            elif col == "meeting_date":  
                new_meeting[col] = st.date_input("Meeting Date", datetime.date.today())  
            elif col == "notes":  
                new_meeting[col] = st.text_area("Notes")  
        submitted = st.form_submit_button("Save Meeting")  
        if submitted:  
            st.session_state.meetings = st.session_state.meetings.append(new_meeting, ignore_index=True)  
            save_table("meetings", st.session_state.meetings)  
              
    st.subheader("Meeting Records")  
    st.dataframe(st.session_state.meetings)  
  
# Additional modules (Disciplinary Actions, Performance Reviews, Training Records, Reports) would follow a similar pattern.  
# Remove any sample or preset data so that each table begins empty and is populated only by what you enter.  
print('done')  
