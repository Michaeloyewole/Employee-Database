import streamlit as st  
import pandas as pd  
import matplotlib.pyplot as plt  
import datetime  
import uuid  
import io  
import base64  
  
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
  
# Sample data for testing (optional)  
if 'data_initialized' not in st.session_state:  
    # Add sample employees  
    st.session_state.employees = pd.DataFrame({  
        'employee_id': [1, 2, 3],  
        'first_name': ['John', 'Jane', 'Michael'],  
        'last_name': ['Doe', 'Smith', 'Johnson'],  
        'employee_number': ['E001', 'E002', 'E003'],  
        'department': ['IT', 'HR', 'Finance'],  
        'job_title': ['Developer', 'HR Manager', 'Accountant'],  
        'hire_date': ['2022-01-15', '2021-05-20', '2023-02-10'],  
        'email': ['john.doe@example.com', 'jane.smith@example.com', 'michael.j@example.com'],  
        'phone': ['555-1234', '555-5678', '555-9012'],  
        'address': ['123 Main St', '456 Oak Ave', '789 Pine Rd'],  
        'date_of_birth': ['1990-05-15', '1985-11-30', '1992-08-22'],  
        'manager_id': [None, 1, 1],  
        'employment_status': ['Active', 'Active', 'Probation']  
    })  
      
    # Add sample training records  
    st.session_state.training = pd.DataFrame({  
        'training_id': [1, 2, 3],  
        'employee_id': [1, 1, 2],  
        'training_name': ['Python Advanced', 'Project Management', 'HR Compliance'],  
        'training_date': ['2023-03-15', '2023-05-20', '2023-04-10'],  
        'provider': ['Tech Academy', 'PMI', 'HR Institute'],  
        'completion_status': ['Completed', 'In Progress', 'Completed'],  
        'certification_expiry': ['2025-03-15', None, '2024-04-10']  
    })  
      
    # Mark as initialized  
    st.session_state.data_initialized = True  
  
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
page = st.sidebar.radio("Go to", ["View Records", "Add Records", "Search", "Reports"])  
  
