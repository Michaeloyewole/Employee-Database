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
# 2. Data Persistence Functions  
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
    if employee_id is None:  
        return "N/A"  
    employee = st.session_state.employees[st.session_state.employees['employee_id'] == employee_id]  
    if not employee.empty:  
        return f"{employee['first_name'].values[0]} {employee['last_name'].values[0]}"  
    return "Unknown"  
  
# -------------------------------  
# 3. Initialize Tables in Session State  
# -------------------------------  
# 1. Employees Table  
if 'employees' not in st.session_state:  
    st.session_state.employees = load_table('employees', [  
        'employee_id', 'first_name', 'last_name', 'employee_number',  
        'department', 'job_title', 'hire_date', 'email', 'phone',  
        'address', 'date_of_birth', 'manager_id', 'employment_status'  
    ])  
  
# 2. One-on-One Meetings Table  
if 'meetings' not in st.session_state:  
    st.session_state.meetings = load_table('meetings', [  
        'meeting_id', 'employee_id', 'manager_id', 'meeting_date',  
        'meeting_time', 'topics_discussed', 'action_items', 'notes',  
        'next_meeting_date'  
    ])  
  
# 3. Disciplinary Actions Table  
if 'disciplinary' not in st.session_state:  
    st.session_state.disciplinary = load_table('disciplinary', [  
        'disciplinary_id', 'employee_id', 'date', 'type', 'reason',  
        'description', 'documentation', 'issued_by'  
    ])  
  
# 4. Performance Reviews Table  
if 'performance' not in st.session_state:  
    st.session_state.performance = load_table('performance', [  
        'review_id', 'employee_id', 'review_date', 'reviewer_id',  
        'performance_rating', 'review_comments', 'goals_set',   
        'areas_for_improvement'  
    ])  
  
# 5. Training Records Table  
if 'training' not in st.session_state:  
    st.session_state.training = load_table('training', [  
        'training_id', 'employee_id', 'training_name', 'training_date',  
        'provider', 'completion_status', 'certification_expiry'  
    ])  
  
# -------------------------------  
# 4. Sidebar Navigation & Export  
# -------------------------------  
st.sidebar.title("Navigation")  
module = st.sidebar.radio("Select Module", [  
    "Employee Management",   
    "One-on-One Meetings",   
    "Disciplinary Actions",  
    "Performance Reviews",  
    "Training Records",  
    "Reports"  
])  
  
# Export functionality  
st.sidebar.header("Data Export")  
export_table = st.sidebar.selectbox(  
    "Select table to export",   
    ["Employees", "Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records"]  
)  
  
if st.sidebar.button("Export CSV"):  
    table_map = {  
        "Employees": "employees",  
        "Meetings": "meetings",  
        "Disciplinary Actions": "disciplinary",  
        "Performance Reviews": "performance",  
        "Training Records": "training"  
    }  
      
    table_name = table_map[export_table]  
    df = getattr(st.session_state, table_name)  
      
    if not df.empty:  
        csv = df.to_csv(index=False).encode('utf-8')  
        b64 = base64.b64encode(csv).decode()  
        href = f'<a href="data:file/csv;base64,{b64}" download="{table_name}.csv">Download {export_table} CSV</a>'  
        st.sidebar.markdown(href, unsafe_allow_html=True)  
    else:  
        st.sidebar.error(f"No data in {export_table} table")  
  
