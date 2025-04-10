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
        for col in columns:  
            if col not in df.columns:  
                df[col] = ""  
        return df  
    except Exception as e:  
        st.error("Error loading file: " + str(e))  
        return pd.DataFrame({col: [] for col in columns})  
  
# -------------------------------  
# 4. Initialize Session State  
# -------------------------------  
# Define columns for each table  
employee_columns = ['employee_id', 'first_name', 'last_name', 'department', 'position', 'email', 'phone', 'employment_status']  
meeting_columns = ['meeting_id', 'employee_id', 'meeting_date', 'meeting_time', 'Meeting Agenda', 'action_items', 'notes', 'next_meeting_date']  
performance_columns = ['review_id', 'employee_id', 'review_date', 'reviewer', 'performance_rating', 'strengths', 'areas_for_improvement', 'goals', 'comments']  
training_columns = ['training_id', 'employee_id', 'course_name', 'start_date', 'end_date', 'status', 'certification', 'score']  
disciplinary_columns = ['disciplinary_id', 'employee_id', 'type', 'date', 'description']  
  
# Initialize session state variables if they don't exist  
if 'employees' not in st.session_state:  
    st.session_state.employees = load_table('employees', employee_columns)  
if 'meetings' not in st.session_state:  
    st.session_state.meetings = load_table('meetings', meeting_columns)  
if 'performance' not in st.session_state:  
    st.session_state.performance = load_table('performance', performance_columns)  
if 'training' not in st.session_state:  
    st.session_state.training = load_table('training', training_columns)  
if 'disciplinary' not in st.session_state:  
    st.session_state.disciplinary = load_table('disciplinary', disciplinary_columns)  
  
# -------------------------------  
# 5. Sidebar Navigation  
# -------------------------------  
st.sidebar.title("Employee Records Tool")  
  
# Use radio buttons for module selection instead of selectbox  
module = st.sidebar.radio(  
    "Select Module",  
    ["Employee Management", "One-on-One Meetings", "Performance Reviews",   
     "Training Records", "Disciplinary Actions", "Reports"]  
)  
  
