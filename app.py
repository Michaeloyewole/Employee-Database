import os  
import streamlit as st  
import pandas as pd  
import matplotlib.pyplot as plt  
from datetime import datetime, timedelta  
import base64  
import sqlite3  
  
# -------------------------------  
# Page Config & Data Directory  
# -------------------------------  
st.set_page_config(  
    page_title="Employee Overtime & Uncovered Duties Tool",  
    page_icon="👥",  
    layout="wide",  
    initial_sidebar_state="expanded"  
)  
  
# -------------------------------  
# SQLite Database Initialization  
# -------------------------------  
def init_sqlite_db():  
    conn = sqlite3.connect('overtime_database.db')  
    cursor = conn.cursor()  
      
    # Overtime table  
    cursor.execute("""  
    CREATE TABLE IF NOT EXISTS overtime (  
        overtime_id TEXT PRIMARY KEY,  
        employee_id TEXT,  
        name TEXT,  
        department TEXT,  
        date TEXT,  
        hours REAL,  
        type TEXT,  
        approved_by TEXT,  
        status TEXT,  
        notes TEXT  
    )  
    """)  
      
    # Uncovered duties table  
    cursor.execute("""  
    CREATE TABLE IF NOT EXISTS uncovered_duties (  
        duty_id TEXT PRIMARY KEY,  
        date TEXT,  
        department TEXT,  
        shift TEXT,  
        hours_uncovered REAL,  
        reason TEXT,  
        status TEXT  
    )  
    """)  
      
    conn.commit()  
    conn.close()  
  
init_sqlite_db()  
  
# -------------------------------  
# Helper Functions  
# -------------------------------  
def load_data(table_name="overtime"):  
    conn = sqlite3.connect('overtime_database.db')  
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)  
    conn.close()  
    if 'date' in df.columns:  
        df['date'] = pd.to_datetime(df['date'])  
    return df  
  
def save_overtime(data):  
    conn = sqlite3.connect('overtime_database.db')  
    cursor = conn.cursor()  
    cursor.execute("""  
    INSERT INTO overtime   
    (overtime_id, employee_id, name, department, date, hours, type, approved_by, status, notes)  
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)  
    """, data)  
    conn.commit()  
    conn.close()  
  
def save_uncovered_duty(data):  
    conn = sqlite3.connect('overtime_database.db')  
    cursor = conn.cursor()  
    cursor.execute("""  
    INSERT INTO uncovered_duties   
    (duty_id, date, department, shift, hours_uncovered, reason, status)  
    VALUES (?, ?, ?, ?, ?, ?, ?)  
    """, data)  
    conn.commit()  
    conn.close()  
  
def update_record(table, id_field, record_id, field, value):  
    conn = sqlite3.connect('overtime_database.db')  
    cursor = conn.cursor()  
    cursor.execute(f"""  
    UPDATE {table}  
    SET {field} = ?  
    WHERE {id_field} = ?  
    """, (value, record_id))  
    conn.commit()  
    conn.close()  
  
def get_download_link(df):  
    csv = df.to_csv(index=False)  
    return st.download_button(  
        label="Download Data",  
        data=csv,  
        file_name="overtime_data.csv",  
        mime="text/csv"  
    )  
  
# -------------------------------  
# Page Functions  
# -------------------------------  
def overtime_entry():  
    st.header("Overtime Entry")  
      
    with st.form("overtime_form"):  
        col1, col2 = st.columns(2)  
          
        with col1:  
            date = st.date_input("Date")  
            employee_id = st.text_input("Employee ID")  
            name = st.text_input("Employee Name")  
            department = st.selectbox(  
                "Department",  
                ["Operations", "OCC", "Training", "Planning"]  
            )  
          
        with col2:  
            hours = st.number_input("Hours", min_value=0.0, step=0.5)  
            overtime_type = st.selectbox(  
                "Type",  
                ["Regular", "Emergency", "Special Project"]  
            )  
            approved_by = st.text_input("Approved By")  
            status = st.selectbox("Status", ["Pending", "Approved", "Rejected"])  
          
        notes = st.text_area("Notes")  
          
        if st.form_submit_button("Submit"):  
            data = (  
                str(datetime.now().timestamp()),  # overtime_id  
                employee_id,  
                name,  
                department,  
                date.strftime("%Y-%m-%d"),  
                hours,  
                overtime_type,  
                approved_by,  
                status,  
                notes  
            )  
            save_overtime(data)  
            st.success("Entry saved successfully!")  
  
def uncovered_duties_entry():  
    st.header("Uncovered Duties Entry")  
      
    with st.form("uncovered_duties_form"):  
        col1, col2 = st.columns(2)  
          
        with col1:  
            date = st.date_input("Date")  
            department = st.selectbox(  
                "Department",  
                ["Operations", "OCC", "Training", "Planning"]  
            )  
            shift = st.selectbox(  
                "Shift",  
                ["Early" , "Late"]  
            )  
          
        with col2:  
            hours_uncovered = st.number_input("Hours Uncovered", min_value=0.0, step=0.5)  
            reason = st.text_input("Reason")  
            status = st.selectbox("Status", ["Open", "Covered", "Cancelled"])  
          
        if st.form_submit_button("Submit"):  
            data = (  
                str(datetime.now().timestamp()),  # duty_id  
                date.strftime("%Y-%m-%d"),  
                department,  
                shift,  
                hours_uncovered,  
                reason,  
                status  
            )  
            save_uncovered_duty(data)  
            st.success("Entry saved successfully!")  
  