# -------------------------------  
# 5. Main Content Area  
# -------------------------------  
if module == "Employee Management":  
    st.header("Employee Management")  
      
    col1, col2 = st.columns(2)  
      
    with col1:  
        st.subheader("Add New Employee")  
        with st.form("employee_form"):  
            new_employee_id = (st.session_state.employees['employee_id'].max() + 1) if not st.session_state.employees.empty else 1  
              
            first_name = st.text_input("First Name")  
            last_name = st.text_input("Last Name")  
            employee_number = st.text_input("Employee Number")  
            department = st.text_input("Department")  
            job_title = st.text_input("Job Title")  
            hire_date = st.date_input("Hire Date", datetime.date.today())  
            email = st.text_input("Email")  
            phone = st.text_input("Phone")  
            address = st.text_input("Address")  
            date_of_birth = st.date_input("Date of Birth", datetime.date(1990, 1, 1))  
              
            # Manager selection  
            if not st.session_state.employees.empty:  
                manager_options = st.session_state.employees.copy()  
                manager_options['display_name'] = manager_options['first_name'] + " " + manager_options['last_name']  
                manager_id = st.selectbox(  
                    "Manager",   
                    options=manager_options['employee_id'].tolist(),  
                    format_func=lambda x: manager_options[manager_options['employee_id'] == x]['display_name'].values[0]  
                )  
            else:  
                manager_id = None  
                st.info("No managers available. This will be set as None.")  
              
            employment_status = st.selectbox("Employment Status", ["Active", "Inactive", "Terminated"])  
              
            submitted = st.form_submit_button("Add Employee")  
              
            if submitted:  
                new_employee = pd.DataFrame({  
                    "employee_id": [new_employee_id],  
                    "first_name": [first_name],  
                    "last_name": [last_name],  
                    "employee_number": [employee_number],  
                    "department": [department],  
                    "job_title": [job_title],  
                    "hire_date": [hire_date.strftime('%Y-%m-%d')],  
                    "email": [email],  
                    "phone": [phone],  
                    "address": [address],  
                    "date_of_birth": [date_of_birth.strftime('%Y-%m-%d')],  
                    "manager_id": [manager_id],  
                    "employment_status": [employment_status]  
                })  
                  
                st.session_state.employees = pd.concat([st.session_state.employees, new_employee], ignore_index=True)  
                st.success("Employee added successfully!")  
      
    with col2:  
        st.subheader("Employees Table")  
        st.dataframe(st.session_state.employees)  
        if st.button("Save Employee Data"):  
            save_table("employees", st.session_state.employees)  
  
elif module == "One-on-One Meetings":  
    st.header("One-on-One Meetings")  
      
    col1, col2 = st.columns(2)  
      
    with col1:  
        st.subheader("Schedule a Meeting")  
        with st.form("meeting_form"):  
            new_meeting_id = (st.session_state.meetings['meeting_id'].max() + 1) if not st.session_state.meetings.empty else 1  
              
            if not st.session_state.employees.empty:  
                employee_options = st.session_state.employees.copy()  
                employee_options['display_name'] = employee_options['first_name'] + " " + employee_options['last_name']  
                  
                employee_id = st.selectbox(  
                    "Employee",   
                    options=employee_options['employee_id'].tolist(),  
                    format_func=lambda x: employee_options[employee_options['employee_id'] == x]['display_name'].values[0]  
                )  
                  
                manager_id = st.selectbox(  
                    "Manager",   
                    options=employee_options['employee_id'].tolist(),  
                    format_func=lambda x: employee_options[employee_options['employee_id'] == x]['display_name'].values[0],  
                    index=1 if len(employee_options) > 1 else 0  
                )  
            else:  
                st.error("No employees available. Please add employees first.")  
                employee_id, manager_id = None, None  
              
            meeting_date = st.date_input("Meeting Date", datetime.date.today())  
            meeting_time = st.time_input("Meeting Time", datetime.time(9, 0))  
            topics_discussed = st.text_area("Topics Discussed")  
            action_items = st.text_area("Action Items")  
            notes = st.text_area("Notes")  
            next_meeting_date = st.date_input("Next Meeting Date (Optional)", datetime.date.today() + datetime.timedelta(days=30))  
              
            submitted_meeting = st.form_submit_button("Add Meeting")  
              
            if submitted_meeting and employee_id is not None and manager_id is not None:  
                new_meeting = pd.DataFrame({  
                    "meeting_id": [new_meeting_id],  
                    "employee_id": [employee_id],  
                    "manager_id": [manager_id],  
                    "meeting_date": [meeting_date.strftime('%Y-%m-%d')],  
                    "meeting_time": [meeting_time.strftime('%H:%M:%S')],  
                    "topics_discussed": [topics_discussed],  
                    "action_items": [action_items],  
                    "notes": [notes],  
                    "next_meeting_date": [next_meeting_date.strftime('%Y-%m-%d')]  
                })  
                  
                st.session_state.meetings = pd.concat([st.session_state.meetings, new_meeting], ignore_index=True)  
                st.success("Meeting scheduled!")  
      
    with col2:  
        st.subheader("Meetings Table")  
        st.dataframe(st.session_state.meetings)  
        if st.button("Save Meetings Data"):  
            save_table("meetings", st.session_state.meetings)  
  