# -------------------------------  
# 6. Module: Employee Management  
# -------------------------------  
if module == "Employee Management":  
    st.header("Employee Management")  
      
    # CSV Upload option for Employees  
    uploaded_employees = st.file_uploader("Upload Employees CSV", type="csv", key="employee_upload")  
    if uploaded_employees is not None:  
        st.session_state.employees = load_from_uploaded_file(uploaded_employees, employee_columns)  
        st.success("Employee data uploaded successfully!")  
      
    # Search and Delete functionality  
    st.subheader("Search Employee")  
    search_col1, search_col2, search_col3 = st.columns([2, 1, 1])  
    with search_col1:  
        search_id = st.text_input("Enter Employee ID to search")  
      
    employee_found = None  
    if search_id and search_id.isdigit():  
        search_id_int = int(search_id)  
        employee_found = st.session_state.employees[st.session_state.employees['employee_id'] == search_id_int]  
          
        if not employee_found.empty:  
            with search_col2:  
                if st.button("Delete Record"):  
                    st.session_state.employees = st.session_state.employees[st.session_state.employees['employee_id'] != search_id_int]  
                    st.success(f"Employee ID {search_id} deleted!")  
                    employee_found = None  
                    search_id = ""  
        else:  
            st.warning(f"No employee found with ID {search_id}")  
      
    # Employee Form  
    st.subheader("Add/Edit Employee")  
    with st.form("employee_form"):  
        col1, col2 = st.columns(2)  
          
        # Auto-populate fields if employee found  
        first_name_val = ""  
        last_name_val = ""  
        department_val = ""  
        position_val = ""  
        email_val = ""  
        phone_val = ""  
        employment_status_val = "Active"  
          
        if employee_found is not None and not employee_found.empty:  
            first_name_val = employee_found['first_name'].values[0]  
            last_name_val = employee_found['last_name'].values[0]  
            department_val = employee_found['department'].values[0]  
            position_val = employee_found['position'].values[0]  
            email_val = employee_found['email'].values[0]  
            phone_val = employee_found['phone'].values[0]  
            employment_status_val = employee_found['employment_status'].values[0]  
          
        with col1:  
            employee_id = st.text_input("Employee ID (max 6 digits)", value=search_id, max_chars=6)  
            first_name = st.text_input("First Name", value=first_name_val)  
            last_name = st.text_input("Last Name", value=last_name_val)  
            department = st.text_input("Department", value=department_val)  
          
        with col2:  
            position = st.text_input("Position", value=position_val)  
            email = st.text_input("Email", value=email_val)  
            phone = st.text_input("Phone", value=phone_val)  
            employment_status = st.selectbox("Employment Status",   
                                            ["Active", "On Leave", "Terminated", "Retired"],  
                                            index=["Active", "On Leave", "Terminated", "Retired"].index(employment_status_val) if employment_status_val in ["Active", "On Leave", "Terminated", "Retired"] else 0)  
          
        submitted = st.form_submit_button("Save Employee")  
        if submitted:  
            if employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            elif first_name == "" or last_name == "":  
                st.error("First name and last name are required.")  
            else:  
                new_employee = pd.DataFrame({  
                    "employee_id": [int(employee_id)],  
                    "first_name": [first_name],  
                    "last_name": [last_name],  
                    "department": [department],  
                    "position": [position],  
                    "email": [email],  
                    "phone": [phone],  
                    "employment_status": [employment_status],  
                })  
                  
                # Update employee if exists  
                emp_id_int = int(employee_id)  
                if emp_id_int in st.session_state.employees['employee_id'].values:  
                    st.session_state.employees = st.session_state.employees[st.session_state.employees['employee_id'] != emp_id_int]  
                st.session_state.employees = pd.concat([st.session_state.employees, new_employee], ignore_index=True)  
                st.success("Employee record added/updated!")  
      
    st.subheader("Employees Table")  
    st.dataframe(st.session_state.employees)  
    st.markdown(get_csv_download_link(st.session_state.employees, "employees.csv", "Download Employees CSV"), unsafe_allow_html=True)  
    if st.button("Save Employees Data"):  
        save_table("employees", st.session_state.employees)  
  
