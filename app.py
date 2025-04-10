import os  
import streamlit as st  
import pandas as pd  
import matplotlib.pyplot as plt  
import datetime  
import base64  
from fpdf import FPDF  
import ipywidgets as widgets  
from IPython.display import display, HTML  
  
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

# PDF export function using FPDF  
class PDFReport(FPDF):  
    def header(self):  
        self.set_font('Arial', 'B', 16)  
        self.cell(0, 10, 'Employee Report', 0, 1, 'C')  
        self.ln(10)  
  
    def footer(self):  
        self.set_y(-15)  
        self.set_font('Arial', 'I', 8)  
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')  
  
    def chapter_body(self, df):  
        self.set_font('Arial', '', 12)  
        for index, row in df.iterrows():  
            line = str(row.to_dict())  
            self.multi_cell(0, 10, line)  
        self.ln()  
  
    def create_pdf(self, df, output_filename):  
        self.add_page()  
        self.chapter_body(df)  
        self.output(output_filename)  
  
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
        return df  
    except Exception as e:  
        st.error(f"Error loading file: {e}")  
        return pd.DataFrame({col: [] for col in columns})  
  
# -------------------------------  
# 4. Initialize Session State  
# -------------------------------  
employee_columns = ["employee_id", "first_name", "last_name", "department", "job_title", "email", "phone", "employment_status"]  
meeting_columns = ["meeting_id", "employee_id", "meeting_date", "meeting_time", "Meeting Agenda", "action_items", "notes", "next_meeting_date"]  
disciplinary_columns = ["disciplinary_id", "employee_id", "type", "date", "description"]  
performance_columns = ["review_id", "employee_id", "review_date", "reviewer", "score", "comments"]  
training_columns = ["training_id", "employee_id", "course_name", "start_date", "end_date", "status", "certification"]  
  
if 'employees' not in st.session_state:  
    st.session_state.employees = load_table("employees", employee_columns)  
if 'meetings' not in st.session_state:  
    st.session_state.meetings = load_table("meetings", meeting_columns)  
if 'disciplinary' not in st.session_state:  
    st.session_state.disciplinary = load_table("disciplinary", disciplinary_columns)  
if 'performance' not in st.session_state:  
    st.session_state.performance = load_table("performance", performance_columns)  
if 'training' not in st.session_state:  
    st.session_state.training = load_table("training", training_columns)  
  
# -------------------------------  
# 5. Sidebar Navigation  
# -------------------------------  
st.sidebar.title("Employee Records Tool")  
module = st.sidebar.selectbox(  
    "Select Module",  
    ["Employee Management", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records", "Reports"]  
)  
  
# -------------------------------  
# 6. Module: Employee Management  
# -------------------------------  
if module == "Employee Management":  
    st.header("Employee Management")  
      
    # CSV Upload option  
    uploaded_employees = st.file_uploader("Upload Employees CSV", type="csv", key="employee_upload")  
    if uploaded_employees is not None:  
        st.session_state.employees = load_from_uploaded_file(uploaded_employees, employee_columns)  
        st.success("Employee data uploaded successfully!")  
      
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
            employment_status = st.selectbox("Employment Status", ["Active", "Inactive", "On Leave", "Terminated"])  
          
        submitted_employee = st.form_submit_button("Add/Update Employee")  
        if submitted_employee:  
            if employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            else:  
                new_employee = pd.DataFrame({  
                    "employee_id": [employee_id],  
                    "first_name": [first_name],  
                    "last_name": [last_name],  
                    "department": [department],  
                    "job_title": [job_title],  
                    "email": [email],  
                    "phone": [phone],  
                    "employment_status": [employment_status],  
                })  
                  
                # Check if employee already exists  
                if int(employee_id) in st.session_state.employees['employee_id'].values:  
                    st.session_state.employees = st.session_state.employees[st.session_state.employees['employee_id'] != int(employee_id)]  
                  
                st.session_state.employees = pd.concat([st.session_state.employees, new_employee], ignore_index=True)  
                st.success("Employee added/updated successfully!")  
      
    st.subheader("Employees Table")  
    st.dataframe(st.session_state.employees)  
    st.markdown(get_csv_download_link(st.session_state.employees, "employees.csv", "Download Employees CSV"), unsafe_allow_html=True)  
    if st.button("Save Employee Data"):  
        save_table("employees", st.session_state.employees)  
  
# -------------------------------  
# 7. Module: One-on-One Meetings  
# -------------------------------  
elif module == "One-on-One Meetings":  
    st.header("One-on-One Meetings")  
      
    # CSV Upload option  
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
                    "meeting_id": [meeting_id],  
                    "employee_id": [employee_id],  
                    "meeting_date": [meeting_date.strftime('%Y-%m-%d')],  
                    "meeting_time": [meeting_time.strftime('%H:%M:%S')],  
                    "Meeting Agenda": [meeting_agenda],  
                    "action_items": [action_items],  
                    "notes": [notes],  
                    "next_meeting_date": [next_meeting_date.strftime('%Y-%m-%d')]  
                })  
                st.session_state.meetings = pd.concat([st.session_state.meetings, new_meeting], ignore_index=True)  
                st.success("Meeting recorded successfully!")  
      
    st.subheader("Meetings Table")  
    st.dataframe(st.session_state.meetings)  
    st.markdown(get_csv_download_link(st.session_state.meetings, "meetings.csv", "Download Meetings CSV"), unsafe_allow_html=True)  
    if st.button("Save Meetings Data"):  
        save_table("meetings", st.session_state.meetings)  
  