elif module == "Disciplinary Actions":  
    st.header("Disciplinary Actions")  
      
    col1, col2 = st.columns(2)  
      
    with col1:  
        st.subheader("Record a Disciplinary Action")  
        with st.form("disciplinary_form"):  
            new_disciplinary_id = (st.session_state.disciplinary['disciplinary_id'].max() + 1) if not st.session_state.disciplinary.empty else 1  
              
            if not st.session_state.employees.empty:  
                employee_options = st.session_state.employees.copy()  
                employee_options['display_name'] = employee_options['first_name'] + " " + employee_options['last_name']  
                  
                employee_id = st.selectbox(  
                    "Employee",   
                    options=employee_options['employee_id'].tolist(),  
                    format_func=lambda x: employee_options[employee_options['employee_id'] == x]['display_name'].values[0],  
                    key="disc_employee"  
                )  
                  
                issued_by = st.selectbox(  
                    "Issued By",   
                    options=employee_options['employee_id'].tolist(),  
                    format_func=lambda x: employee_options[employee_options['employee_id'] == x]['display_name'].values[0],  
                    key="disc_issuer"  
                )  
            else:  
                st.error("No employees available. Please add employees first.")  
                employee_id, issued_by = None, None  
              
            action_date = st.date_input("Date", datetime.date.today())  
            action_type = st.selectbox("Type", ["Verbal Warning", "Written Warning", "Suspension", "Termination"])  
            reason = st.text_input("Reason")  
            description = st.text_area("Description")  
            documentation = st.text_input("Documentation (file path)")  
              
            submitted_disciplinary = st.form_submit_button("Add Disciplinary Action")  
              
            if submitted_disciplinary and employee_id is not None and issued_by is not None:  
                new_disciplinary = pd.DataFrame({  
                    "disciplinary_id": [new_disciplinary_id],  
                    "employee_id": [employee_id],  
                    "date": [action_date.strftime('%Y-%m-%d')],  
                    "type": [action_type],  
                    "reason": [reason],  
                    "description": [description],  
                    "documentation": [documentation],  
                    "issued_by": [issued_by]  
                })  
                  
                st.session_state.disciplinary = pd.concat([st.session_state.disciplinary, new_disciplinary], ignore_index=True)  
                st.success("Disciplinary action recorded!")  
      
    with col2:  
        st.subheader("Disciplinary Actions Table")  
        st.dataframe(st.session_state.disciplinary)  
        if st.button("Save Disciplinary Data"):  
            save_table("disciplinary", st.session_state.disciplinary)  
  