# -------------------------------  
# 7. Module: One-on-One Meetings  
# -------------------------------  
elif module == "One-on-One Meetings":  
    st.header("One-on-One Meetings")  
      
    # CSV Upload option for Meetings  
    uploaded_meetings = st.file_uploader("Upload Meetings CSV", type="csv", key="meeting_upload")  
    if uploaded_meetings is not None:  
        st.session_state.meetings = load_from_uploaded_file(uploaded_meetings, meeting_columns)  
        st.success("Meetings data uploaded successfully!")  
      
    # Search and Delete functionality  
    st.subheader("Search Meeting")  
    search_col1, search_col2, search_col3 = st.columns([2, 1, 1])  
    with search_col1:  
        search_meeting_id = st.text_input("Enter Meeting ID to search")  
      
    meeting_found = None  
    if search_meeting_id and search_meeting_id.isdigit():  
        search_id_int = int(search_meeting_id)  
        meeting_found = st.session_state.meetings[st.session_state.meetings['meeting_id'] == search_id_int]  
          
        if not meeting_found.empty:  
            with search_col2:  
                if st.button("Delete Meeting"):  
                    st.session_state.meetings = st.session_state.meetings[st.session_state.meetings['meeting_id'] != search_id_int]  
                    st.success(f"Meeting ID {search_meeting_id} deleted!")  
                    meeting_found = None  
                    search_meeting_id = ""  
        else:  
            st.warning(f"No meeting found with ID {search_meeting_id}")  
      
    with st.form("meeting_form"):  
        col1, col2 = st.columns(2)  
          
        # Auto-populate fields if meeting found  
        employee_id_val = ""  
        meeting_date_val = datetime.date.today()  
        meeting_time_val = datetime.time(9, 0)  
        meeting_agenda_val = ""  
        action_items_val = ""  
        notes_val = ""  
        next_meeting_date_val = datetime.date.today()  
          
        if meeting_found is not None and not meeting_found.empty:  
            employee_id_val = str(meeting_found['employee_id'].values[0])  
              
            # Handle date conversion  
            try:  
                meeting_date_str = meeting_found['meeting_date'].values[0]  
                if isinstance(meeting_date_str, str):  
                    meeting_date_val = datetime.datetime.strptime(meeting_date_str, '%Y-%m-%d').date()  
            except:  
                meeting_date_val = datetime.date.today()  
                  
            # Handle time conversion  
            try:  
                meeting_time_str = meeting_found['meeting_time'].values[0]  
                if isinstance(meeting_time_str, str):  
                    meeting_time_val = datetime.datetime.strptime(meeting_time_str, '%H:%M:%S').time()  
            except:  
                meeting_time_val = datetime.time(9, 0)  
                  
            meeting_agenda_val = meeting_found['Meeting Agenda'].values[0]  
            action_items_val = meeting_found['action_items'].values[0]  
            notes_val = meeting_found['notes'].values[0]  
              
            # Handle next meeting date conversion  
            try:  
                next_date_str = meeting_found['next_meeting_date'].values[0]  
                if isinstance(next_date_str, str):  
                    next_meeting_date_val = datetime.datetime.strptime(next_date_str, '%Y-%m-%d').date()  
            except:  
                next_meeting_date_val = datetime.date.today()  
          
        with col1:  
            meeting_id = st.text_input("Meeting ID (max 6 digits)", value=search_meeting_id, max_chars=6)  
            employee_id = st.text_input("Employee ID (max 6 digits)", value=employee_id_val, max_chars=6)  
            meeting_date = st.date_input("Meeting Date", value=meeting_date_val)  
            meeting_time = st.time_input("Meeting Time", value=meeting_time_val)  
        with col2:  
            meeting_agenda = st.text_area("Meeting Agenda", value=meeting_agenda_val)  
            action_items = st.text_area("Action Items", value=action_items_val)  
            notes = st.text_area("Notes", value=notes_val)  
            next_meeting_date = st.date_input("Next Meeting Date", value=next_meeting_date_val)  
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
                    "Meeting Agenda": [meeting_agenda],  
                    "action_items": [action_items],  
                    "notes": [notes],  
                    "next_meeting_date": [next_meeting_date.strftime('%Y-%m-%d')]  
                })  
                  
                # Update meeting if exists  
                meeting_id_int = int(meeting_id)  
                if meeting_id_int in st.session_state.meetings['meeting_id'].values:  
                    st.session_state.meetings = st.session_state.meetings[st.session_state.meetings['meeting_id'] != meeting_id_int]  
                st.session_state.meetings = pd.concat([st.session_state.meetings, new_meeting], ignore_index=True)  
                st.success("Meeting recorded successfully!")  
      
    st.subheader("Meetings Table")  
    st.dataframe(st.session_state.meetings)  
    st.markdown(get_csv_download_link(st.session_state.meetings, "meetings.csv", "Download Meetings CSV"), unsafe_allow_html=True)  
    if st.button("Save Meetings Data"):  
        save_table("meetings", st.session_state.meetings)  
  
