import os
import streamlit as st  
import pandas as pd  
import matplotlib.pyplot as plt  
import datetime  
import uuid  
import io  
import base64  
  
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
  
# Load employees data into session state on startup  
if 'employees' not in st.session_state:  
    st.session_state.employees = load_employees()  
  
st.title("Employee Records Tool")  
st.header("Add New Employee")  
  
# Create a form for entering a new employee  
with st.form("employee_form", clear_on_submit=True):  
    first_name = st.text_input("First Name")  
    last_name = st.text_input("Last Name")  
    employee_number = st.text_input("Employee Number")  
    department = st.text_input("Department")  
    job_title = st.text_input("Job Title")  
    hire_date = st.date_input("Hire Date")  
    email = st.text_input("Email")  
    phone = st.text_input("Phone")  
    address = st.text_area("Address")  
    date_of_birth = st.date_input("Date of Birth")  
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
          
        # Append new record to the session state DataFrame  
        st.session_state.employees = pd.concat(  
            [st.session_state.employees, pd.DataFrame([new_employee])],  
            ignore_index=True  
        )  
        st.success("New employee record added!")  
          
# Provide a button to save all current data to CSV  
if st.button("Save All Data"):  
    save_employees(st.session_state.employees)  
  
st.header("Current Employee Records")  
st.dataframe(st.session_state.employees)    
# Set page configuration  
st.set_page_config(  
    page_title="Employee Records Tool",  
    page_icon="👥",  
    layout="wide"  
)  
  
