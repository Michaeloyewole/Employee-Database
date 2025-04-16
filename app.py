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
    st.title("Reports")  
      
    # Load data  
    df_overtime = load_data('overtime')  
    df_duties = load_data('uncovered_duties')  
      
    # Ensure hours columns are numeric and handle any non-numeric values  
    df_overtime['hours'] = pd.to_numeric(df_overtime['hours'], errors='coerce').fillna(0)  
    df_duties['hours_uncovered'] = pd.to_numeric(df_duties['hours_uncovered'], errors='coerce').fillna(0)  
      
    # Create two columns for the charts  
    col1, col2 = st.columns(2)  
      
    with col1:  
        # Overtime Hours by Department  
        overtime_hours = df_overtime.groupby('department')['hours'].sum()  
          
        # Only plot if we have data  
        if len(overtime_hours) > 0 and overtime_hours.sum() > 0:  
            fig1, ax1 = plt.subplots(figsize=(10, 6))  
            plt.style.use('default')  
              
            # Plot the pie chart  
            patches, texts, autotexts = ax1.pie(  
                overtime_hours,  
                labels=overtime_hours.index,  
                autopct='%1.1f%%',  
                colors=['#2563EB', '#24EB84', '#B2EB24', '#EB3424', '#D324EB'][:len(overtime_hours)]  
            )  
              
            # Set title and display  
            ax1.set_title('Overtime Hours by Department', pad=15)  
            st.pyplot(fig1)  
            plt.close()  
        else:  
            st.warning("No overtime hours data available to plot")  
      
    with col2:  
        # Uncovered Hours by Department  
        duties_hours = df_duties.groupby('department')['hours_uncovered'].sum()  
          
        # Only plot if we have data  
        if len(duties_hours) > 0 and duties_hours.sum() > 0:  
            fig2, ax2 = plt.subplots(figsize=(10, 6))  
              
            # Plot the pie chart  
            patches, texts, autotexts = ax2.pie(  
                duties_hours,  
                labels=duties_hours.index,  
                autopct='%1.1f%%',  
                colors=['#2563EB', '#24EB84', '#B2EB24', '#EB3424', '#D324EB'][:len(duties_hours)]  
            )  
              
            # Set title and display  
            ax2.set_title('Uncovered Hours by Department', pad=15)  
            st.pyplot(fig2)  
            plt.close()  
        else:  
            st.warning("No uncovered duties data available to plot")  
      
    # Summary statistics  
    st.subheader("Summary Statistics")  
      
    # Create summary tables  
    summary_overtime = df_overtime.groupby('department').agg({  
        'hours': ['sum', 'mean', 'count']  
    }).round(2)  
      
    summary_duties = df_duties.groupby('department').agg({  
        'hours_uncovered': ['sum', 'mean', 'count']  
    }).round(2)  
      
    # Display summary tables  
    col3, col4 = st.columns(2)  
      
    with col3:  
        st.write("Overtime Summary by Department")  
        if not summary_overtime.empty:  
            st.dataframe(summary_overtime)  
        else:  
            st.warning("No overtime data available")  
      
    with col4:  
        st.write("Uncovered Duties Summary by Department")  
        if not summary_duties.empty:  
            st.dataframe(summary_duties)  
        else:  
            st.warning("No uncovered duties data available")  
      
    # Monthly trend analysis  
    st.subheader("Monthly Trends")  
      
    if not df_overtime.empty or not df_duties.empty:  
        # Create monthly trends  
        df_overtime['month'] = pd.to_datetime(df_overtime['date']).dt.to_period('M')  
        df_duties['month'] = pd.to_datetime(df_duties['date']).dt.to_period('M')  
          
        monthly_overtime = df_overtime.groupby('month')['hours'].sum()  
        monthly_duties = df_duties.groupby('month')['hours_uncovered'].sum()  
          
        # Plot trends  
        fig3, ax3 = plt.subplots(figsize=(12, 6))  
          
        if not monthly_overtime.empty:  
            monthly_overtime.plot(kind='line', marker='o', ax=ax3, label='Overtime Hours', color='#2563EB')  
        if not monthly_duties.empty:  
            monthly_duties.plot(kind='line', marker='s', ax=ax3, label='Uncovered Hours', color='#24EB84')  
          
        plt.title('Monthly Hours Trend', pad=15)  
        plt.xlabel('Month', labelpad=10)  
        plt.ylabel('Hours', labelpad=10)  
        plt.legend()  
        plt.grid(True, alpha=0.3)  
        plt.xticks(rotation=45)  
        plt.tight_layout()  
        st.pyplot(fig3)  
        plt.close()  
    else:  
        st.warning("No data available for trend analysis")  
  
   if st.button("Download Report"):  
        csv = df_overtime.to_csv(index=False)  
        b64 = base64.b64encode(csv.encode()).decode()  
        href = f'data:file/csv;base64,{b64}'  
        st.markdown(f'<a href="{href}" download="overtime_report.csv">Download CSV Report</a>', unsafe_allow_html=True)  
  
# -------------------------------  
# Main App  
# -------------------------------  
st.title("Employee Overtime Management System")  
  
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
st.sidebar.markdown("© 2025 Employee Management System")  