# -------------------------------  
# 8. Module: Performance Reviews  
# -------------------------------  
elif module == "Performance Reviews":  
    st.header("Performance Reviews")  
      
    # CSV Upload option for Performance  
    uploaded_performance = st.file_uploader("Upload Performance CSV", type="csv", key="performance_upload")  
    if uploaded_performance is not None:  
        st.session_state.performance = load_from_uploaded_file(uploaded_performance, performance_columns)  
        st.success("Performance data uploaded successfully!")  
      
    # Search and Delete functionality  
    st.subheader("Search Performance Review")  
    search_col1, search_col2, search_col3 = st.columns([2, 1, 1])  
    with search_col1:  
        search_review_id = st.text_input("Enter Review ID to search")  
      
    review_found = None  
    if search_review_id and search_review_id.isdigit():  
        search_id_int = int(search_review_id)  
        review_found = st.session_state.performance[st.session_state.performance['review_id'] == search_id_int]  
          
        if not review_found.empty:  
            with search_col2:  
                if st.button("Delete Review"):  
                    st.session_state.performance = st.session_state.performance[st.session_state.performance['review_id'] != search_id_int]  
                    st.success(f"Review ID {search_review_id} deleted!")  
                    review_found = None  
                    search_review_id = ""  
        else:  
            st.warning(f"No review found with ID {search_review_id}")  
      
    with st.form("performance_form"):  
        col1, col2 = st.columns(2)  
          
        # Auto-populate fields if review found  
        employee_id_val = ""  
        review_date_val = datetime.date.today()  
        reviewer_val = ""  
        performance_rating_val = 3  
        strengths_val = ""  
        areas_for_improvement_val = ""  
        goals_val = ""  
        comments_val = ""  
          
        if review_found is not None and not review_found.empty:  
            employee_id_val = str(review_found['employee_id'].values[0])  
              
            # Handle date conversion  
            try:  
                review_date_str = review_found['review_date'].values[0]  
                if isinstance(review_date_str, str):  
                    review_date_val = datetime.datetime.strptime(review_date_str, '%Y-%m-%d').date()  
            except:  
                review_date_val = datetime.date.today()  
                  
            reviewer_val = review_found['reviewer'].values[0]  
              
            # Handle rating conversion  
            try:  
                rating = review_found['performance_rating'].values[0]  
                if isinstance(rating, (int, float)):  
                    performance_rating_val = int(rating)  
                elif isinstance(rating, str) and rating.isdigit():  
                    performance_rating_val = int(rating)  
            except:  
                performance_rating_val = 3  
                  
            strengths_val = review_found['strengths'].values[0]  
            areas_for_improvement_val = review_found['areas_for_improvement'].values[0]  
            goals_val = review_found['goals'].values[0]  
            comments_val = review_found['comments'].values[0]  
          
        with col1:  
            review_id = st.text_input("Review ID (max 6 digits)", value=search_review_id, max_chars=6)  
            employee_id = st.text_input("Employee ID (max 6 digits)", value=employee_id_val, max_chars=6)  
            review_date = st.date_input("Review Date", value=review_date_val)  
            reviewer = st.text_input("Reviewer", value=reviewer_val)  
        with col2:  
            performance_rating = st.slider("Performance Rating (1-5)", 1, 5, value=performance_rating_val)  
            strengths = st.text_area("Strengths", value=strengths_val)  
            areas_for_improvement = st.text_area("Areas for Improvement", value=areas_for_improvement_val)  
            goals = st.text_area("Goals", value=goals_val)  
            comments = st.text_area("Comments", value=comments_val)  
        submitted_perf = st.form_submit_button("Record Performance Review")  
        if submitted_perf:  
            if review_id == "" or not review_id.isdigit():  
                st.error("Please enter a valid numeric Review ID (up to 6 digits).")  
            elif employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            else:  
                new_review = pd.DataFrame({  
                    "review_id": [int(review_id)],  
                    "employee_id": [int(employee_id)],  
                    "review_date": [review_date.strftime('%Y-%m-%d')],  
                    "reviewer": [reviewer],  
                    "performance_rating": [performance_rating],  
                    "strengths": [strengths],  
                    "areas_for_improvement": [areas_for_improvement],  
                    "goals": [goals],  
                    "comments": [comments]  
                })  
                  
                # Update review if exists  
                review_id_int = int(review_id)  
                if review_id_int in st.session_state.performance['review_id'].values:  
                    st.session_state.performance = st.session_state.performance[st.session_state.performance['review_id'] != review_id_int]  
                st.session_state.performance = pd.concat([st.session_state.performance, new_review], ignore_index=True)  
                st.success("Performance review recorded successfully!")  
      
    st.subheader("Performance Reviews Table")  
    st.dataframe(st.session_state.performance)  
    st.markdown(get_csv_download_link(st.session_state.performance, "performance.csv", "Download Performance CSV"), unsafe_allow_html=True)  
    if st.button("Save Performance Data"):  
        save_table("performance", st.session_state.performance)  
  