elif module == "Performance Reviews":  
    st.header("Performance Reviews")  
      
    col1, col2 = st.columns(2)  
      
    with col1:  
        st.subheader("Add Performance Review")  
        with st.form("review_form"):  
            new_review_id = (st.session_state.performance['review_id'].max() + 1) if not st.session_state.performance.empty else 1  
              
            if not st.session_state.employees.empty:  
                employee_options = st.session_state.employees.copy()  
                employee_options['display_name'] = employee_options['first_name'] + " " + employee_options['last_name']  
                  
                employee_id = st.selectbox(  
                    "Employee",   
                    options=employee_options['employee_id'].tolist(),  
                    format_func=lambda x: employee_options[employee_options['employee_id'] == x]['display_name'].values[0],  
                    key="review_employee"  
                )  
                  
                reviewer_id = st.selectbox(  
                    "Reviewer",   
                    options=employee_options['employee_id'].tolist(),  
                    format_func=lambda x: employee_options[employee_options['employee_id'] == x]['display_name'].values[0],  
                    key="reviewer"  
                )  
            else:  
                st.error("No employees available. Please add employees first.")  
                employee_id, reviewer_id = None, None  
              
            review_date = st.date_input("Review Date", datetime.date.today())  
            performance_rating = st.selectbox("Performance Rating", ["Exceeds Expectations", "Meets Expectations", "Needs Improvement", "Unsatisfactory"])  
            review_comments = st.text_area("Review Comments")  
            goals_set = st.text_area("Goals Set")  
            areas_for_improvement = st.text_area("Areas for Improvement")  
              
            submitted_review = st.form_submit_button("Add Performance Review")  
              
            if submitted_review and employee_id is not None and reviewer_id is not None:  
                new_review = pd.DataFrame({  
                    "review_id": [new_review_id],  
                    "employee_id": [employee_id],  
                    "review_date": [review_date.strftime('%Y-%m-%d')],  
                    "reviewer_id": [reviewer_id],  
                    "performance_rating": [performance_rating],  
                    "review_comments": [review_comments],  
                    "goals_set": [goals_set],  
                    "areas_for_improvement": [areas_for_improvement]  
                })  
                  
                st.session_state.performance = pd.concat([st.session_state.performance, new_review], ignore_index=True)  
                st.success("Performance review added!")  
      
    with col2:  
        st.subheader("Performance Reviews Table")  
        st.dataframe(st.session_state.performance)  
        if st.button("Save Performance Data"):  
            save_table("performance", st.session_state.performance)  
  
elif module == "Training Records":  
    st.header("Training Records")  
      
    col1, col2 = st.columns(2)  
      
    with col1:  
        st.subheader("Add Training Record")  
        with st.form("training_form"):  
            new_training_id = (st.session_state.training['training_id'].max() + 1) if not st.session_state.training.empty else 1  
              
            if not st.session_state.employees.empty:  
                employee_options = st.session_state.employees.copy()  
                employee_options['display_name'] = employee_options['first_name'] + " " + employee_options['last_name']  
                  
                employee_id = st.selectbox(  
                    "Employee",   
                    options=employee_options['employee_id'].tolist(),  
                    format_func=lambda x: employee_options[employee_options['employee_id'] == x]['display_name'].values[0],  
                    key="training_employee"  
                )  
            else:  
                st.error("No employees available. Please add employees first.")  
                employee_id = None  
              
            training_name = st.text_input("Training Name")  
            training_date = st.date_input("Training Date", datetime.date.today())  
            provider = st.text_input("Provider")  
            completion_status = st.selectbox("Completion Status", ["Completed", "In Progress", "Not Started", "Failed"])  
            certification_expiry = st.date_input("Certification Expiry (if applicable)", datetime.date.today() + datetime.timedelta(days=365))  
              
            submitted_training = st.form_submit_button("Add Training Record")  
              
            if submitted_training and employee_id is not None:  
                new_training = pd.DataFrame({  
                    "training_id": [new_training_id],  
                    "employee_id": [employee_id],  
                    "training_name": [training_name],  
                    "training_date": [training_date.strftime('%Y-%m-%d')],  
                    "provider": [provider],  
                    "completion_status": [completion_status],  
                    "certification_expiry": [certification_expiry.strftime('%Y-%m-%d')]  
                })  
                  
                st.session_state.training = pd.concat([st.session_state.training, new_training], ignore_index=True)  
                st.success("Training record added!")  
      
    with col2:  
        st.subheader("Training Records Table")  
        st.dataframe(st.session_state.training)  
        if st.button("Save Training Data"):  
            save_table("training", st.session_state.training)  
  
