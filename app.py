import streamlit as st  
import pandas as pd  
import matplotlib.pyplot as plt  
from datetime import datetime, timedelta  
import sqlite3  
import uuid  
import base64  
  
# Page configuration  
st.set_page_config(  
    page_title="Employee Overtime & Uncovered Duties Tool",  
    page_icon="👥",  
    layout="wide",  
    initial_sidebar_state="expanded"  
)  
  
# Database initialization  
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
        depot TEXT,  
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
    (overtime_id, employee_id, name, department, date, hours, depot, approved_by, status, notes)  
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
  
def get_download_link(df, text):  
    """Generate a download link for a DataFrame"""  
    csv = df.to_csv(index=False)  
    b64 = base64.b64encode(csv.encode()).decode()  
    href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">{text}</a>'  
    return href  
  
def overtime_entry():  
    st.header("Overtime Entry Form")  
      
    # Create two columns for side-by-side layout  
    col1, col2 = st.columns(2)  
      
    # Shared variables for both forms  
    shared_data = {}  
      
    with col1:  
        with st.form("overtime_form_left"):  
            shared_data['employee_id'] = st.text_input("Employee ID")  
            shared_data['name'] = st.text_input("Name")  
            shared_data['department'] = st.text_input("Department")  
            shared_data['depot'] = st.selectbox("Depot", ["West", "East"])  
            shared_data['date'] = st.date_input("Date")  
              
            if st.form_submit_button("Submit Left Form"):  
                overtime_id = str(uuid.uuid4())  
                data = (overtime_id, shared_data['employee_id'], shared_data['name'],   
                       shared_data['department'], shared_data['date'].strftime('%Y-%m-%d'),   
                       shared_data.get('hours', 0), shared_data['depot'],  
                       shared_data.get('approved_by', ''), shared_data.get('status', 'Pending'),   
                       shared_data.get('notes', ''))  
                save_overtime(data)  
                st.success("Overtime record saved successfully!")  
      
    with col2:  
        with st.form("overtime_form_right"):  
            shared_data['hours'] = st.number_input("Hours", min_value=0.0, step=0.5)  
            shared_data['approved_by'] = st.text_input("Approved By")  
            shared_data['status'] = st.selectbox("Status", ["Pending", "Approved", "Rejected"])  
            shared_data['notes'] = st.text_area("Notes")  
              
            if st.form_submit_button("Submit Right Form"):  
                overtime_id = str(uuid.uuid4())  
                data = (overtime_id, shared_data['employee_id'], shared_data['name'],   
                       shared_data['department'], shared_data['date'].strftime('%Y-%m-%d'),   
                       shared_data['hours'], shared_data['depot'],  
                       shared_data['approved_by'], shared_data['status'],   
                       shared_data['notes'])  
                save_overtime(data)  
                st.success("Overtime record saved successfully!")  
  
def uncovered_duties_entry():  
    st.header("Uncovered Duties Entry Form")  
      
    col1, col2 = st.columns(2)  
      
    with col1:  
        with st.form("duties_form_left"):  
            date = st.date_input("Date")  
            department = st.text_input("Department")  
            shift = st.selectbox("Shift", ["Morning", "Afternoon", "Night"])  
              
            if st.form_submit_button("Submit Left Form"):  
                duty_id = str(uuid.uuid4())  
                data = (duty_id, date.strftime('%Y-%m-%d'), department, shift,  
                       hours_uncovered, reason, status)  
                save_uncovered_duty(data)  
                st.success("Uncovered duty record saved successfully!")  
      
    with col2:  
        with st.form("duties_form_right"):  
            hours_uncovered = st.number_input("Hours Uncovered", min_value=0.0, step=0.5)  
            reason = st.text_area("Reason")  
            status = st.selectbox("Status", ["Open", "Covered", "Cancelled"])  
              
            if st.form_submit_button("Submit Right Form"):  
                duty_id = str(uuid.uuid4())  
                data = (duty_id, date.strftime('%Y-%m-%d'), department, shift,  
                       hours_uncovered, reason, status)  
                save_uncovered_duty(data)  
                st.success("Uncovered duty record saved successfully!")  
  