# -------------------------------  
# 9. Module: Training Records  
# -------------------------------  
elif module == "Training Records":  
    st.header("Training Records")  
      
    # CSV Upload option for Training  
    uploaded_training = st.file_uploader("Upload Training CSV", type="csv", key="training_upload")  
    if uploaded_training is not None:  
        st.session_state.training = load_from_uploaded_file(uploaded_training, training_columns)  
        st.success("Training data uploaded successfully!")  
      
    # Search and Delete functionality  
    st.subheader("Search Training Record")  
    search_col1, search_col2, search_col3 = st.columns([2, 1, 1])  
    with search_col1:  
        search_training_id = st.text_input("Enter Training ID to search")  
      
    training_found = None  
    if search_training_id and search_training_id.isdigit():  
        search_id_int = int(search_training_id)  
        training_found = st.session_state.training[st.session_state.training['training_id'] == search_id_int]  
          
        if not training_found.empty:  
            with search_col2:  
                if st.button("Delete Training"):  
                    st.session_state.training = st.session_state.training[st.session_state.training['training_id'] != search_id_int]  
                    st.success(f"Training ID {search_training_id} deleted!")  
                    training_found = None  
                    search_training_id = ""  
        else:  
            st.warning(f"No training found with ID {search_training_id}")  
      
    with st.form("training_form"):  
        col1, col2 = st.columns(2)  
          
        # Auto-populate fields if training found  
        employee_id_val = ""  
        course_name_val = ""  
        start_date_val = datetime.date.today()  
        end_date_val = datetime.date.today() + datetime.timedelta(days=30)  
        status_val = "Enrolled"  
        certification_val = ""  
        score_val = ""  
          
        if training_found is not None and not training_found.empty:  
            employee_id_val = str(training_found['employee_id'].values[0])  
            course_name_val = training_found['course_name'].values[0]  
              
            # Handle date conversions  
            try:  
                start_date_str = training_found['start_date'].values[0]  
                if isinstance(start_date_str, str):  
                    start_date_val = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()  
            except:  
                start_date_val = datetime.date.today()  
                  
            try:  
                end_date_str = training_found['end_date'].values[0]  
                if isinstance(end_date_str, str):  
                    end_date_val = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()  
            except:  
                end_date_val = datetime.date.today() + datetime.timedelta(days=30)  
                  
            status_val = training_found['status'].values[0]  
            certification_val = training_found['certification'].values[0]  
            score_val = str(training_found['score'].values[0])  
          
        with col1:  
            training_id = st.text_input("Training ID (max 6 digits)", value=search_training_id, max_chars=6)  
            employee_id = st.text_input("Employee ID (max 6 digits)", value=employee_id_val, max_chars=6)  
            course_name = st.text_input("Course Name", value=course_name_val)  
            start_date = st.date_input("Start Date", value=start_date_val)  
        with col2:  
            end_date = st.date_input("End Date", value=end_date_val)  
            status = st.selectbox("Status", ["Enrolled", "In Progress", "Completed", "Failed", "Withdrawn"],   
                                index=["Enrolled", "In Progress", "Completed", "Failed", "Withdrawn"].index(status_val) if status_val in ["Enrolled", "In Progress", "Completed", "Failed", "Withdrawn"] else 0)  
            certification = st.text_input("Certification", value=certification_val)  
            score = st.text_input("Score", value=score_val)  
        submitted_training = st.form_submit_button("Record Training")  
        if submitted_training:  
            if training_id == "" or not training_id.isdigit():  
                st.error("Please enter a valid numeric Training ID (up to 6 digits).")  
            elif employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            elif course_name == "":  
                st.error("Course name is required.")  
            else:  
                new_training = pd.DataFrame({  
                    "training_id": [int(training_id)],  
                    "employee_id": [int(employee_id)],  
                    "course_name": [course_name],  
                    "start_date": [start_date.strftime('%Y-%m-%d')],  
                    "end_date": [end_date.strftime('%Y-%m-%d')],  
                    "status": [status],  
                    "certification": [certification],  
                    "score": [score]  
                })  
                  
                # Update training if exists  
                training_id_int = int(training_id)  
                if training_id_int in st.session_state.training['training_id'].values:  
                    st.session_state.training = st.session_state.training[st.session_state.training['training_id'] != training_id_int]  
                st.session_state.training = pd.concat([st.session_state.training, new_training], ignore_index=True)  
                st.success("Training record added successfully!")  
      
    st.subheader("Training Records Table")  
    st.dataframe(st.session_state.training)  
    st.markdown(get_csv_download_link(st.session_state.training, "training.csv", "Download Training CSV"), unsafe_allow_html=True)  
    if st.button("Save Training Data"):  
        save_table("training", st.session_state.training)  
  