elif module == "Reports":  
    st.header("Reports")  
      
    report_type = st.selectbox(  
        "Select Report Type",  
        [  
            "Department Distribution",   
            "Employment Status Distribution",  
            "Performance Ratings Distribution",  
            "Training Completion Status",  
            "Disciplinary Actions by Type"  
        ]  
    )  
      
    if report_type == "Department Distribution":  
        if not st.session_state.employees.empty:  
            dept_count = st.session_state.employees['department'].value_counts().reset_index()  
            dept_count.columns = ['Department', 'Count']  
              
            st.subheader("Employees by Department")  
            st.table(dept_count)  
              
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
      
    elif report_type == "Employment Status Distribution":  
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
      
    elif report_type == "Performance Ratings Distribution":  
        if not st.session_state.performance.empty:  
            rating_counts = st.session_state.performance['performance_rating'].value_counts().reset_index()  
            rating_counts.columns = ['Rating', 'Count']  
              
            st.subheader("Performance Ratings Distribution")  
            st.table(rating_counts)  
              
            fig, ax = plt.subplots(figsize=(12, 8))  
            colors = ['#2563EB', '#24EB84', '#EB3424', '#D324EB']  
            ax.bar(rating_counts['Rating'], rating_counts['Count'], color=colors[:len(rating_counts)])  
            ax.set_title("Performance Ratings Distribution", fontsize=20, pad=15, color="#171717")  
            ax.set_xlabel("Rating", fontsize=16, labelpad=10, color="#171717")  
            ax.set_ylabel("Count", fontsize=16, labelpad=10, color="#171717")  
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
            st.info("No performance review data available for reporting.")  
      
    elif report_type == "Training Completion Status":  
        if not st.session_state.training.empty:  
            completion_counts = st.session_state.training['completion_status'].value_counts().reset_index()  
            completion_counts.columns = ['Status', 'Count']  
              
            st.subheader("Training Completion Status")  
            st.table(completion_counts)  
              
            fig, ax = plt.subplots(figsize=(12, 8))  
            colors = ['#2563EB', '#24EB84', '#EB3424', '#D324EB']  
            wedges, texts, autotexts = ax.pie(  
                completion_counts['Count'],  
                labels=completion_counts['Status'],  
                autopct='%1.1f%%',  
                startangle=90,  
                colors=colors[:len(completion_counts)]  
            )  
            ax.set_title("Training Completion Status", fontsize=20, pad=15, color="#171717")  
            for text in texts:  
                text.set_color('#171717')  
                text.set_fontsize(14)  
            for autotext in autotexts:  
                autotext.set_color('white')  
                autotext.set_fontsize(14)  
            ax.axis('equal')  
            st.pyplot(fig)  
        else:  
            st.info("No training data available for reporting.")  
      
    elif report_type == "Disciplinary Actions by Type":  
        if not st.session_state.disciplinary.empty:  
            type_counts = st.session_state.disciplinary['type'].value_counts().reset_index()  
            type_counts.columns = ['Type', 'Count']  
              
            st.subheader("Disciplinary Actions by Type")  
            st.table(type_counts)  
              
            fig, ax = plt.subplots(figsize=(12, 8))  
            colors = ['#2563EB', '#24EB84', '#B2EB24', '#EB3424']  
            ax.bar(type_counts['Type'], type_counts['Count'], color=colors[:len(type_counts)])  
            ax.set_title("Disciplinary Actions by Type", fontsize=20, pad=15, color="#171717")  
            ax.set_xlabel("Type", fontsize=16, labelpad=10, color="#171717")  
            ax.set_ylabel("Count", fontsize=16, labelpad=10, color="#171717")  
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
            st.info("No disciplinary data available for reporting.")  