# View Records Page  
if page == "View Records":  
    st.header("View Records")  
      
    record_type = st.selectbox(  
        "Select record type to view:",  
        ["Employees", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records"]  
    )  
      
    if record_type == "Employees":  
        if not st.session_state.employees.empty:  
            st.dataframe(st.session_state.employees)  
            st.markdown(download_csv(st.session_state.employees, "employees"), unsafe_allow_html=True)  
        else:  
            st.info("No employee records found.")  
              
    elif record_type == "One-on-One Meetings":  
        if not st.session_state.meetings.empty:  
            st.dataframe(st.session_state.meetings)  
            st.markdown(download_csv(st.session_state.meetings, "meetings"), unsafe_allow_html=True)  
        else:  
            st.info("No meeting records found.")  
              
    elif record_type == "Disciplinary Actions":  
        if not st.session_state.disciplinary.empty:  
            st.dataframe(st.session_state.disciplinary)  
            st.markdown(download_csv(st.session_state.disciplinary, "disciplinary_actions"), unsafe_allow_html=True)  
        else:  
            st.info("No disciplinary records found.")  
              
    elif record_type == "Performance Reviews":  
        if not st.session_state.performance.empty:  
            st.dataframe(st.session_state.performance)  
            st.markdown(download_csv(st.session_state.performance, "performance_reviews"), unsafe_allow_html=True)  
        else:  
            st.info("No performance review records found.")  
              
    elif record_type == "Training Records":  
        if not st.session_state.training.empty:  
            st.dataframe(st.session_state.training)  
            st.markdown(download_csv(st.session_state.training, "training_records"), unsafe_allow_html=True)  
        else:  
            st.info("No training records found.")  
  
# Add Records Page  
elif page == "Add Records":  
    st.header("Add New Records")  
      
    record_type = st.selectbox(  
        "Select record type to add:",  
        ["Employee", "One-on-One Meeting", "Disciplinary Action", "Performance Review", "Training Record"]  
    )  
      
    if record_type == "Employee":  
        with st.form("employee_form"):  
            st.subheader("Add New Employee")  
              
            col1, col2 = st.columns(2)  
              
            with col1:  
                first_name = st.text_input("First Name")  
                last_name = st.text_input("Last Name")  
                employee_number = st.text_input("Employee Number (e.g., E001)")  
                department = st.selectbox("Department", ["IT", "HR", "Finance", "Marketing", "Operations", "Sales", "Other"])  
                job_title = st.text_input("Job Title")  
                hire_date = st.date_input("Hire Date", datetime.datetime.now())  
              
            with col2:  
                email = st.text_input("Email")  
                phone = st.text_input("Phone")  
                address = st.text_area("Address")  
                date_of_birth = st.date_input("Date of Birth", datetime.datetime.now() - datetime.timedelta(days=365*30))  
                  
                # Get existing employee IDs for manager selection  
                if not st.session_state.employees.empty:  
                    manager_options = st.session_state.employees.apply(  
                        lambda x: f"{x['employee_id']} - {x['first_name']} {x['last_name']}",   
                        axis=1  
                    ).tolist()  
                    manager_options = ["None"] + manager_options  
                    manager_selection = st.selectbox("Manager", manager_options)  
                      
                    if manager_selection == "None":  
                        manager_id = None  
                    else:  
                        manager_id = int(manager_selection.split(" - ")[0])  
                else:  
                    manager_id = None  
                    st.info("No existing employees to select as manager.")  
                  
                employment_status = st.selectbox("Employment Status", ["Active", "Probation", "Terminated", "On Leave"])  
              
            submit_button = st.form_submit_button("Add Employee")  
              
            if submit_button:  
                # Generate new employee ID (simple increment)  
                if st.session_state.employees.empty:  
                    new_id = 1  
                else:  
                    new_id = st.session_state.employees['employee_id'].max() + 1  
                  
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
                st.success(f"Employee {first_name} {last_name} added successfully!")  
      
    elif record_type == "One-on-One Meeting":  
        with st.form("meeting_form"):  
            st.subheader("Add One-on-One Meeting")  
              
            # Check if we have employees  
            if st.session_state.employees.empty:  
                st.warning("No employees in the system. Please add employees first.")  
                submit_disabled = True  
            else:  
                submit_disabled = False  
                  
                # Get employee options  
                employee_options = st.session_state.employees.apply(  
                    lambda x: f"{x['employee_id']} - {x['first_name']} {x['last_name']}",   
                    axis=1  
                ).tolist()  
                  
                employee_selection = st.selectbox("Employee", employee_options)  
                employee_id = int(employee_selection.split(" - ")[0])  
                  
                manager_options = st.session_state.employees.apply(  
                    lambda x: f"{x['employee_id']} - {x['first_name']} {x['last_name']}",   
                    axis=1  
                ).tolist()  
                  
                manager_selection = st.selectbox("Manager", manager_options)  
                manager_id = int(manager_selection.split(" - ")[0])  
                  
                meeting_date = st.date_input("Meeting Date", datetime.datetime.now())  
                meeting_time = st.time_input("Meeting Time", datetime.time(9, 0))  
                  
                topics_discussed = st.text_area("Topics Discussed")  
                action_items = st.text_area("Action Items")  
                notes = st.text_area("Notes")  
                  
                has_next_meeting = st.checkbox("Schedule Next Meeting")  
                if has_next_meeting:  
                    next_meeting_date = st.date_input("Next Meeting Date",   
                                                     datetime.datetime.now() + datetime.timedelta(days=30))  
                    next_meeting_date_str = next_meeting_date.strftime('%Y-%m-%d')  
                else:  
                    next_meeting_date_str = None  
              
            submit_button = st.form_submit_button("Add Meeting", disabled=submit_disabled)  
              
            if submit_button:  
                # Generate new meeting ID  
                if st.session_state.meetings.empty:  
                    new_id = 1  
                else:  
                    new_id = st.session_state.meetings['meeting_id'].max() + 1  
                  
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
                    'next_meeting_date': [next_meeting_date_str]  
                })  
                  
                # Add to meetings dataframe  
                st.session_state.meetings = pd.concat([st.session_state.meetings, new_meeting], ignore_index=True)  
                st.success("Meeting record added successfully!")  
      
    elif record_type == "Disciplinary Action":  
        with st.form("disciplinary_form"):  
            st.subheader("Add Disciplinary Action")  
              
            # Check if we have employees  
            if st.session_state.employees.empty:  
                st.warning("No employees in the system. Please add employees first.")  
                submit_disabled = True  
            else:  
                submit_disabled = False  
                  
                # Get employee options  
                employee_options = st.session_state.employees.apply(  
                    lambda x: f"{x['employee_id']} - {x['first_name']} {x['last_name']}",   
                    axis=1  
                ).tolist()  
                  
                employee_selection = st.selectbox("Employee", employee_options)  
                employee_id = int(employee_selection.split(" - ")[0])  
                  
                action_date = st.date_input("Date", datetime.datetime.now())  
                action_type = st.selectbox("Type", ["Verbal Warning", "Written Warning", "Suspension", "Termination"])  
                  
                reason = st.text_input("Reason")  
                description = st.text_area("Description")  
                documentation = st.text_input("Documentation Reference")  
                  
                issuer_options = st.session_state.employees.apply(  
                    lambda x: f"{x['employee_id']} - {x['first_name']} {x['last_name']}",   
                    axis=1  
                ).tolist()  
                  
                issuer_selection = st.selectbox("Issued By", issuer_options)  
                issued_by = int(issuer_selection.split(" - ")[0])  
              
            submit_button = st.form_submit_button("Add Disciplinary Action", disabled=submit_disabled)  
              
            if submit_button:  
                # Generate new disciplinary ID  
                if st.session_state.disciplinary.empty:  
                    new_id = 1  
                else:  
                    new_id = st.session_state.disciplinary['disciplinary_id'].max() + 1  
                  
                # Create new disciplinary record  
                new_disciplinary = pd.DataFrame({  
                    'disciplinary_id': [new_id],  
                    'employee_id': [employee_id],  
                    'date': [action_date.strftime('%Y-%m-%d')],  
                    'type': [action_type],  
                    'reason': [reason],  
                    'description': [description],  
                    'documentation': [documentation],  
                    'issued_by': [issued_by]  
                })  
                  
                # Add to disciplinary dataframe  
                st.session_state.disciplinary = pd.concat([st.session_state.disciplinary, new_disciplinary], ignore_index=True)  
                st.success("Disciplinary action record added successfully!")  
      
    elif record_type == "Performance Review":  
        with st.form("performance_form"):  
            st.subheader("Add Performance Review")  
              
            # Check if we have employees  
            if st.session_state.employees.empty:  
                st.warning("No employees in the system. Please add employees first.")  
                submit_disabled = True  
            else:  
                submit_disabled = False  
                  
                # Get employee options  
                employee_options = st.session_state.employees.apply(  
                    lambda x: f"{x['employee_id']} - {x['first_name']} {x['last_name']}",   
                    axis=1  
                ).tolist()  
                  
                employee_selection = st.selectbox("Employee", employee_options)  
                employee_id = int(employee_selection.split(" - ")[0])  
                  
                review_date = st.date_input("Review Date", datetime.datetime.now())  
                  
                reviewer_options = st.session_state.employees.apply(  
                    lambda x: f"{x['employee_id']} - {x['first_name']} {x['last_name']}",   
                    axis=1  
                ).tolist()  
                  
                reviewer_selection = st.selectbox("Reviewer", reviewer_options)  
                reviewer_id = int(reviewer_selection.split(" - ")[0])  
                  
                performance_rating = st.selectbox("Performance Rating",   
                                                ["Exceeds Expectations", "Meets Expectations",   
                                                 "Needs Improvement", "Unsatisfactory"])  
                  
                review_comments = st.text_area("Review Comments")  
                goals_set = st.text_area("Goals Set")  
                areas_for_improvement = st.text_area("Areas for Improvement")  
              
            submit_button = st.form_submit_button("Add Performance Review", disabled=submit_disabled)  
              
            if submit_button:  
                # Generate new review ID  
                if st.session_state.performance.empty:  
                    new_id = 1  
                else:  
                    new_id = st.session_state.performance['review_id'].max() + 1  
                  
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
                  
                # Add to performance dataframe  
                st.session_state.performance = pd.concat([st.session_state.performance, new_review], ignore_index=True)  
                st.success("Performance review added successfully!")  
      
    elif record_type == "Training Record":  
        with st.form("training_form"):  
            st.subheader("Add Training Record")  
              
            # Check if we have employees  
            if st.session_state.employees.empty:  
                st.warning("No employees in the system. Please add employees first.")  
                submit_disabled = True  
            else:  
                submit_disabled = False  
                  
                # Get employee options  
                employee_options = st.session_state.employees.apply(  
                    lambda x: f"{x['employee_id']} - {x['first_name']} {x['last_name']}",   
                    axis=1  
                ).tolist()  
                  
                employee_selection = st.selectbox("Employee", employee_options)  
                employee_id = int(employee_selection.split(" - ")[0])  
                  
                training_name = st.text_input("Training Name")  
                training_date = st.date_input("Training Date", datetime.datetime.now())  
                provider = st.text_input("Provider")  
                  
                completion_status = st.selectbox("Completion Status",   
                                               ["Completed", "In Progress", "Not Started", "Failed"])  
                  
                has_expiry = st.checkbox("Has Certification Expiry")  
                if has_expiry:  
                    certification_expiry = st.date_input("Certification Expiry",   
                                                       datetime.datetime.now() + datetime.timedelta(days=365))  
                    certification_expiry_str = certification_expiry.strftime('%Y-%m-%d')  
                else:  
                    certification_expiry_str = None  
              
            submit_button = st.form_submit_button("Add Training Record", disabled=submit_disabled)  
              
            if submit_button:  
                # Generate new training ID  
                if st.session_state.training.empty:  
                    new_id = 1  
                else:  
                    new_id = st.session_state.training['training_id'].max() + 1  
                  
                # Create new training record  
                new_training = pd.DataFrame({  
                    'training_id': [new_id],  
                    'employee_id': [employee_id],  
                    'training_name': [training_name],  
                    'training_date': [training_date.strftime('%Y-%m-%d')],  
                    'provider': [provider],  
                    'completion_status': [completion_status],  
                    'certification_expiry': [certification_expiry_str]  
                })  
                  
                # Add to training dataframe  
                st.session_state.training = pd.concat([st.session_state.training, new_training], ignore_index=True)  
                st.success("Training record added successfully!")  
  