# Initialize session state for data storage  
if 'employees' not in st.session_state:  
    st.session_state.employees = pd.DataFrame({  
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
  
if 'meetings' not in st.session_state:  
    st.session_state.meetings = pd.DataFrame({  
        'meeting_id': [],  
        'employee_id': [],  
        'manager_id': [],  
        'meeting_date': [],  
        'meeting_time': [],  
        'topics_discussed': [],  
        'action_items': [],  
        'notes': [],  
        'next_meeting_date': []  
    })  
  
if 'disciplinary' not in st.session_state:  
    st.session_state.disciplinary = pd.DataFrame({  
        'disciplinary_id': [],  
        'employee_id': [],  
        'date': [],  
        'type': [],  
        'reason': [],  
        'description': [],  
        'documentation': [],  
        'issued_by': []  
    })  
  
if 'performance' not in st.session_state:  
    st.session_state.performance = pd.DataFrame({  
        'review_id': [],  
        'employee_id': [],  
        'review_date': [],  
        'reviewer_id': [],  
        'performance_rating': [],  
        'review_comments': [],  
        'goals_set': [],  
        'areas_for_improvement': []  
    })  
  
if 'training' not in st.session_state:  
    st.session_state.training = pd.DataFrame({  
        'training_id': [],  
        'employee_id': [],  
        'training_name': [],  
        'training_date': [],  
        'provider': [],  
        'completion_status': [],  
        'certification_expiry': []  
    })  
  
# Add sample data if needed (for testing)  
if 'initialized' not in st.session_state:  
    # Add sample employees  
    st.session_state.employees = pd.DataFrame({  
        'employee_id': [1, 2, 3],  
        'first_name': ['John', 'Jane', 'Michael'],  
        'last_name': ['Doe', 'Smith', 'Johnson'],  
        'employee_number': ['E001', 'E002', 'E003'],  
        'department': ['IT', 'HR', 'Finance'],  
        'job_title': ['Developer', 'HR Manager', 'Accountant'],  
        'hire_date': ['2020-01-15', '2019-05-20', '2021-03-10'],  
        'email': ['john@example.com', 'jane@example.com', 'michael@example.com'],  
        'phone': ['555-1234', '555-5678', '555-9012'],  
        'address': ['123 Main St', '456 Oak Ave', '789 Pine Rd'],  
        'date_of_birth': ['1985-06-15', '1990-02-28', '1988-11-12'],  
        'manager_id': [None, 1, 2],  
        'employment_status': ['Active', 'Active', 'Probation']  
    })  
      
    # Add sample training records  
    st.session_state.training = pd.DataFrame({  
        'training_id': [1, 2, 3],  
        'employee_id': [1, 2, 3],  
        'training_name': ['Python Development', 'HR Compliance', 'Accounting Basics'],  
        'training_date': ['2022-03-15', '2022-02-10', '2022-04-05'],  
        'provider': ['Tech Academy', 'HR Institute', 'Finance School'],  
        'completion_status': ['Completed', 'In Progress', 'Not Started'],  
        'certification_expiry': ['2024-03-15', None, None]  
    })  
      
    st.session_state.initialized = True  
  
# Function to download dataframe as CSV  
def download_csv(df, filename):  
    csv = df.to_csv(index=False)  
    b64 = base64.b64encode(csv.encode()).decode()  
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download {filename} CSV</a>'  
    return href  
  
# Main app title  
st.title("Employee Records Tool")  
  
# Sidebar navigation  
st.sidebar.title("Navigation")  
page = st.sidebar.radio("Go to", ["Dashboard", "Employees", "Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records", "Reports"])  
  
# Dashboard page  
if page == "Dashboard":  
    st.header("Dashboard")  
      
    col1, col2 = st.columns(2)  
      
    with col1:  
        st.subheader("Employee Statistics")  
        st.info(f"Total Employees: {len(st.session_state.employees)}")  
          
        if not st.session_state.employees.empty:  
            status_counts = st.session_state.employees['employment_status'].value_counts()  
            st.write("Employment Status Breakdown:")  
            st.write(status_counts)  
      
    with col2:  
        st.subheader("Training Statistics")  
        if not st.session_state.training.empty:  
            training_status = st.session_state.training['completion_status'].value_counts()  
            st.write("Training Completion Status:")  
            st.write(training_status)  
      
    st.subheader("Recent Activities")  
    st.info("This section would typically show recent changes to the database.")  
  
# Employees page  
elif page == "Employees":  
    st.header("Employees")  
      
    tab1, tab2, tab3 = st.tabs(["View Employees", "Add Employee", "Search Employees"])  
      
    with tab1:  
        st.subheader("Employee Records")  
        if not st.session_state.employees.empty:  
            st.dataframe(st.session_state.employees)  
            st.markdown(download_csv(st.session_state.employees, "employees"), unsafe_allow_html=True)  
        else:  
            st.info("No employee records found.")  
      
    with tab2:  
        st.subheader("Add New Employee")  
          
        with st.form("employee_form"):  
            col1, col2 = st.columns(2)  
              
            with col1:  
                first_name = st.text_input("First Name")  
                last_name = st.text_input("Last Name")  
                employee_number = st.text_input("Employee Number (e.g., E004)")  
                department = st.selectbox("Department", ["IT", "HR", "Finance", "Marketing", "Operations", "Sales", "Other"])  
                job_title = st.text_input("Job Title")  
                hire_date = st.date_input("Hire Date", datetime.datetime.now())  
              
            with col2:  
                email = st.text_input("Email")  
                phone = st.text_input("Phone")  
                address = st.text_input("Address")  
                date_of_birth = st.date_input("Date of Birth", datetime.datetime.now() - datetime.timedelta(days=365*30))  
                  
                # Get existing employee IDs for manager selection  
                if not st.session_state.employees.empty:  
                    manager_options = st.session_state.employees[['employee_id', 'first_name', 'last_name']].copy()  
                    manager_options['full_name'] = manager_options['first_name'] + " " + manager_options['last_name']  
                    manager_dict = dict(zip(manager_options['employee_id'], manager_options['full_name']))  
                    manager_dict[None] = "None (Top Manager)"  
                    manager_id = st.selectbox("Manager", options=list(manager_dict.keys()), format_func=lambda x: manager_dict[x])  
                else:  
                    manager_id = None  
                    st.info("No existing employees to select as manager.")  
                  
                employment_status = st.selectbox("Employment Status", ["Active", "Probation", "Inactive", "Terminated"])  
              
            submit_button = st.form_submit_button("Add Employee")  
              
            if submit_button:  
                if not first_name or not last_name or not employee_number:  
                    st.error("First name, last name, and employee number are required.")  
                else:  
                    # Check if employee number already exists  
                    if not st.session_state.employees.empty and employee_number in st.session_state.employees['employee_number'].values:  
                        st.error(f"Employee number {employee_number} already exists.")  
                    else:  
                        # Generate new employee ID  
                        new_id = 1 if st.session_state.employees.empty else st.session_state.employees['employee_id'].max() + 1  
                          
                        # Create new employee record  
                        new_employee = pd.DataFrame({  
                            'employee_id': [new_id],  
                            'first_name': [first_name],  
                            'last_name': [last_name],  
                            'employee_number': [employee_number],  
                            'department': [department],  
                            'job_title': [job_title],  
                            'hire_date': [hire_date.strftime('%Y-%m-%d')],  
                            'email': [email],  
                            'phone': [phone],  
                            'address': [address],  
                            'date_of_birth': [date_of_birth.strftime('%Y-%m-%d')],  
                            'manager_id': [manager_id],  
                            'employment_status': [employment_status]  
                        })  
                          
                        # Add to employees dataframe  
                        st.session_state.employees = pd.concat([st.session_state.employees, new_employee], ignore_index=True)  
                        st.success(f"Employee {first_name} {last_name} added successfully with ID {new_id}.")  
      
    with tab3:  
        st.subheader("Search Employees")  
        search_term = st.text_input("Enter search term (name, department, job title, etc.)")  
          
        if search_term and not st.session_state.employees.empty:  
            # Convert all columns to string for searching  
            df_str = st.session_state.employees.astype(str)  
              
            # Search across all columns  
            mask = df_str.apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)  
            search_results = st.session_state.employees[mask]  
              
            if not search_results.empty:  
                st.write(f"Found {len(search_results)} matching records:")  
                st.dataframe(search_results)  
            else:  
                st.info(f"No records found matching '{search_term}'.")  
  
# Meetings page  
elif page == "Meetings":  
    st.header("One-on-One Meetings")  
      
    tab1, tab2, tab3 = st.tabs(["View Meetings", "Add Meeting", "Search Meetings"])  
      
    with tab1:  
        st.subheader("Meeting Records")  
        if not st.session_state.meetings.empty:  
            st.dataframe(st.session_state.meetings)  
            st.markdown(download_csv(st.session_state.meetings, "meetings"), unsafe_allow_html=True)  
        else:  
            st.info("No meeting records found.")  
      
    with tab2:  
        st.subheader("Add New Meeting")  
          
        with st.form("meeting_form"):  
            # Employee selection  
            if not st.session_state.employees.empty:  
                employee_options = st.session_state.employees[['employee_id', 'first_name', 'last_name']].copy()  
                employee_options['full_name'] = employee_options['first_name'] + " " + employee_options['last_name']  
                employee_dict = dict(zip(employee_options['employee_id'], employee_options['full_name']))  
                  
                employee_id = st.selectbox("Employee", options=list(employee_dict.keys()), format_func=lambda x: employee_dict[x])  
                manager_id = st.selectbox("Manager", options=list(employee_dict.keys()), format_func=lambda x: employee_dict[x])  
            else:  
                st.error("No employees in the system. Please add employees first.")  
                employee_id = None  
                manager_id = None  
              
            meeting_date = st.date_input("Meeting Date", datetime.datetime.now())  
            meeting_time = st.time_input("Meeting Time", datetime.time(9, 0))  
            topics_discussed = st.text_area("Topics Discussed")  
            action_items = st.text_area("Action Items")  
            notes = st.text_area("Notes")  
            next_meeting_date = st.date_input("Next Meeting Date (Optional)", datetime.datetime.now() + datetime.timedelta(days=30))  
              
            submit_button = st.form_submit_button("Add Meeting")  
              
            if submit_button and employee_id is not None and manager_id is not None:  
                # Generate new meeting ID  
                new_id = 1 if st.session_state.meetings.empty else st.session_state.meetings['meeting_id'].max() + 1  
                  
                # Create new meeting record  
                new_meeting = pd.DataFrame({  
                    'meeting_id': [new_id],  
                    'employee_id': [employee_id],  
                    'manager_id': [manager_id],  
                    'meeting_date': [meeting_date.strftime('%Y-%m-%d')],  
                    'meeting_time': [meeting_time.strftime('%H:%M')],  
                    'topics_discussed': [topics_discussed],  
                    'action_items': [action_items],  
                    'notes': [notes],  
                    'next_meeting_date': [next_meeting_date.strftime('%Y-%m-%d')]  
                })  
                  
                # Add to meetings dataframe  
                st.session_state.meetings = pd.concat([st.session_state.meetings, new_meeting], ignore_index=True)  
                st.success(f"Meeting added successfully with ID {new_id}.")  
      
    with tab3:  
        st.subheader("Search Meetings")  
        search_term = st.text_input("Enter search term (employee name, topics, etc.)")  
          
        if search_term and not st.session_state.meetings.empty:  
            # Convert all columns to string for searching  
            df_str = st.session_state.meetings.astype(str)  
              
            # Search across all columns  
            mask = df_str.apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)  
            search_results = st.session_state.meetings[mask]  
              
            if not search_results.empty:  
                st.write(f"Found {len(search_results)} matching records:")  
                st.dataframe(search_results)  
            else:  
                st.info(f"No records found matching '{search_term}'.")  
  