# -------------------------------  
# 10. Module: Disciplinary Actions  
# -------------------------------  
elif module == "Disciplinary Actions":  
    st.header("Disciplinary Actions")  
      
    # CSV Upload option for Disciplinary  
    uploaded_disciplinary = st.file_uploader("Upload Disciplinary CSV", type="csv", key="disciplinary_upload")  
    if uploaded_disciplinary is not None:  
        st.session_state.disciplinary = load_from_uploaded_file(uploaded_disciplinary, disciplinary_columns)  
        st.success("Disciplinary data uploaded successfully!")  
      
    # Search and Delete functionality  
    st.subheader("Search Disciplinary Record")  
    search_col1, search_col2, search_col3 = st.columns([2, 1, 1])  
    with search_col1:  
        search_disciplinary_id = st.text_input("Enter Disciplinary ID to search")  
      
    disciplinary_found = None  
    if search_disciplinary_id and search_disciplinary_id.isdigit():  
        search_id_int = int(search_disciplinary_id)  
        disciplinary_found = st.session_state.disciplinary[st.session_state.disciplinary['disciplinary_id'] == search_id_int]  
          
        if not disciplinary_found.empty:  
            with search_col2:  
                if st.button("Delete Disciplinary"):  
                    st.session_state.disciplinary = st.session_state.disciplinary[st.session_state.disciplinary['disciplinary_id'] != search_id_int]  
                    st.success(f"Disciplinary ID {search_disciplinary_id} deleted!")  
                    disciplinary_found = None  
                    search_disciplinary_id = ""  
        else:  
            st.warning(f"No disciplinary record found with ID {search_disciplinary_id}")  
      
    with st.form("disciplinary_form"):  
        col1, col2 = st.columns(2)  
          
        # Auto-populate fields if disciplinary found  
        employee_id_val = ""  
        d_type_val = ""  
        d_date_val = datetime.date.today()  
        description_val = ""  
          
        if disciplinary_found is not None and not disciplinary_found.empty:  
            employee_id_val = str(disciplinary_found['employee_id'].values[0])  
            d_type_val = disciplinary_found['type'].values[0]  
              
            # Handle date conversion  
            try:  
                d_date_str = disciplinary_found['date'].values[0]  
                if isinstance(d_date_str, str):  
                    d_date_val = datetime.datetime.strptime(d_date_str, '%Y-%m-%d').date()  
            except:  
                d_date_val = datetime.date.today()  
                  
            description_val = disciplinary_found['description'].values[0]  
          
        with col1:  
            disciplinary_id = st.text_input("Disciplinary ID (max 6 digits)", value=search
