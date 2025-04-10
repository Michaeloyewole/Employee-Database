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
  
# New function to search records  
def search_records(df, search_term, columns_to_search):  
    """Search for records containing the search term in specified columns"""  
    if df.empty:  
        return df  
      
    # Convert all searchable columns to string for searching  
    df_search = df.copy()  
    for col in columns_to_search:  
        if col in df_search.columns:  
            df_search[col] = df_search[col].astype(str)  
      
    # Create a mask for each column and combine with OR  
    mask = pd.Series(False, index=df.index)  
    for col in columns_to_search:  
        if col in df_search.columns:  
            mask = mask | df_search[col].str.contains(search_term, case=False, na=False)  
      
    return df[mask]  
  
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
  
# Setting up Sidebar Navigation with modules listed out  
module_options = ['Employee Management', 'Meeting Records', 'Training Completion']  
selected_module = st.sidebar.radio('Modules', module_options)  
  
# Depending on the module, load appropriate dataset and adjust interface  
if 'employees' not in st.session_state:  
    employee_columns = ['employee_id', 'first_name', 'last_name', 'department', 'position', 'hire_date']  
    st.session_state.employees = load_table('employees', employee_columns)  
  
if 'meetings' not in st.session_state:  
    meeting_columns = ['meeting_id', 'employee_id', 'meeting_date', 'meeting_type', 'notes']  
    st.session_state.meetings = load_table('meetings', meeting_columns)  
  
if 'training' not in st.session_state:  
    training_columns = ['training_id', 'employee_id', 'course_name', 'start_date', 'end_date', 'status']  
    st.session_state.training = load_table('training', training_columns)  
  
if selected_module == 'Employee Management':  
    st.header('Employee Management')  
      
    # Search functionality  
    search_term = st.text_input('Search Records')  
    if search_term:  
        df_search = search_records(st.session_state.employees, search_term, ['employee_id', 'first_name', 'last_name', 'department', 'position'])  
        st.dataframe(df_search)  
    else:  
        st.dataframe(st.session_state.employees)  
  
    # Form for Adding/Editing Employee  
    with st.form(key='employee_form', clear_on_submit=True):  
        emp_id = st.text_input('Employee ID')  
        # Auto-populate details if employee exists  
        existing_details = auto_populate_employee_details(emp_id)  
        if existing_details:  
            st.info(f"Employee exists: {get_employee_display_name(emp_id)}")  
            first_name = st.text_input('First Name', value=existing_details['first_name'])  
            last_name = st.text_input('Last Name', value=existing_details['last_name'])  
            department = st.text_input('Department', value=existing_details['department'])  
            position = st.text_input('Position', value=existing_details['position'])  
            hire_date = st.text_input('Hire Date', value=existing_details['hire_date'])  
        else:  
            first_name = st.text_input('First Name')  
            last_name = st.text_input('Last Name')  
            department = st.text_input('Department')  
            position = st.text_input('Position')  
            hire_date = st.text_input('Hire Date')  
              
        submit_button = st.form_submit_button(label='Add / Update Employee')  
  
    if submit_button:  
        # Check if employee exists and update, otherwise add new record  
        if existing_details:  
            st.session_state.employees.loc[st.session_state.employees['employee_id'] == emp_id, ['first_name', 'last_name', 'department', 'position', 'hire_date']] = [first_name, last_name, department, position, hire_date]  
            st.success('Employee record updated.')  
        else:  
            new_record = pd.DataFrame({  
                'employee_id': [emp_id],  
                'first_name': [first_name],  
                'last_name': [last_name],  
                'department': [department],  
                'position': [position],  
                'hire_date': [hire_date]  
            })  
            st.session_state.employees = pd.concat([st.session_state.employees, new_record], ignore_index=True)  
            st.success('New employee record added.')  
        save_table('employees', st.session_state.employees)  
  
    # Delete functionality  
    del_id = st.text_input('Enter Employee ID to Delete')  
    if st.button('Delete Record') and del_id:  
        if not st.session_state.employees[st.session_state.employees['employee_id'] == del_id].empty:  
            st.session_state.employees = st.session_state.employees[st.session_state.employees['employee_id'] != del_id]  
            save_table('employees', st.session_state.employees)  
            st.success('Employee record deleted.')  
        else:  
            st.error('Employee ID not found.')  
  
    # Direct table editing  
    st.markdown('### Edit Employee Records')  
    try:  
        # Try using st.data_editor (newer versions)  
        edited_df = st.data_editor(st.session_state.employees, num_rows="dynamic")  
    except AttributeError:  
        # Fallback to experimental_data_editor  
        edited_df = st.experimental_data_editor(st.session_state.employees, num_rows="dynamic")  
    except Exception:  
        # Last resort fallback  
        st.warning("Direct table editing not available in this Streamlit version")  
        edited_df = st.session_state.employees  
          
    st.session_state.employees = edited_df  
    if st.button('Save Changes'):  
        save_table('employees', st.session_state.employees)  
  
elif selected_module == 'Meeting Records':  
    st.header('Meeting Records')  
      
    # Search functionality  
    search_term = st.text_input('Search Meeting Records')  
    if search_term:  
        df_search = search_records(st.session_state.meetings, search_term, ['meeting_id', 'employee_id', 'meeting_type', 'notes'])  
        st.dataframe(df_search)  
    else:  
        st.dataframe(st.session_state.meetings)  
      
    # Meeting form and other functionality would go here  
    # Similar to the employee management section  
  
elif selected_module == 'Training Completion':  
    st.header('Training Completion')  
      
    # Search functionality  
    search_term = st.text_input('Search Training Records')  
    if search_term:  
        df_search = search_records(st.session_state.training, search_term, ['training_id', 'employee_id', 'course_name', 'status'])  
        st.dataframe(df_search)  
    else:  
        st.dataframe(st.session_state.training)  
      
    # Training form and other functionality would go here  
    # Similar to the employee management section  