# Disciplinary Actions page  
elif page == "Disciplinary Actions":  
    st.header("Disciplinary Actions")  
      
    tab1, tab2, tab3 = st.tabs(["View Actions", "Add Action", "Search Actions"])  
      
    with tab1:  
        st.subheader("Disciplinary Action Records")  
        if not st.session_state.disciplinary.empty:  
            st.dataframe(st.session_state.disciplinary)  
            st.markdown(download_csv(st.session_state.disciplinary, "disciplinary_actions"), unsafe_allow_html=True)  
        else:  
            st.info("No disciplinary action records found.")  
      
    with tab2:  
        st.subheader("Add New Disciplinary Action")  
          
        with st.form("disciplinary_form"):  
            # Employee selection  
            if not st.session_state.employees.empty:  
                employee_options = st.session_state.employees[['employee_id', 'first_name', 'last_name']].copy()  
                employee_options['full_name'] = employee_options['first_name'] + " " + employee_options['last_name']  
                employee_dict = dict(zip(employee_options['employee_id'], employee_options['full_name']))  
                  
                employee_id = st.selectbox("Employee", options=list(employee_dict.keys()), format_func=lambda x: employee_dict[x])  
                issued_by = st.selectbox("Issued By", options=list(employee_dict.keys()), format_func=lambda x: employee_dict[x])  
            else:  
                st.error("No employees in the system. Please add employees first.")  
                employee_id = None  
                issued_by = None  
              
            action_date = st.date_input("Date", datetime.datetime.now())  
            action_type = st.selectbox("Type", ["Verbal Warning", "Written Warning", "Suspension", "Termination"])  
            reason = st.text_input("Reason")  
            description = st.text_area("Description")  
            documentation = st.text_input("Documentation (file path or reference)")  
              
            submit_button = st.form_submit_button("Add Disciplinary Action")  
              
            if submit_button and employee_id is not None and issued_by is not None:  
                # Generate new disciplinary action ID  
                new_id = 1 if st.session_state.disciplinary.empty else st.session_state.disciplinary['disciplinary_id'].max() + 1  
                  
                # Create new disciplinary action record  
                new_action = pd.DataFrame({  
                    'disciplinary_id': [new_id],  
                    'employee_id': [employee_id],  
                    'date': [action_date.strftime('%Y-%m-%d')],  
                    'type': [action_type],  
                    'reason': [reason],  
                    'description': [description],  
                    'documentation': [documentation],  
                    'issued_by': [issued_by]  
                })  
                  
                # Add to disciplinary actions dataframe  
                st.session_state.disciplinary = pd.concat([st.session_state.disciplinary, new_action], ignore_index=True)  
                st.success(f"Disciplinary action added successfully with ID {new_id}.")  
      
    with tab3:  
        st.subheader("Search Disciplinary Actions")  
        search_term = st.text_input("Enter search term (employee name, type, reason, etc.)")  
          
        if search_term and not st.session_state.disciplinary.empty:  
            # Convert all columns to string for searching  
            df_str = st.session_state.disciplinary.astype(str)  
              
            # Search across all columns  
            mask = df_str.apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)  
            search_results = st.session_state.disciplinary[mask]  
              
            if not search_results.empty:  
                st.write(f"Found {len(search_results)} matching records:")  
                st.dataframe(search_results)  
            else:  
                st.info(f"No records found matching '{search_term}'.")  
  