def upload_data():  
    st.header("Upload Data")  
      
    tab1, tab2 = st.tabs(["Overtime Data", "Uncovered Duties Data"])  
      
    with tab1:  
        uploaded_file = st.file_uploader("Choose Overtime CSV file", type="csv", key="overtime_upload")  
        if uploaded_file is not None:  
            df = pd.read_csv(uploaded_file)  
            if st.button("Import Overtime Data"):  
                conn = sqlite3.connect('overtime_database.db')  
                df.to_sql('overtime', conn, if_exists='append', index=False)  
                conn.close()  
                st.success("Overtime data imported successfully!")  
      
    with tab2:  
        uploaded_file = st.file_uploader("Choose Uncovered Duties CSV file", type="csv", key="duties_upload")  
        if uploaded_file is not None:  
            df = pd.read_csv(uploaded_file)  
            if st.button("Import Uncovered Duties Data"):  
                conn = sqlite3.connect('overtime_database.db')  
                df.to_sql('uncovered_duties', conn, if_exists='append', index=False)  
                conn.close()  
                st.success("Uncovered duties data imported successfully!")  
  
def view_reports():  
    st.header("Reports")  
      
    # Date filter  
    col1, col2 = st.columns(2)  
    with col1:  
        start_date = st.date_input("From Date", datetime.now() - timedelta(days=30))  
    with col2:  
        end_date = st.date_input("To Date", datetime.now())  
      
    # Department filter  
    department = st.selectbox(  
        "Filter by Department",  
        ["All Departments", "Operations", "Engineering", "HR", "Finance"]  
    )  
      
    # Load and filter data  
    df_overtime = load_data("overtime")  
    df_duties = load_data("uncovered_duties")  
      
    # Apply filters  
    mask_date_ot = (df_overtime['date'].dt.date >= start_date) & (df_overtime['date'].dt.date <= end_date)  
    mask_date_duties = (pd.to_datetime(df_duties['date']).dt.date >= start_date) & (pd.to_datetime(df_duties['date']).dt.date <= end_date)  
      
    df_overtime = df_overtime[mask_date_ot]  
    df_duties = df_duties[mask_date_duties]  
      
    if department != "All Departments":  
        df_overtime = df_overtime[df_overtime['department'] == department]  
        df_duties = df_duties[df_duties['department'] == department]  
      
    # Display metrics  
    col1, col2, col3, col4 = st.columns(4)  
    with col1:  
        st.metric("Total Overtime Hours", f"{df_overtime['hours'].sum():.1f}")  
    with col2:  
        st.metric("Total Entries", len(df_overtime))  
    with col3:  
        st.metric("Uncovered Hours", f"{df_duties['hours_uncovered'].sum():.1f}")  
    with col4:  
        st.metric("Open Uncovered Duties", len(df_duties[df_duties['status'] == 'Open']))  
      
    # Charts  
    st.subheader("Overtime Distribution")  
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))  
      
    # Overtime by department  
    dept_hours = df_overtime.groupby('department')['hours'].sum()  
    dept_hours.plot(kind='pie', ax=ax1, title='Overtime Hours by Department')  
      
    # Uncovered duties by department  
    duties_hours = df_duties.groupby('department')['hours_uncovered'].sum()  
    duties_hours.plot(kind='pie', ax=ax2, title='Uncovered Hours by Department')  
      
    st.pyplot(fig)  
      
    # Data tables with editing capability  
    st.subheader("Overtime Records")  
    edited_overtime = st.data_editor(  
        df_overtime,  
        num_rows="dynamic",  
        use_container_width=True,  
        column_config={  
            "overtime_id": None,  # Hide ID column  
            "date": st.column_config.DateColumn("Date"),  
            "hours": st.column_config.NumberColumn("Hours", min_value=0, max_value=24, step=0.5),  
            "status": st.column_config.SelectboxColumn("Status", options=["Pending", "Approved", "Rejected"])  
        }  
    )  
      
    st.subheader("Uncovered Duties Records")  
    edited_duties = st.data_editor(  
        df_duties,  
        num_rows="dynamic",  
        use_container_width=True,  
        column_config={  
            "duty_id": None,  # Hide ID column  
            "date": st.column_config.DateColumn("Date"),  
            "hours_uncovered": st.column_config.NumberColumn("Hours", min_value=0, max_value=24, step=0.5),  
            "status": st.column_config.SelectboxColumn("Status", options=["Open", "Covered", "Cancelled"])  
        }  
    )  
      
    # Download buttons  
    col1, col2 = st.columns(2)  
    with col1:  
        get_download_link(edited_overtime)  
    with col2:  
        get_download_link(edited_duties)  
  
# -------------------------------  
# Main App  
# -------------------------------  
st.title("Employee Overtime & Uncovered Duties Management System")  
  
# Sidebar navigation  
page = st.sidebar.radio(  
    "Navigation",  
    ["Overtime Entry", "Uncovered Duties Entry", "Upload Data", "Reports"]  
)  
  
if page == "Overtime Entry":  
    overtime_entry()  
elif page == "Uncovered Duties Entry":  
    uncovered_duties_entry()  
elif page == "Upload Data":  
    upload_data()  
else:  
    view_reports()  
  
# Footer  
st.sidebar.markdown("---")  
st.sidebar.markdown("© 2023 Employee Management System")  
