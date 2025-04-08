import os  
import streamlit as st    
import pandas as pd    
import matplotlib.pyplot as plt    
import datetime    
import uuid    
import io    
import base64    
  
# Set page configuration FIRST to avoid StreamlitSetPageConfigMustBeFirstCommandError  
st.set_page_config(  
    page_title="Employee Records Tool",  
    page_icon="👥",  
    layout="wide",  
    initial_sidebar_state="expanded"  
)  
  
# Define a directory for persistent CSV storage    
DATA_DIR = 'data'    
if not os.path.exists(DATA_DIR):    
    os.makedirs(DATA_DIR)    
  
# Function to load employee data from CSV    
def load_employees():    
    employees_path = os.path.join(DATA_DIR, 'employees.csv')    
    if os.path.exists(employees_path):    
        return pd.read_csv(employees_path)    
    else:    
        # Create an empty DataFrame with proper columns    
        return pd.DataFrame({    
            'employee_id': [],    
            'first_name': [],    
            'last_name': [],    
            'employee_number': [],    
            'department': [],    
            'job_title': [],    
            'hire_date': [],    
            'email': [],    
            'phone': [],    
            'address': [],    
            'date_of_birth': [],    
            'manager_id': [],    
            'employment_status': []    
        })    
  
# Function to save the employee DataFrame to CSV    
def save_employees(df):    
    employees_path = os.path.join(DATA_DIR, 'employees.csv')    
    df.to_csv(employees_path, index=False)    
    st.success("Data saved successfully!")    
  
# Load employees data into session state on app startup    
if 'employees' not in st.session_state:    
    st.session_state.employees = load_employees()    
  
# ---- Interface Layout ----  
st.title("Employee Records Tool")  
st.header("Add New Employee")  
  
# Left column for New Employee Form; Right column for reporting and extra features  
col1, col2 = st.columns([1, 1])  
with col1:  
    st.subheader("New Employee Entry")  
    with st.form("employee_form", clear_on_submit=True):  
        first_name = st.text_input("First Name")  
        last_name = st.text_input("Last Name")  
        employee_number = st.text_input("Employee Number")  
        department = st.text_input("Department")  
        job_title = st.text_input("Job Title")  
        hire_date = st.date_input("Hire Date", datetime.date.today())  
        email = st.text_input("Email")  
        phone = st.text_input("Phone")  
        address = st.text_area("Address")  
        date_of_birth = st.date_input("Date of Birth", datetime.date(1990, 1, 1))  
        manager_id = st.text_input("Manager ID")  
        employment_status = st.selectbox("Employment Status", ["Active", "Inactive"])  
          
        submitted = st.form_submit_button("Submit New Record")  
        if submitted:  
            new_employee = {  
                'employee_id': str(uuid.uuid4()),  
                'first_name': first_name,  
                'last_name': last_name,  
                'employee_number': employee_number,  
                'department': department,  
                'job_title': job_title,  
                'hire_date': hire_date,  
                'email': email,  
                'phone': phone,  
                'address': address,  
                'date_of_birth': date_of_birth,  
                'manager_id': manager_id,  
                'employment_status': employment_status  
            }  
            st.session_state.employees = pd.concat(  
                [st.session_state.employees, pd.DataFrame([new_employee])],  
                ignore_index=True  
            )  
            st.success("New employee record added!")  
  
    # Save Data Button  
    if st.button("Save All Data"):  
        save_employees(st.session_state.employees)  
  
with col2:  
    st.subheader("Current Employee Records")  
    st.dataframe(st.session_state.employees)  
      
    st.markdown("---")  
    st.subheader("Reporting & Visualizations")  
    report_type = st.selectbox("Select Report Type", ["Department Distribution", "Employment Status Distribution"])  
      
    if report_type == "Department Distribution":  
        if not st.session_state.employees.empty:  
            dept_counts = st.session_state.employees['department'].value_counts().reset_index()  
            dept_counts.columns = ['Department', 'Count']  
            st.table(dept_counts)  
              
            fig, ax = plt.subplots(figsize=(12, 8))  
            colors = ['#2563EB', '#24EB84', '#B2EB24', '#EB3424', '#D324EB']  
            ax.bar(dept_counts['Department'], dept_counts['Count'], color=colors[:len(dept_counts)])  
              
            ax.set_title("Employees by Department", fontsize=20, pad=15, color="#171717")  
            ax.set_xlabel("Department", fontsize=16, labelpad=10, color="#171717")  
            ax.set_ylabel("Count", fontsize=16, labelpad=10, color="#171717")  
            ax.tick_params(axis='x', labelsize=14, colors="#171717")  
            ax.tick_params(axis='y', labelsize=14, colors="#171717")  
            ax.spines['left'].set_color('#E5E7EB')  
            ax.spines['bottom'].set_color('#E5E7EB')  
            ax.set_axisbelow(True)  
            ax.yaxis.grid(True, color='#F3F4F6')  
            plt.tight_layout()  
            st.pyplot(fig)  
        else:  
            st.info("No employee data available for reporting.")  
      
    elif report_type == "Employment Status Distribution":  
        if not st.session_state.employees.empty:  
            status_counts = st.session_state.employees['employment_status'].value_counts().reset_index()  
            status_counts.columns = ['Status', 'Count']  
            st.table(status_counts)  
              
            fig, ax = plt.subplots(figsize=(12, 8))  
            colors = ['#2563EB', '#24EB84', '#EB3424']  
            wedges, texts, autotexts = ax.pie(  
                status_counts['Count'],    
                labels=status_counts['Status'],    
                autopct='%1.1f%%',    
                startangle=90,    
                colors=colors[:len(status_counts)]  
            )  
              
            ax.set_title("Employment Status Distribution", fontsize=20, pad=15, color="#171717")  
            for text in texts:  
                text.set_color('#171717')  
                text.set_fontsize(14)  
            for autotext in autotexts:  
                autotext.set_color('white')  
                autotext.set_fontsize(14)  
            ax.axis('equal')  
            st.pyplot(fig)  
        else:  
            st.info("No employee data available for reporting.")  
  
# Optionally add Export functionality in a sidebar    
st.sidebar.header("Data Export")  
if st.sidebar.button("Export CSV"):  
    csv = st.session_state.employees.to_csv(index=False).encode('utf-8')  
    b64 = base64.b64encode(csv).decode()  
    href = f'<a href="data:file/csv;base64,{b64}" download="employees.csv">Download CSV File</a>'  
    st.sidebar.markdown(href, unsafe_allow_html=True)  