# Performance Reviews page  
elif page == "Performance Reviews":  
    st.header("Performance Reviews")  
      
    tab1, tab2, tab3 = st.tabs(["View Reviews", "Add Review", "Search Reviews"])  
      
    with tab1:  
        st.subheader("Performance Review Records")  
        if not st.session_state.performance.empty:  
            st.dataframe(st.session_state.performance)  
            st.markdown(download_csv(st.session_state.performance, "performance_reviews"), unsafe_allow_html=True)  
        else:  
            st.info("No performance review records found.")  
      
    with tab2:  
        st.subheader("Add New Performance Review")  
          
        with st.form("review_form"):  
            # Employee selection  
            if not st.session_state.employees.empty:  
                employee_options = st.session_state.employees[['employee_id', 'first_name', 'last_name']].copy()  
                employee_options['full_name'] = employee_options['first_name'] + " " + employee_options['last_name']  
                employee_dict = dict(zip(employee_options['employee_id'], employee_options['full_name']))  
                  
                employee_id = st.selectbox("Employee", options=list(employee_dict.keys()), format_func=lambda x: employee_dict[x])  
                reviewer_id = st.selectbox("Reviewer", options=list(employee_dict.keys()), format_func=lambda x: employee_dict[x])  
            else:  
                st.error("No employees in the system. Please add employees first.")  
                employee_id = None  
                reviewer_id = None  
              
            review_date = st.date_input("Review Date", datetime.datetime.now())  
            performance_rating = st.selectbox("Performance Rating", ["Exceeds Expectations", "Meets Expectations", "Needs Improvement", "Unsatisfactory"])  
            review_comments = st.text_area("Review Comments")  
            goals_set = st.text_area("Goals Set")  
            areas_for_improvement = st.text_area("Areas for Improvement")  
              
            submit_button = st.form_submit_button("Add Performance Review")  
              
            if submit_button and employee_id is not None and reviewer_id is not None:  
                # Generate new review ID  
                new_id = 1 if st.session_state.performance.empty else st.session_state.performance['review_id'].max() + 1  
                  
                # Create new performance review record  
                new_review = pd.DataFrame({  
                    'review_id': [new_id],  
                    'employee_id': [employee_id],  
                    'review_date': [review_date.strftime('%Y-%m-%d')],  
                    'reviewer_id': [reviewer_id],  
                    'performance_rating': [performance_rating],  
                    'review_comments': [review_comments],  
                    'goals_set': [goals_set],  
                    'areas_for_improvement': [areas_for_improvement]  
                })  
                  
                # Add to performance reviews dataframe  
                st.session_state.performance = pd.concat([st.session_state.performance, new_review], ignore_index=True)  
                st.success(f"Performance review added successfully with ID {new_id}.")  
      
    with tab3:  
        st.subheader("Search Performance Reviews")  
        search_term = st.text_input("Enter search term (employee name, rating, comments, etc.)")  
          
        if search_term and not st.session_state.performance.empty:  
            # Convert all columns to string for searching  
            df_str = st.session_state.performance.astype(str)  
              
            # Search across all columns  
            mask = df_str.apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)  
            search_results = st.session_state.performance[mask]  
              
            if not search_results.empty:  
                st.write(f"Found {len(search_results)} matching records:")  
                st.dataframe(search_results)  
            else:  
                st.info(f"No records found matching '{search_term}'.")  
  