# -------------------------------  
# 8. Module: Disciplinary Actions  
# -------------------------------  
elif module == "Disciplinary Actions":  
    st.header("Disciplinary Actions")  
    # Updated column structure for disciplinary actions:  
    # ["Period (Date)", "disciplinary_id", "ID", "First Name", "Last Name", "Job Title",  
    #  "Violation", "Interview Date", "Reason", "Comments", "Interviewer", "Decision"]  
      
    # CSV Upload option  
    uploaded_disciplinary = st.file_uploader("Upload Disciplinary CSV", type="csv", key="disciplinary_upload")  
    if uploaded_disciplinary is not None:  
        # When uploading, ensure the file has at least the required columns (if missing, fill with empty string)  
        required_cols = ["Period (Date)", "disciplinary_id", "ID", "First Name", "Last Name",  
                         "Job Title", "Violation", "Interview Date", "Reason", "Comments", "Interviewer", "Decision"]  
        st.session_state.disciplinary = load_from_uploaded_file(uploaded_disciplinary, required_cols)  
        st.success("Disciplinary data uploaded successfully!")  
      
    # Updated Form for Disciplinary Actions  
    with st.form("disciplinary_form"):  
        st.subheader("Record Disciplinary Action")  
          
        col1, col2, col3 = st.columns(3)  
        with col1:  
            period_date = st.date_input("Period (Date)", datetime.date.today())  
            disciplinary_id = st.text_input("Disciplinary ID (max 6 digits)", max_chars=6)  
            emp_id = st.text_input("ID (Employee ID - max 6 digits)", max_chars=6)  
            first_name = st.text_input("First Name")  
        with col2:  
            last_name = st.text_input("Last Name")  
            job_title = st.text_input("Job Title")  
            violation = st.text_input("Violation")  
            interview_date = st.date_input("Interview Date", datetime.date.today())  
        with col3:  
            reason = st.text_area("Reason")  
            comments = st.text_area("Comments")  
            interviewer = st.text_input("Interviewer")  
            decision = st.text_input("Decision")  
          
        submitted_disc = st.form_submit_button("Record Disciplinary Action")  
        if submitted_disc:  
            # Validate numeric inputs for IDs  
            if disciplinary_id == "" or not disciplinary_id.isdigit():  
                st.error("Please enter a valid numeric Disciplinary ID (up to 6 digits).")  
            elif emp_id == "" or not emp_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            else:  
                new_disc = pd.DataFrame({  
                    "Period (Date)": [period_date.strftime('%Y-%m-%d')],  
                    "disciplinary_id": [disciplinary_id],  
                    "ID": [emp_id],  
                    "First Name": [first_name],  
                    "Last Name": [last_name],  
                    "Job Title": [job_title],  
                    "Violation": [violation],  
                    "Interview Date": [interview_date.strftime('%Y-%m-%d')],  
                    "Reason": [reason],  
                    "Comments": [comments],  
                    "Interviewer": [interviewer],  
                    "Decision": [decision]  
                })  
                st.session_state.disciplinary = pd.concat([st.session_state.disciplinary, new_disc], ignore_index=True)  
                st.success("Disciplinary action recorded successfully!")  
      
    st.subheader("Disciplinary Actions Table")  
    st.dataframe(st.session_state.disciplinary)  
    st.markdown(get_csv_download_link(st.session_state.disciplinary, "disciplinary.csv", "Download Disciplinary CSV"), unsafe_allow_html=True)  
    if st.button("Save Disciplinary Data"):  
        save_table("disciplinary", st.session_state.disciplinary)  