def view_reports():  
    st.header("Reports Dashboard")  
    df_overtime = load_data("overtime")  
    df_duties = load_data("uncovered_duties")  
      
    if df_overtime.empty and df_duties.empty:  
        st.warning("No data available in the database")  
        return  
  
    # Create three columns for filters  
    col1, col2, col3 = st.columns(3)  
      
    with col1:  
        start_date = st.date_input("From Date", datetime.now() - timedelta(days=30))  
    with col2:  
        end_date = st.date_input("To Date", datetime.now())  
    with col3:  
        depot_options = ["Both"] + sorted(df_overtime['depot'].dropna().unique().tolist())  
        selected_depot = st.selectbox("Depot", depot_options)  
  
    # Apply filters  
    mask_overtime = (df_overtime['date'].dt.date >= start_date) & (df_overtime['date'].dt.date <= end_date)  
    mask_duties = (df_duties['date'].dt.date >= start_date) & (df_duties['date'].dt.date <= end_date)  
      
    if selected_depot != "Both":  
        mask_overtime &= (df_overtime['depot'] == selected_depot)  
      
    df_overtime_filtered = df_overtime[mask_overtime].copy()  
    df_duties_filtered = df_duties[mask_duties].copy()  
  
    # Display metrics  
    col1, col2, col3 = st.columns(3)  
    with col1:  
        st.metric("Total Overtime Hours", f"{df_overtime_filtered['hours'].sum():.1f}")  
    with col2:  
        st.metric("Total Uncovered Hours", f"{df_duties_filtered['hours_uncovered'].sum():.1f}")  
    with col3:  
        st.metric("Total Records", len(df_overtime_filtered) + len(df_duties_filtered))  
  
    # Visualizations  
    if not df_overtime_filtered.empty:  
        # Overtime by Depot Pie Chart  
        st.subheader("Overtime Distribution by Depot")  
        overtime_by_depot = df_overtime_filtered.groupby('depot')['hours'].sum()  
          
        fig1, ax1 = plt.subplots(figsize=(10, 6))  
        plt.style.use('default')  
        colors = ['#2563EB', '#24EB84']  
        overtime_by_depot.plot(kind='pie', autopct='%1.1f%%', colors=colors, ax=ax1)  
        plt.title('Overtime Hours by Depot', pad=15, fontsize=14)  
        plt.ylabel('')  
        st.pyplot(fig1)  
        plt.close()  
  
        # Overtime by Department and Depot  
        st.subheader("Overtime by Department and Depot")  
        overtime_by_dept_depot = df_overtime_filtered.groupby(['depot', 'department'])['hours'].sum().unstack()  
          
        fig2, ax2 = plt.subplots(figsize=(12, 6))  
        overtime_by_dept_depot.plot(kind='bar', ax=ax2)  
        plt.title('Overtime Hours by Department and Depot', pad=15, fontsize=14)  
        plt.xlabel('Depot', labelpad=10)  
        plt.ylabel('Hours', labelpad=10)  
        plt.xticks(rotation=45)  
        plt.legend(title='Department', bbox_to_anchor=(1.05, 1), loc='upper left')  
        plt.tight_layout()  
        st.pyplot(fig2)  
        plt.close()  
  
    # Data Tables  
    st.subheader("Overtime Records")  
    st.dataframe(df_overtime_filtered)  
      
    st.subheader("Uncovered Duties Records")  
    st.dataframe(df_duties_filtered)  
  
    # Download buttons  
    col1, col2 = st.columns(2)  
    with col1:  
        st.markdown(get_download_link(df_overtime_filtered, "Download Overtime Data"), unsafe_allow_html=True)  
    with col2:  
        st.markdown(get_download_link(df_duties_filtered, "Download Uncovered Duties Data"), unsafe_allow_html=True)  
  
def upload_module():  
    st.header("Upload Data")  
      
    upload_type = st.radio("Select Upload Type", ["Overtime", "Uncovered Duties"])  
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")  
      
    if uploaded_file is not None:  
        try:  
            df = pd.read_csv(uploaded_file)  
            if upload_type == "Overtime":  
                for _, row in df.iterrows():  
                    overtime_id = str(uuid.uuid4())  
                    data = (overtime_id,) + tuple(row)  
                    save_overtime(data)  
            else:  
                for _, row in df.iterrows():  
                    duty_id = str(uuid.uuid4())  
                    data = (duty_id,) + tuple(row)  
                    save_uncovered_duty(data)  
            st.success(f"{upload_type} data uploaded successfully!")  
        except Exception as e:  
            st.error(f"Error processing file: {e}")  
  
def main():  
    st.title("Employee Overtime & Uncovered Duties Management System")  
      
    # Navigation  
    page = st.sidebar.radio(  
        "Navigation",  
        ["Overtime Entry", "Uncovered Duties Entry", "Upload Data", "Reports"]  
    )  
      
    # Page routing  
    if page == "Overtime Entry":  
        overtime_entry()  
    elif page == "Uncovered Duties Entry":  
        uncovered_duties_entry()  
    elif page == "Upload Data":  
        upload_module()  
    else:  
        view_reports()  
  
if __name__ == "__main__":  
    init_sqlite_db()  
    main()  