# Training Records page  
elif page == "Training Records":  
    st.header("Training Records")  
      
    tab1, tab2, tab3 = st.tabs(["View Training Records", "Add Training Record", "Search Training Records"])  
      
    with tab1:  
        st.subheader("Training Records")  
        if not st.session_state.training.empty:  
            st.dataframe(st.session_state.training)  
            st.markdown(download_csv(st.session_state.training, "training_records"), unsafe_allow_html=True)  
        else:  
            st.info("No training records found.")  
      
    with tab2:  
        st.subheader("Add New Training Record")  
          
        with st.form("training_form"):  
            # Employee selection  
            if not st.session_state.employees.empty:  
                employee_options = st.session_state.employees[['employee_id', 'first_name', 'last_name']].copy()  
                employee_options['full_name'] = employee_options['first_name'] + " " + employee_options['last_name']  
                employee_dict = dict(zip(employee_options['employee_id'], employee_options['full_name']))  
                  
                employee_id = st.selectbox("Employee", options=list(employee_dict.keys()), format_func=lambda x: employee_dict[x])  
            else:  
                st.error("No employees in the system. Please add employees first.")  
                employee_id = None  
              
            training_name = st.text_input("Training Name")  
            training_date = st.date_input("Training Date", datetime.datetime.now())  
            provider = st.text_input("Provider")  
            completion_status = st.selectbox("Completion Status", ["Not Started", "In Progress", "Completed", "Failed"])  
              
            has_expiry = st.checkbox("Has Expiration Date")  
            certification_expiry = None  
            if has_expiry:  
                certification_expiry = st.date_input("Certification Expiry Date", datetime.datetime.now() + datetime.timedelta(days=365))  
              
            submit_button = st.form_submit_button("Add Training Record")  
              
            if submit_button and employee_id is not None:  
                # Generate new training ID  
                new_id = 1 if st.session_state.training.empty else st.session_state.training['training_id'].max() + 1  
                  
                # Create new training record  
                new_training = pd.DataFrame({  
                    'training_id': [new_id],  
                    'employee_id': [employee_id],  
                    'training_name': [training_name],  
                    'training_date': [training_date.strftime('%Y-%m-%d')],  
                    'provider': [provider],  
                    'completion_status': [completion_status],  
                    'certification_expiry': [certification_expiry.strftime('%Y-%m-%d') if certification_expiry else None]  
                })  
                  
                # Add to training records dataframe  
                st.session_state.training = pd.concat([st.session_state.training, new_training], ignore_index=True)  
                st.success(f"Training record added successfully with ID {new_id}.")  
      
    with tab3:  
        st.subheader("Search Training Records")  
        search_term = st.text_input("Enter search term (employee name, training name, provider, etc.)")  
          
        if search_term and not st.session_state.training.empty:  
            # Convert all columns to string for searching  
            df_str = st.session_state.training.astype(str)  
              
            # Search across all columns  
            mask = df_str.apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)  
            search_results = st.session_state.training[mask]  
              
            if not search_results.empty:  
                st.write(f"Found {len(search_results)} matching records:")  
                st.dataframe(search_results)  
            else:  
                st.info(f"No records found matching '{search_term}'.")  
  
