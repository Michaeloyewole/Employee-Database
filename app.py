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
# 2. CSV Upload/Download Functions    
# -------------------------------    
def get_csv_download_link(df, filename, label='Download CSV file'):    
    csv = df.to_csv(index=False)    
    b64 = base64.b64encode(csv.encode()).decode()    
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">{label}</a>'    
  
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
  
# New function to auto-populate employee details  
def auto_populate_employee_details(employee_id):  
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
# 4. Initialize Session State as Empty DataFrames    
# -------------------------------    
if 'employees' not in st.session_state:    
    employee_columns = ['employee_id', 'first_name', 'last_name', 'department', 'position', 'hire_date']    
    st.session_state.employees = pd.DataFrame({col: [] for col in employee_columns})    
  
if 'meetings' not in st.session_state:    
    meeting_columns = ['meeting_id', 'employee_id', 'meeting_date', 'meeting_type', 'notes']    
    st.session_state.meetings = pd.DataFrame({col: [] for col in meeting_columns})    
  
if 'training' not in st.session_state:    
    training_columns = ['training_id', 'employee_id', 'course_name', 'completion_date', 'status']    
    st.session_state.training = pd.DataFrame({col: [] for col in training_columns})    
  
# -------------------------------    
# 5. Sidebar Navigation (Modules)    
# -------------------------------    
st.sidebar.title("Modules")  
module = st.sidebar.radio("Select Module",   
                          options=["Employee Records", "Meeting Records", "Training Completion", "Reports"])  
st.session_state.current_module = module  
  
# -------------------------------    
# 6. Module: Employee Records    
# -------------------------------    
if st.session_state.current_module == "Employee Records":  
    st.title("Employee Records")  
      
    # CSV Upload for Employees  
    st.subheader("Upload Employee CSV File")  
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])  
    employee_columns = ['employee_id', 'first_name', 'last_name', 'department', 'position', 'hire_date']  
    if uploaded_file is not None:  
        st.session_state.employees = load_from_uploaded_file(uploaded_file, employee_columns)  
        st.success("Employee data loaded from file.")  
      
    # Form for adding/updating employees  
    st.subheader("Add / Update Employee")  
    with st.form(key="employee_form"):  
        employee_id = st.text_input("Employee ID")  
        # Auto-populate details if employee exists  
        details = auto_populate_employee_details(employee_id)  
        if details:  
            st.info("Employee exists. Details auto-populated.")  
        first_name = st.text_input("First Name", value=details['first_name'] if details else "")  
        last_name = st.text_input("Last Name", value=details['last_name'] if details else "")  
        department = st.text_input("Department", value=details['department'] if details else "")  
        position = st.text_input("Position", value=details['position'] if details else "")  
        hire_date = st.date_input("Hire Date", value=datetime.datetime.strptime(details['hire_date'], '%Y-%m-%d').date() if details and details.get('hire_date') else datetime.date.today())  
        submit_emp = st.form_submit_button("Save Employee")  
    if submit_emp:  
        if employee_id in st.session_state.employees['employee_id'].values:  
            idx = st.session_state.employees.index[st.session_state.employees['employee_id'] == employee_id][0]  
            st.session_state.employees.at[idx, 'first_name'] = first_name  
            st.session_state.employees.at[idx, 'last_name'] = last_name  
            st.session_state.employees.at[idx, 'department'] = department  
            st.session_state.employees.at[idx, 'position'] = position  
            st.session_state.employees.at[idx, 'hire_date'] = hire_date  
            st.success("Updated employee: " + first_name + " " + last_name)  
        else:  
            new_employee = pd.DataFrame({  
                'employee_id': [employee_id],  
                'first_name': [first_name],  
                'last_name': [last_name],  
                'department': [department],  
                'position': [position],  
                'hire_date': [hire_date]  
            })  
            st.session_state.employees = pd.concat([st.session_state.employees, new_employee], ignore_index=True)  
            st.success("Added new employee: " + first_name + " " + last_name)  
        save_table("employees", st.session_state.employees)  
      
    # CSV Download for Employees  
    st.markdown(get_csv_download_link(st.session_state.employees, "employees.csv", "Download Employees CSV"), unsafe_allow_html=True)  
      
    # Delete employee  
    del_id = st.text_input("Enter Employee ID to Delete")  
    if st.button("Delete Employee") and del_id:  
        if not st.session_state.employees[st.session_state.employees['employee_id'] == del_id].empty:  
            st.session_state.employees = st.session_state.employees[st.session_state.employees['employee_id'] != del_id]  
            save_table("employees", st.session_state.employees)  
            st.success("Employee record deleted.")  
        else:  
            st.error("Employee ID not found.")  
  
# -------------------------------    
# 7. Module: Meeting Records    
# -------------------------------    
elif st.session_state.current_module == "Meeting Records":  
    st.title("Meeting Records")  
      
    # CSV Upload for Meetings  
    st.subheader("Upload Meeting CSV File")  
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"], key="meetings_upload")  
    meeting_columns = ['meeting_id', 'employee_id', 'meeting_date', 'meeting_type', 'notes']  
    if uploaded_file is not None:  
        st.session_state.meetings = load_from_uploaded_file(uploaded_file, meeting_columns)  
        st.success("Meeting data loaded from file.")  
      
    # Form for adding meeting records  
    st.subheader("Add Meeting Record")  
    with st.form(key="meeting_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            meeting_id = st.text_input("Meeting ID")  
            employee_options = [""] + st.session_state.employees['employee_id'].tolist()  
            meeting_employee = st.selectbox("Employee", employee_options)  
            meeting_date = st.date_input("Meeting Date")  
        with col2:  
            meeting_type = st.selectbox("Meeting Type", ["", "One-on-One", "Performance Review", "Project Discussion", "Other"])  
            notes = st.text_area("Notes")  
        submit_meet = st.form_submit_button("Save Meeting")  
    if submit_meet:  
        new_meeting = pd.DataFrame({  
            'meeting_id': [meeting_id],  
            'employee_id': [meeting_employee],  
            'meeting_date': [meeting_date.strftime("%Y-%m-%d")],  
            'meeting_type': [meeting_type],  
            'notes': [notes]  
        })  
        st.session_state.meetings = pd.concat([st.session_state.meetings, new_meeting], ignore_index=True)  
        save_table("meetings", st.session_state.meetings)  
        st.success("Meeting record added successfully!")  
      
    # CSV Download for Meetings  
    st.markdown(get_csv_download_link(st.session_state.meetings, "meetings.csv", "Download Meetings CSV"), unsafe_allow_html=True)  
      
# -------------------------------    
# 8. Module: Training Completion    
# -------------------------------    
elif st.session_state.current_module == "Training Completion":  
    st.title("Training Completion")  
      
    # CSV Upload for Training  
    st.subheader("Upload Training CSV File")  
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"], key="training_upload")  
    training_columns = ['training_id', 'employee_id', 'course_name', 'completion_date', 'status']  
    if uploaded_file is not None:  
        st.session_state.training = load_from_uploaded_file(uploaded_file, training_columns)  
        st.success("Training data loaded from file.")  
      
    st.subheader("Training Records")  
    st.dataframe(st