# Search Page  
elif page == "Search":  
    st.header("Search Records")  
      
    record_type = st.selectbox(  
        "Select record type to search:",  
        ["Employees", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records"]  
    )  
      
    search_term = st.text_input("Enter search term")  
      
    if st.button("Search"):  
        if search_term:  
            if record_type == "Employees" and not st.session_state.employees.empty:  
                # Search in employee records  
                results = st.session_state.employees[  
                    st.session_state.employees.astype(str).apply(  
                        lambda row: row.str.contains(search_term, case=False).any(), axis=1  
                    )  
                ]  
                  
                if not results.empty:  
                    st.subheader(f"Found {len(results)} matching employee records:")  
                    st.dataframe(results)  
                else:  
                    st.info("No matching employee records found.")  
              
            elif record_type == "One-on-One Meetings" and not st.session_state.meetings.empty:  
                # Search in meeting records  
                results = st.session_state.meetings[  
                    st.session_state.meetings.astype(str).apply(  
                        lambda row: row.str.contains(search_term, case=False).any(), axis=1  
                    )  
                ]  
                  
                if not results.empty:  
                    st.subheader(f"Found {len(results)} matching meeting records:")  
                    st.dataframe(results)  
                else:  
                    st.info("No matching meeting records found.")  
              
            elif record_type == "Disciplinary Actions" and not st.session_state.disciplinary.empty:  
                # Search in disciplinary records  
                results = st.session_state.disciplinary[  
                    st.session_state.disciplinary.astype(str).apply(  
                        lambda row: row.str.contains(search_term, case=False).any(), axis=1  
                    )  
                ]  
                  
                if not results.empty:  
                    st.subheader(f"Found {len(results)} matching disciplinary records:")  
                    st.dataframe(results)  
                else:  
                    st.info("No matching disciplinary records found.")  
              
            elif record_type == "Performance Reviews" and not st.session_state.performance.empty:  
                # Search in performance review records  
                results = st.session_state.performance[  
                    st.session_state.performance.astype(str).apply(  
                        lambda row: row.str.contains(search_term, case=False).any(), axis=1  
                    )  
                ]  
                  
                if not results.empty:  
                    st.subheader(f"Found {len(results)} matching performance review records:")  
                    st.dataframe(results)  
                else:  
                    st.info("No matching performance review records found.")  
              
            elif record_type == "Training Records" and not st.session_state.training.empty:  
                # Search in training records  
                results = st.session_state.training[  
                    st.session_state.training.astype(str).apply(  
                        lambda row: row.str.contains(search_term, case=False).any(), axis=1  
                    )  
                ]  
                  
                if not results.empty:  
                    st.subheader(f"Found {len(results)} matching training records:")  
                    st.dataframe(results)  
                else:  
                    st.info("No matching training records found.")  
              
            else:  
                st.info(f"No {record_type.lower()} records available to search.")  
        else:  
            st.warning("Please enter a search term.")  
  
# Reports Page  
elif page == "Reports":  
    st.header("Reports")  
      
    report_type = st.selectbox(  
        "Select report type:",  
        ["Department Distribution", "Employment Status", "Training Completion Status",   
         "Performance Ratings", "Upcoming Certification Expirations"]  
    )  
      
    if report_type == "Department Distribution":  
        if not st.session_state.employees.empty:  
            # Count employees by department  
            dept_counts = st.session_state.employees['department'].value_counts().reset_index()  
            dept_counts.columns = ['Department', 'Count']  
              
            # Display as table  
            st.subheader("Employee Count by Department")  
            st.dataframe(dept_counts)  
              
            # Create bar chart  
            fig, ax = plt.subplots(figsize=(12, 8))  
              
            # Plot horizontal bars  
            bars = ax.barh(dept_counts['Department'], dept_counts['Count'], color='#2563EB')  
              
            # Add data labels  
            for i, bar in enumerate(bars):  
                ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,   
                        str(dept_counts['Count'].iloc[i]),  
                        va='center', fontsize=14, color='#171717')  
              
            # Customize appearance  
            ax.set_title("Employee Distribution by Department", fontsize=20, pad=15, color="#171717")  
            ax.set_xlabel("Number of Employees", fontsize=16, labelpad=10, color="#171717")  
            ax.set_ylabel("Department", fontsize=16, labelpad=10, color="#171717")  
              
            # Style the plot  
            ax.spines['top'].set_visible(False)  
            ax.spines['right'].set_visible(False)  
            ax.spines['left'].set_color('#E5E7EB')  
            ax.spines['bottom'].set_color('#E5E7EB')  
              
            ax.tick_params(axis='both', colors='#171717', labelsize=14)  
            ax.set_axisbelow(True)  
            ax.grid(axis='x', linestyle='-', alpha=0.2, color='#F3F4F6')  
              
            st.pyplot(fig)  
        else:  
            st.info("No employee data available for reporting.")  
      
    elif report_type == "Employment Status":  
        if not st.session_state.employees.empty:  
            # Count employees by status  
            status_counts = st.session_state.employees['employment_status'].value_counts().reset_index()  
            status_counts.columns = ['Status', 'Count']  
              
            # Display as table  
            st.subheader("Employee Count by Employment Status")  
            st.dataframe(status_counts)  
              
            # Create pie chart  
            fig, ax = plt.subplots(figsize=(12, 8))  
              
            # Custom colors  
            colors = ['#2563EB', '#24EB84', '#EB3424', '#D324EB']  
              
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
              
            st.pyplot(fig)  
        else:  
            st.info("No employee data available for reporting.")  
      
    elif report_type == "Training Completion Status":  
        if not st.session_state.training.empty:  
            # Count training records by completion status  
            training_status = st.session_state.training['completion_status'].value_counts().reset_index()  
            training_status.columns = ['Status', 'Count']  
              
            # Display as table  
            st.subheader("Training Records by Completion Status")  
            st.dataframe(training_status)  
              
            # Create bar chart  
            fig, ax = plt.subplots(figsize=(12, 8))  
              
            # Define colors based on status  
            status_colors = {  
                'Completed': '#24EB84',  
                'In Progress': '#2563EB',  
                'Not Started': '#E5E7EB',  
                'Failed': '#EB3424'  
            }  
              
            # Get colors for each status  
            colors = [status_colors.get(status, '#2563EB') for status in training_status['Status']]  
              
            # Create horizontal bar chart  
            bars = ax.barh(training_status['Status'], training_status['Count'], color=colors)  
              
            # Add data labels  
            for i, bar in enumerate(bars):  
                ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,   
                        str(training_status['Count'].iloc[i]),  
                        va='center', fontsize=14, color='#171
