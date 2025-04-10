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
def get_csv_download_link(df, filename, label="Download CSV file"):  
    csv = df.to_csv(index=False)  
    b64 = base64.b64encode(csv.encode()).decode()  
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">{label}</a>'  
  
# -------------------------------  
# 3. Data Persistence Functions  
# -------------------------------  
def load_table(table_name, columns):  
    path = os.path.join(DATA_DIR, f"{table_name}.csv")  
    if os.path.exists(path):  
        return pd.read_csv(path)  
    else:  
        return pd.DataFrame({col: [] for col in columns})  
  
def save_table(table_name, df):  
    path = os.path.join(DATA_DIR, f"{table_name}.csv")  
    df.to_csv(path, index=False)  
    st.success(f"{table_name.capitalize()} data saved successfully!")  
  
def load_from_uploaded_file(uploaded_file, columns):  
    try:  
        df = pd.read_csv(uploaded_file)  
        # Ensure required columns exist; if not, add them  
        for col in columns:  
            if col not in df.columns:  
                df[col] = ""  
        return df  
    except Exception as e:  
        st.error("Error loading file: " + str(e))  
        return pd.DataFrame({col: [] for col in columns})  
  
# -------------------------------  
# 4. Table Editing Functionality (Single Display)  
# -------------------------------  
def edit_table(df, key_prefix):  
    # Create container for editing  
    edit_container = st.container()  
    with edit_container:  
        if st.button("Edit Table", key=f"{key_prefix}_edit_button"):  
            st.session_state[f"{key_prefix}_edit_mode"] = True  
  
    # If in edit mode, show checkboxes on the table (without duplicating display)  
    if st.session_state.get(f"{key_prefix}_edit_mode", False):  
        with st.container():  
            st.write("Select rows to delete:")  
            if not df.empty:  
                # Create checkboxes for each row  
                selection = [st.checkbox("", key=f"{key_prefix}_select_{i}") for i in range(len(df))]  
                if st.button("Delete Selected Rows", key=f"{key_prefix}_delete_button"):  
                    selected_indices = [i for i, sel in enumerate(selection) if sel]  
                    if selected_indices:  
                        df = df.drop(df.index[selected_indices]).reset_index(drop=True)  
                        st.success(f"Deleted {len(selected_indices)} row(s)")  
                        st.session_state[f"{key_prefix}_edit_mode"] = False  
                    else:  
                        st.warning("No rows selected")  
            else:  
                st.info("No data to edit")  
    return df  
  
# -------------------------------  
# 5. Define Table Columns for Each Module  
# -------------------------------  
employee_columns = [  
    "employee_id", "first_name", "last_name", "department",   
    "job_title", "email", "phone", "employment_status"  
]  
meeting_columns = [  
    "meeting_id", "employee_id", "meeting_date", "meeting_time",  
    "meeting_agenda", "action_items", "notes", "next_meeting_date"  
]  
disciplinary_columns = [  
    "disciplinary_id", "employee_id", "date", "type",   
    "description", "action_taken", "follow_up_date"  
]  
review_columns = [  
    "review_id", "employee_id", "review_date", "score", "feedback"  
]  
training_columns = [  
    "training_id", "employee_id", "training_name", "date_completed", "status"  
]  
  
# -------------------------------  
# 6. Sidebar Navigation  
# -------------------------------  
modules = ["Employee Management", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records", "Reports"]  
module = st.sidebar.selectbox("Select Module", modules)  
  
# -------------------------------  
# 7. Module: Employee Management  
# -------------------------------  
if module == "Employee Management":  
    st.header("Employee Management")  
    if "employees" not in st.session_state:  
        st.session_state.employees = load_table("employees", employee_columns)  
  
    # Employee upload  
    uploaded_employees = st.file_uploader("Upload Employees CSV", type="csv", key="employees_upload")  
    if uploaded_employees is not None:  
        st.session_state.employees = load_from_uploaded_file(uploaded_employees, employee_columns)  
        st.success("Employees data uploaded successfully!")  
      
    # Employee Form (ensuring uniform columns)  
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
            employment_status = st.selectbox("Employment Status", ["Active", "Inactive", "On Leave"])  
        submitted_employee = st.form_submit_button("Submit Employee")  
        if submitted_employee:  
            if employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            else:  
                new_employee = pd.DataFrame({  
                    "employee_id": [int(employee_id)],  
                    "first_name": [first_name],  
                    "last_name": [last_name],  
                    "department": [department],  
                    "job_title": [job_title],  
                    "email": [email],  
                    "phone": [phone],  
                    "employment_status": [employment_status]  
                })  
                # Check if employee exists; update otherwise add  
                if int(employee_id) in st.session_state.employees.get("employee_id", []):  
                    idx = st.session_state.employees[st.session_state.employees["employee_id"] == int(employee_id)].index[0]  
                    st.session_state.employees.loc[idx] = new_employee.iloc[0]  
                    st.success("Employee " + employee_id + " updated successfully!")  
                else:  
                    st.session_state.employees = pd.concat([st.session_state.employees, new_employee], ignore_index=True)  
                    st.success("Employee " + employee_id + " added successfully!")  
  
    st.subheader("Employees Table")  
    st.session_state.employees = edit_table(st.session_state.employees, "employees")  
    st.dataframe(st.session_state.employees)  
    st.markdown(get_csv_download_link(st.session_state.employees, "employees.csv", "Download Employees CSV"), unsafe_allow_html=True)  
    if st.button("Save Employee Data"):  
        save_table("employees", st.session_state.employees)  
  
# -------------------------------  
# 8. Module: One-on-One Meetings  
# -------------------------------  
elif module == "One-on-One Meetings":  
    st.header("One-on-One Meetings")  
    if "meetings" not in st.session_state:  
        st.session_state.meetings = load_table("meetings", meeting_columns)  
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
                    "meeting_id": [int(meeting_id)],  
                    "employee_id": [int(employee_id)],  
                    "meeting_date": [meeting_date.strftime('%Y-%m-%d')],  
                    "meeting_time": [meeting_time.strftime('%H:%M:%S')],  
                    "meeting_agenda": [meeting_agenda],  
                    "action_items": [action_items],  
                    "notes": [notes],  
                    "next_meeting_date": [next_meeting_date.strftime('%Y-%m-%d')]  
                })  
                st.session_state.meetings = pd.concat([st.session_state.meetings, new_meeting], ignore_index=True)  
                st.success("Meeting recorded successfully!")  
      
    st.subheader("Meetings Table")  
    st.session_state.meetings = edit_table(st.session_state.meetings, "meetings")  
    st.dataframe(st.session_state.meetings)  
    st.markdown(get_csv_download_link(st.session_state.meetings, "meetings.csv", "Download Meetings CSV"), unsafe_allow
