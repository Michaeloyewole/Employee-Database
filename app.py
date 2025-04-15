import os  
import streamlit as st  
import pandas as pd  
import matplotlib.pyplot as plt  
from datetime import datetime, timedelta  
import base64  
import sqlite3  
import uuid  
  
# -------------------------------  
# Page Config & Data Directory  
# -------------------------------  
st.set_page_config(  
    page_title="Employee Overtime Tool",  
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
  
def get_download_link(df, label="Download Data"):  
    csv = df.to_csv(index=False)  
    b64 = base64.b64encode(csv.encode()).decode()  
    href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">{label}</a>'  
    st.markdown(href, unsafe_allow_html=True)  
  
# -------------------------------  
# Overtime Entry Form  
# -------------------------------  
def overtime_entry():  
    st.header("Overtime Entry Form")  
    with st.form("overtime_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            employee_id = st.text_input("Employee ID")  
            name = st.text_input("Name")  
            department = st.selectbox(  
                "Department",  
                ["Operations", "Engineering", "HR", "Finance", "IT", "Sales"]  
            )  
            date = st.date_input("Date")  
        with col2:  
            hours = st.number_input("Hours", min_value=0.0, max_value=24.0, step=0.5)  
            overtime_type = st.selectbox(  
                "Type",  
                ["Regular", "Emergency", "Holiday", "Special Project"]  
            )  
            approved_by = st.text_input("Approved By")  
            status = st.selectbox("Status", ["Pending", "Approved", "Rejected"])  
        notes = st.text_area("Notes")  
        submitted = st.form_submit_button("Submit")  
        if submitted:  
            overtime_id = str(uuid.uuid4())  
            data = (  
                overtime_id, employee_id, name, department,  
                date.strftime("%Y-%m-%d"), hours, overtime_type,  
                approved_by, status, notes  
            )  
            save_overtime(data)  
            st.success("Overtime entry saved successfully!")  
  
# -------------------------------  
# Uncovered Duties Entry Form  
# -------------------------------  
def uncovered_duties_entry():  
    st.header("Uncovered Duties Entry Form")  
    with st.form("duties_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            date = st.date_input("Date")  
            department = st.selectbox(  
                "Department",  
                ["Operations", "Engineering", "HR", "Finance", "IT", "Sales"]  
            )  
            shift = st.selectbox("Shift", ["Morning", "Afternoon", "Night"])  
        with col2:  
            hours_uncovered = st.number_input(  
                "Hours Uncovered",  
                min_value=0.0,  
                max_value=24.0,  
                step=0.5  
            )  
            reason = st.text_area("Reason")  
            status = st.selectbox(  
                "Status",  
                ["Open", "Covered", "Cancelled"]  
            )  
        submitted = st.form_submit_button("Submit")  
        if submitted:  
            duty_id = str(uuid.uuid4())  
            data = (  
                duty_id, date.strftime("%Y-%m-%d"),  
                department, shift, hours_uncovered,  
                reason, status  
            )  
            save_uncovered_duty(data)  
            st.success("Uncovered duty entry saved successfully!")  
  
# -------------------------------  
# Reports Module  
# -------------------------------  
def view_reports():  
    st.header("Reports Dashboard")  
    df_overtime = load_data("overtime")  
    df_duties = load_data("uncovered_duties")  
    if df_overtime.empty and df_duties.empty:  
        st.warning("No data available in the database")  
        return  
  
    # Date filters  
    col1, col2 = st.columns(2)  
    with col1:  
        start_date = st.date_input("From Date", datetime.now() - timedelta(days=30))  
    with col2:  
        end_date = st.date_input("To Date", datetime.now())  
  
    # Department filter  
    all_departments = sorted(list(set(  
        list(df_overtime['department'].dropna().unique()) +   
        list(df_duties['department'].dropna().unique())  
    )))  
    selected_dept = st.selectbox("Select Department", ["All"] + all_departments)  
  
    # Apply filters  
    mask_overtime = (df_overtime['date'].dt.date >= start_date) & (df_overtime['date'].dt.date <= end_date)  
    mask_duties = (df_duties['date'].dt.date >= start_date) & (df_duties['date'].dt.date <= end_date)  
    if selected_dept != "All":  
        mask_overtime &= (df_overtime['department'] == selected_dept)  
        mask_duties &= (df_duties['department'] == selected_dept)  
    df_overtime_filtered = df_overtime[mask_overtime]  
    df_duties_filtered = df_duties[mask_duties]  
  
    # Summary metrics  
    col1, col2, col3 = st.columns(3)  
    with col1:  
        st.metric("Total Overtime Hours", f"{df_overtime_filtered['hours'].sum():.1f}")  
    with col2:  
        st.metric("Total Uncovered Hours", f"{df_duties_filtered['hours_uncovered'].sum():.1f}")  
    with col3:  
        st.metric("Total Records", len(df_overtime_filtered) + len(df_duties_filtered))  
  
    # Overtime pie chart  
    if not df_overtime_filtered.empty and df_overtime_filtered['hours'].notna().any():  
        overtime_by_dept = df_overtime_filtered.groupby('department')['hours'].sum()  
        if not overtime_by_dept.empty and overtime_by_dept.sum() > 0:  
            fig1, ax1 = plt.subplots(figsize=(10, 6))  
            overtime_by_dept.plot(kind='pie', ax=ax1, autopct='%1.1f%%')  
            plt.title('Overtime Hours by Department')  
            st.pyplot(fig1)  
            plt.close()  
        else:  
            st.info("No overtime data to plot for selected filters.")  
    else:  
        st.info("No overtime data to plot for selected filters.")  
  
    # Uncovered duties pie chart  
    if not df_duties_filtered.empty and df_duties_filtered['hours_uncovered'].notna().any():  
        duties_by_dept = df_duties_filtered.groupby('department')['hours_uncovered'].sum()  
        if not duties_by_dept.empty and duties_by_dept.sum() > 0:  
            fig2, ax2 = plt.subplots(figsize=(10, 6))  
            duties_by_dept.plot(kind='pie', ax=ax2, autopct='%1.1f%%')  
            plt.title('Uncovered Hours by Department')  
            st.pyplot(fig2)  
            plt.close()  
        else:  
            st.info("No uncovered duties data to plot for selected filters.")  
    else:  
        st.info("No uncovered duties data to plot for selected filters.")  
  
    # Editable tables  
    st.subheader("Edit Overtime Records")  
    st.data_editor(df_overtime_filtered, use_container_width=True, num_rows="dynamic")  
    st.subheader("Edit Uncovered Duties Records")  
    st.data_editor(df_duties_filtered, use_container_width=True, num_rows="dynamic")  
  
    # Download links  
    get_download_link(df_overtime_filtered, label="Download Filtered Overtime Data")  
    get_download_link(df_duties_filtered, label="Download Filtered Uncovered Duties Data")  
  
# -------------------------------  
# Main App  
# -------------------------------  
st.title("Employee Overtime Management System")  
page = st.sidebar.radio(  
    "Navigation",  
    ["Overtime Entry", "Uncovered Duties Entry", "Reports"]  
)  
if page == "Overtime Entry":  
    overtime_entry()  
elif page == "Uncovered Duties Entry":  
    uncovered_duties_entry()  
else:  
    view_reports()  

# Footer  
st.sidebar.markdown("---")  
st.sidebar.markdown("© 2025 Employee Management System")  