# -------------------------------  
# 9. Module: Performance Reviews  
# -------------------------------  
elif module == "Performance Reviews":  
    st.header("Performance Reviews")  
      
    # CSV Upload option  
    uploaded_performance = st.file_uploader("Upload Performance CSV", type="csv", key="performance_upload")  
    if uploaded_performance is not None:  
        st.session_state.performance = load_from_uploaded_file(uploaded_performance, performance_columns)  
        st.success("Performance data uploaded successfully!")  
      
    with st.form("performance_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            review_id = st.text_input("Review ID (max 6 digits)", max_chars=6)  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            review_date = st.date_input("Review Date", datetime.date.today())  
        with col2:  
            reviewer = st.text_input("Reviewer")  
            score = st.slider("Score", 1, 5, 3)  
            comments = st.text_area("Comments")  
        submitted_review = st.form_submit_button("Record Performance Review")  
        if submitted_review:  
            if review_id == "" or not review_id.isdigit():  
                st.error("Please enter a valid numeric Review ID (up to 6 digits).")  
            elif employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            else:  
                new_review = pd.DataFrame({  
                    "review_id": [review_id],  
                    "employee_id": [employee_id],  
                    "review_date": [review_date.strftime('%Y-%m-%d')],  
                    "reviewer": [reviewer],  
                    "score": [score],  
                    "comments": [comments]  
                })  
                st.session_state.performance = pd.concat([st.session_state.performance, new_review], ignore_index=True)  
                st.success("Performance review recorded successfully!")  
      
    st.subheader("Performance Reviews Table")  
    st.dataframe(st.session_state.performance)  
    st.markdown(get_csv_download_link(st.session_state.performance, "performance.csv", "Download Performance CSV"), unsafe_allow_html=True)  
    if st.button("Save Performance Data"):  
        save_table("performance", st.session_state.performance)  
  
# -------------------------------  
# 10. Module: Training Records  
# -------------------------------  
elif module == "Training Records":  
    st.header("Training Records")  
      
    # CSV Upload option  
    uploaded_training = st.file_uploader("Upload Training CSV", type="csv", key="training_upload")  
    if uploaded_training is not None:  
        st.session_state.training = load_from_uploaded_file(uploaded_training, training_columns)  
        st.success("Training data uploaded successfully!")  
      
    with st.form("training_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            training_id = st.text_input("Training ID (max 6 digits)", max_chars=6)  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            course_name = st.text_input("Course Name")  
        with col2:  
            start_date = st.date_input("Start Date", datetime.date.today())  
            end_date = st.date_input("End Date", datetime.date.today() + datetime.timedelta(days=30))  
            status = st.selectbox("Status", ["Not Started", "In Progress", "Completed", "Failed"])  
            certification = st.text_input("Certification")  
        submitted_training = st.form_submit_button("Record Training")  
        if submitted_training:  
            if training_id == "" or not training_id.isdigit():  
                st.error("Please enter a valid numeric Training ID (up to 6 digits).")  
            elif employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            else:  
                new_training = pd.DataFrame({  
                    "training_id": [training_id],  
                    "employee_id": [employee_id],  
                    "course_name": [course_name],  
                    "start_date": [start_date.strftime('%Y-%m-%d')],  
                    "end_date": [end_date.strftime('%Y-%m-%d')],  
                    "status": [status],  
                    "certification": [certification]  
                })  
                st.session_state.training = pd.concat([st.session_state.training, new_training], ignore_index=True)  
                st.success("Training record added successfully!")  
      
    st.subheader("Training Records Table")  
    st.dataframe(st.session_state.training)  
    st.markdown(get_csv_download_link(st.session_state.training, "training.csv", "Download Training CSV"), unsafe_allow_html=True)  
    if st.button("Save Training Data"):  
        save_table("training", st.session_state.training)  
  
# -------------------------------  
# 11. Module: Reports  
# -------------------------------  
def generate_report(data):  
    display(HTML('<h2>Robust Report Module</h2>'))  
      
    # Date range selection widgets  
    today = datetime.date.today()  
    default_from = today - datetime.timedelta(days=30)  
    date_from_picker = widgets.DatePicker(description='Date From', value=default_from)  
    date_to_picker = widgets.DatePicker(description='Date To', value=today)  
      
    # Grouping Options widget  
    grouping_options = widgets.SelectMultiple(  
        options=['Employee', 'Department', 'Job Title'],  
        value=['Employee'],  
        description='Group by',  
        disabled=False  
    )  
      
    # Export option widget  
    export_dropdown = widgets.Dropdown(  
        options=['None', 'CSV', 'PDF'],  
        value='None',  
        description='Export Format',  
        disabled=False,  
    )  
  
    # Button to trigger report generation  
    generate_button = widgets.Button(description='Generate Report')  
    output_area = widgets.Output()  
  
    def on_generate_clicked(b):  
        with output_area:  
            output_area.clear_output()  
            # Retrieve date range  
            date_from = date_from_picker.value  
            date_to = date_to_picker.value  
            if date_from is None or date_to is None:  
                print('Please select both start and end dates.')  
                return  
              
            # Filter dataframe based on date (expects a "date" column)  
            if 'date' in data.columns:  
                df = data.copy()  
                df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date  
                mask = (df['date'] >= date_from) & (df['date'] <= date_to)  
                report_df = df.loc[mask].copy()  
            else:  
                print('No date column found in data. Showing full data.')  
                report_df = data.copy()  
                  
            # Determine grouping based on selected options  
            selected_groupings = list(grouping_options.value)  
            group_cols = []  
            for option in selected_groupings:  
                if option == 'Employee' and 'employee' in report_df.columns:  
                    group_cols.append('employee')  
                elif option == 'Department' and 'department' in report_df.columns:  
                    group_cols.append('department')  
                elif option == 'Job Title' and 'job_title' in report_df.columns:  
                    group_cols.append('job_title')  
                      
            if group_cols:  
                report_grouped = report_df.groupby(group_cols).size().reset_index(name='Count')  
            else:  
                report_grouped = report_df.copy()  
              
            print('Report Data:')  
            display(report_grouped)  
              
            # Plotting report if a "Count" column is available  
            if 'Count' in report_grouped.columns and not report_grouped.empty:  
                fig, ax = plt.subplots(figsize=(12, 8))  
                ax.bar(report_grouped.index.astype(str), report_grouped['Count'], color='#2563EB')  
                ax.set_xlabel('Group', labelpad=10)  
                ax.set_ylabel('Count', labelpad=10)  
                ax.set_title('Report Grouped by ' + ', '.join(selected_groupings), pad=15)  
                ax.set_axisbelow(True)  
                plt.xticks(rotation=45, ha='right')  
                plt.show()  
              
            # Handle export options  
            export_format = export_dropdown.value  
            if export_format == 'CSV':  
                display(get_csv_download_link(report_grouped, 'report.csv', 'Download Report as CSV'))  
            elif export_format == 'PDF':  
                pdf = PDFReport()  
                output_filename = 'report.pdf'  
                pdf.create_pdf(report_grouped, output_filename)  
                with open(output_filename, 'rb') as f:  
                    pdf_data = f.read()  
                b64_pdf = base64.b64encode(pdf_data).decode()  
                pdf_link = '<a href="data:application/octet-stream;base64,' + b64_pdf + '" download="' + output_filename + '">Download Report as PDF</a>'  
                display(HTML(pdf_link))  
                print('PDF report generated successfully')  
            else:  
                print('No export selected.')  
      
    generate_button.on_click(on_generate_clicked)  
      
    # Display the widget layout  
    widget_box = widgets.VBox([  
        date_from_picker,  
        date_to_picker,  
        grouping_options,  
        export_dropdown,  
        generate_button,  
        output_area  
    ])  
    display(widget_box)  