# Reports page  
elif page == "Reports":  
    st.header("Reports")  
      
    report_type = st.selectbox(  
        "Select Report Type",  
        ["Department Distribution", "Employment Status Distribution", "Training Completion Status"]  
    )  
      
    if report_type == "Department Distribution":  
        if not st.session_state.employees.empty:  
            # Count employees by department  
            dept_counts = st.session_state.employees['department'].value_counts().reset_index()  
            dept_counts.columns = ['Department', 'Count']  
              
            # Display as table  
            st.subheader("Employees by Department")  
            st.dataframe(dept_counts)  
              
            # Create bar chart  
            fig, ax = plt.subplots(figsize=(12, 8))  
              
            # Define colors  
            colors = ['#2563EB', '#24EB84', '#B2EB24', '#EB3424', '#D324EB']  
              
            # Create bar chart  
            bars = ax.bar(dept_counts['Department'], dept_counts['Count'], color=colors[:len(dept_counts)])  
              
            # Add data labels  
            for i, bar in enumerate(bars):  
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,   
                        str(dept_counts['Count'].iloc[i]),  
                        ha='center', fontsize=14, color='#171717')  
              
            # Customize appearance  
            ax.set_title("Employee Distribution by Department", fontsize=20, pad=15, color="#171717")  
            ax.set_xlabel("Department", fontsize=16, labelpad=10, color="#171717")  
            ax.set_ylabel("Number of Employees", fontsize=16, labelpad=10, color="#171717")  
              
            # Style the axes  
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
      
    elif report_type == "Employment Status Distribution":  
        if not st.session_state.employees.empty:  
            # Count employees by status  
            status_counts = st.session_state.employees['employment_status'].value_counts().reset_index()  
            status_counts.columns = ['Status', 'Count']  
              
            # Display as table  
            st.subheader("Employees by Employment Status")  
            st.dataframe(status_counts)  
              
            # Create pie chart  
            fig, ax = plt.subplots(figsize=(12, 8))  
              
            # Custom colors  
            colors = ['#2563EB', '#24EB84', '#EB3424']  
              
            # Create pie chart  
            wedges, texts, autotexts = ax.pie(  
                status_counts['Count'],   
                labels=status_counts['Status'],  
                autopct='%1.1f%%',  
                startangle=90,  
                colors=colors[:len(status_counts)]  
            )  
              
            # Customize appearance  
            ax.set_title("Employment Status Distribution", fontsize=20, pad=15, color="#171717")  
              
            # Style the text elements  
            for text in texts:  
                text.set_color('#171717')  
                text.set_fontsize(14)  
              
            for autotext in autotexts:  
                autotext.set_color('white')  
                autotext.set_fontsize(14)  
                  
            # Equal aspect ratio ensures that pie is drawn as a circle  
            ax.axis('equal')  
              
            st.pyplot()
