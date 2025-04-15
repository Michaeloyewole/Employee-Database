import streamlit as st  
import pandas as pd  
import matplotlib.pyplot as plt  
from datetime import datetime, timedelta  
import sqlite3  
import uuid  
import io  
  
st.set_page_config(  
    page_title="Employee Overtime & Uncovered Duties Tool",  
    page_icon="👥",  
    layout="wide",  
    initial_sidebar_state="expanded"  
)  
  
# --- Database Functions ---  
def init_sqlite_db():  
    conn = sqlite3.connect('overtime_database.db')  
    cursor = conn.cursor()  
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
    )""")  
    cursor.execute("""  
    CREATE TABLE IF NOT EXISTS uncovered_duties (  
        duty_id TEXT PRIMARY KEY,  
        date TEXT,  
        department TEXT,  
        shift TEXT,  
        hours_uncovered REAL,  
        reason TEXT,  
        status TEXT  
    )""")  
    conn.commit()  
    conn.close()  
  
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
  
def update_overtime_record(data):  
    conn = sqlite3.connect('overtime_database.db')  
    cursor = conn.cursor()  
    cursor.execute("""  
        UPDATE overtime   
        SET employee_id=?, name=?, department=?, date=?, hours=?, type=?,   
            approved_by=?, status=?, notes=?  
        WHERE overtime_id=?  
    """, (  
        data['employee_id'], data['name'], data['department'],   
        data['date'], data['hours'], data['type'],  
        data['approved_by'], data['status'], data['notes'],  
        data['overtime_id']  
    ))  
    conn.commit()  
    conn.close()  
  
def update_duty_record(data):  
    conn = sqlite3.connect('overtime_database.db')  
    cursor = conn.cursor()  
    cursor.execute("""  
        UPDATE uncovered_duties   
        SET date=?, department=?, shift=?, hours_uncovered=?,   
            reason=?, status=?  
        WHERE duty_id=?  
    """, (  
        data['date'], data['department'], data['shift'],  
        data['hours_uncovered'], data['reason'], data['status'],  
        data['duty_id']  
    ))  
    conn.commit()  
    conn.close()  
  
def get_download_link(df, label):  
    csv = df.to_csv(index=False)  
    b64 = base64.b64encode(csv.encode()).decode()  
    href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">{label}</a>'  
    return href  
  
# --- Entry Forms ---  
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
  
# --- Upload Module ---  
def upload_module():  
    st.header("Upload Data")  
    upload_type = st.radio("Select Upload Type", ["Overtime", "Uncovered Duties"])  
      
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")  
    if uploaded_file is not None:  
        try:  
            df = pd.read_csv(uploaded_file)  
            st.write("Preview of uploaded data:")  
            st.write(df.head())  
              
            if st.button("Confirm Upload"):  
                if upload_type == "Overtime":  
                    for _, row in df.iterrows():  
                        data = (str(uuid.uuid4()), row['employee_id'], row['name'],  
                               row['department'], row['date'], row['hours'],  
                               row['type'], row['approved_by'], row['status'],  
                               row['notes'])  
                        save_overtime(data)  
                else:  
                    for _, row in df.iterrows():  
                        data = (str(uuid.uuid4()), row['date'], row['department'],  
                               row['shift'], row['hours_uncovered'], row['reason'],  
                               row['status'])  
                        save_uncovered_duty(data)  
                st.success(f"{upload_type} data uploaded successfully!")  
        except Exception as e:  
            st.error(f"Error processing file: {e}")  
  
# --- Reports ---  
def view_reports():  
    st.header("Reports Dashboard")  
    df_overtime = load_data("overtime")  
    df_duties = load_data("uncovered_duties")  
      
    if df_overtime.empty and df_duties.empty:  
        st.warning("No data available in the database")  
        return  
  
    col1, col2 = st.columns(2)  
    with col1:  
        start_date = st.date_input("From Date", datetime.now() - timedelta(days=30))  
    with col2:  
        end_date = st.date_input("To Date", datetime.now())  
  
    all_departments = sorted(list(set(df_overtime['department'].dropna().unique()).union(  
        set(df_duties['department'].dropna().unique())  
    )))  
    selected_dept = st.selectbox("Select Department", ["All"] + all_departments)  
  
    mask_overtime = (df_overtime['date'].dt.date >= start_date) & (df_overtime['date'].dt.date <= end_date)  
    mask_duties = (df_duties['date'].dt.date >= start_date) & (df_duties['date'].dt.date <= end_date)  
      
    if selected_dept != "All":  
        mask_overtime &= (df_overtime['department'] == selected_dept)  
        mask_duties &= (df_duties['department'] == selected_dept)  
      
    df_overtime_filtered = df_overtime[mask_overtime].copy()  
    df_duties_filtered = df_duties[mask_duties].copy()  
  
    col1, col2, col3 = st.columns(3)  
    with col1:  
        st.metric("Total Overtime Hours", f"{df_overtime_filtered['hours'].sum():.1f}")  
    with col2:  
        st.metric("Total Uncovered Hours", f"{df_duties_filtered['hours_uncovered'].sum():.1f}")  
    with col3:  
        st.metric("Total Records", len(df_overtime_filtered) + len(df_duties_filtered))  
  
    if not df_overtime_filtered.empty and df_overtime_filtered['hours'].sum() > 0:  
        overtime_by_dept = df_overtime_filtered.groupby('department')['hours'].sum()  
        if not overtime_by_dept.empty:  
            fig1, ax1 = plt.subplots(figsize=(10, 6))  
            overtime_by_dept.plot(kind='pie', ax=ax1, autopct='%1.1f%%')  
            plt.title('Overtime Hours by Department')  
            st.pyplot(fig1)  
            plt.close()  
  
    if not df_duties_filtered.empty and df_duties_filtered['hours_uncovered'].sum() > 0:  
        duties_by_dept = df_duties_filtered.groupby('department')['hours_uncovered'].sum()  
        if not duties_by_dept.empty:  
            fig2, ax2 = plt.subplots(figsize=(10, 6))  
            duties_by_dept.plot(kind='pie', ax=ax2, autopct='%1.1f%%')  
            plt.title('Uncovered Hours by Department')  
            st.pyplot(fig2)  
            plt.close()  
  
    st.subheader("Overtime Records")  
    edited_overtime = st.data_editor(  
        df_overtime_filtered,  
        use_container_width=True,  
        num_rows="dynamic",  
        key="overtime_editor"  
    )  
      
    st.subheader("Uncovered Duties Records")  
    edited_duties = st.data_editor(  
        df_duties_filtered,  
        use_container_width=True,  
        num_rows="dynamic",  
        key="duties_editor"  
    )  
  
    if st.button("Save Changes"):  
        try:  
            for idx, row in edited_overtime.iterrows():  
                update_overtime_record(row.to_dict())  
            for idx, row in edited_duties.iterrows():  
                update_duty_record(row.to_dict())  
            st.success("Changes saved successfully!")  
            st.experimental_rerun()  
        except Exception as e:  
            st.error(f"Error saving changes: {str(e)}")  
  
    st.markdown(get_download_link(edited_overtime, "Download Overtime Data"), unsafe_allow_html=True)  
    st.markdown(get_download_link(edited_duties, "Download Uncovered Duties Data"), unsafe_allow_html=True)  
  
# --- Main App ---  
def main():  
    st.title("Employee Overtime Management System")  
      
    page = st.sidebar.radio(  
        "Navigation",  
        ["Overtime Entry", "Uncovered Duties Entry", "Upload Data", "Reports"]  
    )  
      
    if page == "Overtime Entry":  
        overtime_entry()  
    elif page == "Uncovered Duties Entry":  
        uncovered_duties_entry()  
    elif page == "Upload Data":  
        upload_module()  
    else:  
        view_reports()  
  
if __name__ == "__main__":  
    main()  
