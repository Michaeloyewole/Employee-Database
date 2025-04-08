import os  
import streamlit as st    
import pandas as pd    
import matplotlib.pyplot as plt    
import datetime    
import uuid    
import io    
import base64    
  
# ------------------------------------------  
# 1. Page Config & Data Directory Setup  
# ------------------------------------------  
st.set_page_config(  
    page_title="Employee Records Tool",  
    page_icon="👥",  
    layout="wide",  
    initial_sidebar_state="expanded"  
)  
  
DATA_DIR = 'data'  
if not os.path.exists(DATA_DIR):  
    os.makedirs(DATA_DIR)  
  
# ------------------------------------------  
# 2. Data Persistence Functions  
# ------------------------------------------  
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
  
# ------------------------------------------  
# 3. Initialize Tables in Session State  
# ------------------------------------------  
if 'employees' not in st.session_state:  
    st.session_state.employees = load_table('employees', [  
        'employee_id', 'first_name', 'last_name', 'employee_number',  
        'department', 'job_title', 'hire_date', 'email', 'phone',  
        'address', 'date_of_birth', 'manager_id', 'employment_status'  
    ])  
  
if 'departments' not in st.session_state:  
    st.session_state.departments = load_table('departments', [  
        'department_id', 'department_name', 'location', 'manager_id'  
    ])  
  
if 'job_titles' not in st.session_state:  
    st.session_state.job_titles = load_table('job_titles', [  
        'job_id', 'job_title', 'min_salary', 'max_salary'  
    ])  
  
# ------------------------------------------  
# 4. Sidebar Navigation & Export Options  
# ------------------------------------------  
st.sidebar.title("Navigation")  
page = st.sidebar.radio("Select Section",   
                         ["Employees", "Departments", "Job Titles", "Reports"])  
  
st.sidebar.header("Data Export")  
export_table = st.sidebar.selectbox("Select table to export",   
                                    ["Employees", "Departments", "Job Titles"])  
if st.sidebar.button("Export CSV"):  
    table_name = export_table.lower()  
    csv = getattr(st.session_state, table_name).to_csv(index=False).encode('utf-8')  
    b64 = base64.b64encode(csv).decode()  
    href = f'<a href="data:file/csv;base64,{b64}" download="{table_name}.csv">Download {export_table} CSV</a>'  
    st.sidebar.markdown(href, unsafe_allow_html=True)  
  
# ------------------------------------------  
# 5. Main Interface with Forms and Data Display  
# ------------------------------------------  
if page == "Employees":  
    st.title("Employees Table")  
    col1, col2 = st.columns([1,2])  
      
    # Left: Data Entry Form  
    with col1:  
        st.header("Add New Employee")  
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
            submitted = st.form_submit_button("Submit Employee")  
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
                st.session_state.employees = st.session_state.employees.append(new_employee, ignore_index=True)  
                st.success("New employee record added!")  
        if st.button("Save Employees Data"):  
            save_table("employees", st.session_state.employees)  
      
    # Right: Display Employees Table  
    with col2:  
        st.header("Current Employees Data")  
        st.dataframe(st.session_state.employees)  
      
elif page == "Departments":  
    st.title("Departments Table")  
    col1, col2 = st.columns([1, 2])  
      
    # Left: Data Entry Form  
    with col1:  
        st.header("Add New Department")  
        with st.form("department_form", clear_on_submit=True):  
            department_name = st.text_input("Department Name")  
            location = st.text_input("Location")  
            manager_id = st.text_input("Manager ID")  
            submitted = st.form_submit_button("Submit Department")  
            if submitted:  
                new_department = {  
                    'department_id': str(uuid.uuid4()),  
                    'department_name': department_name,  
                    'location': location,  
                    'manager_id': manager_id  
                }  
                st.session_state.departments = st.session_state.departments.append(new_department, ignore_index=True)  
                st.success("New department record added!")  
        if st.button("Save Departments Data"):  
            save_table("departments", st.session_state.departments)  
      
    # Right: Display Departments Table  
    with col2:  
        st.header("Current Departments Data")  
        st.dataframe(st.session_state.departments)  
      
elif page == "Job Titles":  
    st.title("Job Titles Table")  
    col1, col2 = st.columns([1, 2])  
      
    # Left: Data Entry Form  
    with col1:  
        st.header("Add New Job Title")  
        with st.form("job_titles_form", clear_on_submit=True):  
            job_title = st.text_input("Job Title")  
            min_salary = st.number_input("Minimum Salary", value=0)  
            max_salary = st.number_input("Maximum Salary", value=0)  
            submitted = st.form_submit_button("Submit Job Title")  
            if submitted:  
                new_job = {  
                    'job_id': str(uuid.uuid4()),  
                    'job_title': job_title,  
                    'min_salary': min_salary,  
                    'max_salary': max_salary  
                }  
                st.session_state.job_titles = st.session_state.job_titles.append(new_job, ignore_index=True)  
                st.success("New job title record added!")  
        if st.button("Save Job Titles Data"):  
            save_table("job_titles", st.session_state.job_titles)  
      
    # Right: Display Job Titles Table  
    with col2:  
        st.header("Current Job Titles Data")  
        st.dataframe(st.session_state.job_titles)  
      
elif page == "Reports":  
    st.title("Reports")  
    report_option = st.selectbox("Select report", ["Department Distribution", "Employment Status Distribution"])  
      
    if report_option == "Department Distribution":  
        if not st.session_state.employees.empty:  
            # Compute counts  
            dept_count = st.session_state.employees['department'].value_counts().reset_index()  
            dept_count.columns = ['Department', 'Count']  
            st.subheader("Employees by Department")  
            st.table(dept_count)  
              
            # Bar Chart  
            fig, ax = plt.subplots(figsize=(12, 8))  
            colors = ['#2563EB', '#24EB84', '#B2EB24', '#EB3424', '#D324EB']  
            ax.bar(dept_count['Department'], dept_count['Count'], color=colors[:len(dept_count)])  
            ax.set_title("Department Distribution", fontsize=20, pad=15, color="#171717")  
            ax.set_xlabel("Department", fontsize=16, labelpad=10, color="#171717")  
            ax.set_ylabel("Number of Employees", fontsize=16, labelpad=10, color="#171717")  
            ax.spines['top'].set_visible(False)  
            ax.spines['right'].set_visible(False)  
            ax.spines['left'].set_color('#E5E7EB')  
            ax.spines['bottom'].set_color('#E5E7EB')  
            ax.tick_params(axis='x', labelsize=14, colors='#171717')  
            ax.tick_params(axis='y', labelsize=14, colors='#171717')  
            ax.set_axisbelow(True)  
            ax.yaxis.grid(True, color='#F3F4F6')  
            plt.tight_layout()  
            st.pyplot(fig)  
        else:  
            st.info("No employee data available for reporting.")  
      
    elif report_option == "Employment Status Distribution":  
        if not st.session_state.employees.empty:  
            status_counts = st.session_state.employees['employment_status'].value_counts().reset_index()  
            status_counts.columns = ['Status', 'Count']  
            st.subheader("Employees by Employment Status")  
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
