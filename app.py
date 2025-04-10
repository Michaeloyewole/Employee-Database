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
        for col in columns:  
            if col not in df.columns:  
                df[col] = ""  
        return df  
    except Exception as e:  
        st.error("Error loading file: " + str(e))  
        return pd.DataFrame({col: [] for col in columns})  
  
# -------------------------------  
# 4. Define Columns for Each Module (Uniform)  
# -------------------------------  
employee_columns = ["employee_id", "first_name", "last_name", "department", "job_title", "email", "phone", "employment_status"]  
review_columns = ["review_id", "employee_id", "review_date", "score", "comments"]  
meeting_columns = ["meeting_id", "employee_id", "meeting_date", "meeting_time", "meeting_agenda", "action_items", "notes", "next_meeting_date"]  
training_columns = ["training_id", "employee_id", "course_name", "start_date", "end_date", "status", "certification"]  
disciplinary_columns = ["disciplinary_id", "employee_id", "type", "date", "description"]  
  
# -------------------------------  
# 5. Table Editing Function (Single Display)  
# -------------------------------  
def edit_table(df, key_prefix):  
    edit_mode_key = f"{key_prefix}_edit_mode"  
    if edit_mode_key not in st.session_state:  
        st.session_state[edit_mode_key] = False  
          
    if st.button("Edit Table", key=f"{key_prefix}_edit_button"):  
        st.session_state[edit_mode_key] = True  
  
    if st.session_state[edit_mode_key]:  
        st.write("Select rows to delete:")  
        if not df.empty:  
            selection = df.copy()  
            selection['Delete?'] = False  
            edited = st.experimental_data_editor(selection, key=f"{key_prefix}_editor", num_rows="dynamic", use_container_width=True)  
            if st.button("Apply Deletions", key=f"{key_prefix}_delete_button"):  
                # Delete rows marked True in 'Delete?'  
                df = df.drop(edited.index[edited['Delete?'] == True]).reset_index(drop=True)  
                st.success("Deleted selected rows")  
                st.session_state[edit_mode_key] = False  
                return df  
        else:  
            st.info("No data available to edit")  
          
        if st.button("Exit Edit Mode", key=f"{key_prefix}_exit_button"):  
            st.session_state[edit_mode_key] = False  
    return df  
  
# -------------------------------  
# 6. Sidebar Navigation and Session State Setup  
# -------------------------------  
if 'employees' not in st.session_state:  
    st.session_state.employees = load_table("employees", employee_columns)  
if 'reviews' not in st.session_state:  
    st.session_state.reviews = load_table("reviews", review_columns)  
if 'meetings' not in st.session_state:  
    st.session_state.meetings = load_table("meetings", meeting_columns)  
if 'training' not in st.session_state:  
    st.session_state.training = load_table("training", training_columns)  
if 'disciplinary' not in st.session_state:  
    st.session_state.disciplinary = load_table("disciplinary", disciplinary_columns)  
  
modules = ["Employee Management", "Performance Reviews", "One-on-One Meetings", "Training Records", "Disciplinary Actions", "Reports"]  
module = st.sidebar.selectbox("Choose Module", modules)  
  
# -------------------------------  
# 7. Module: Employee Management  
# -------------------------------  
if module == "Employee Management":  
    st.header("Employee Management")  
    # Employee Form  
    with st.form("employee_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            employee_id = st.text_input("Employee ID", max_chars=6)  
            first_name = st.text_input("First Name")  
            last_name = st.text_input("Last Name")  
            department = st.text_input("Department")  
        with col2:  
            job_title = st.text_input("Job Title")  
            email = st.text_input("Email")  
            phone = st.text_input("Phone")  
            employment_status = st.text_input("Employment Status")  
        submitted = st.form_submit_button("Add Employee")  
        if submitted:  
            if employee_id == "" or not employee_id.isdigit():  
                st.error("Enter a valid numeric Employee ID.")  
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
                st.session_state.employees = pd.concat([st.session_state.employees, new_employee], ignore_index=True)  
                st.success("Employee added successfully!")  
      
    st.subheader("Employees Table")  
    st.session_state.employees = edit_table(st.session_state.employees, "employees")  
    st.dataframe(st.session_state.employees)  
    st.markdown(get_csv_download_link(st.session_state.employees, "employees.csv", "Download Employees CSV"), unsafe_allow_html=True)  
    if st.button("Save Employees Data"):  
        save_table("employees", st.session_state.employees)  
  
# -------------------------------  
# 8. Module: Performance Reviews  
# -------------------------------  
elif module == "Performance Reviews":  
    st.header("Performance Reviews")  
    with st.form("review_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            review_id = st.text_input("Review ID", max_chars=6)  
            employee_id = st.text_input("Employee ID", max_chars=6)  
            review_date = st.date_input("Review Date", datetime.date.today())  
        with col2:  
            score = st.number_input("Score", min_value=0, max_value=100, step=1)  
            comments = st.text_area("Comments")  
        submitted_review = st.form_submit_button("Add Review")  
        if submitted_review:  
            if review_id == "" or not review_id.isdigit():  
                st.error("Enter a valid numeric Review ID.")  
            else:  
                new_review = pd.DataFrame({  
                    "review_id": [int(review_id)],  
                    "employee_id": [int(employee_id)],  
                    "review_date": [review_date.strftime('%Y-%m-%d')],  
                    "score": [score],  
                    "comments": [comments]  
                })  
                st.session_state.reviews = pd.concat([st.session_state.reviews, new_review], ignore_index=True)  
                st.success("Review added successfully!")  
      
    st.subheader("Reviews Table")  
    st.session_state.reviews = edit_table(st.session_state.reviews, "reviews")  
    st.dataframe(st.session_state.reviews)  
    st.markdown(get_csv_download_link(st.session_state.reviews, "reviews.csv", "Download Reviews CSV"), unsafe_allow_html=True
