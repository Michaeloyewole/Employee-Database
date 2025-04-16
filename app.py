import streamlit as st  
import pandas as pd  
import matplotlib.pyplot as plt  
from datetime import datetime, timedelta  
import sqlite3  
import uuid  
import base64  
  
st.set_page_config(  
    page_title="Employee Overtime & Uncovered Duties Tool",  
    page_icon="👥",  
    layout="wide",  
    initial_sidebar_state="expanded"  
)  
  
# Database functions  
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
  
def delete_overtime_record(overtime_id):  
    conn = sqlite3.connect('overtime_database.db')  
    cursor = conn.cursor()  
    cursor.execute("DELETE FROM overtime WHERE overtime_id=?", (overtime_id,))  
    conn.commit()  
    conn.close()  
  
def delete_duty_record(duty_id):  
    conn = sqlite3.connect('overtime_database.db')  
    cursor = conn.cursor()  
    cursor.execute("DELETE FROM uncovered_duties WHERE duty_id=?", (duty_id,))  
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
  
def update_overtime_record(row):  
    conn = sqlite3.connect('overtime_database.db')  
    cursor = conn.cursor()  
    cursor.execute("""  
    UPDATE overtime   
    SET employee_id=?, name=?, department=?, date=?, hours=?, depot=?, approved_by=?, status=?, notes=?  
    WHERE overtime_id=?  
    """, (row['employee_id'], row['name'], row['department'], row['date'],   
          row['hours'], row['depot'], row['approved_by'], row['status'],   
          row['notes'], row['overtime_id']))  
    conn.commit()  
    conn.close()  
  
def update_duty_record(row):  
    conn = sqlite3.connect('overtime_database.db')  
    cursor = conn.cursor()  
    cursor.execute("""  
    UPDATE uncovered_duties   
    SET date=?, department=?, shift=?, hours_uncovered=?, reason=?, status=?  
    WHERE duty_id=?  
    """, (row['date'], row['department'], row['shift'], row['hours_uncovered'],  
          row['reason'], row['status'], row['duty_id']))  
    conn.commit()  
    conn.close()  
  
def get_download_link(df, text):  
    csv = df.to_csv(index=False)  
    b64 = base64.b64encode(csv.encode()).decode()  
    href = f'data:file/csv;base64,{b64}'  
    return f'<a href="{href}" download="data.csv">{text}</a>'  
  
# Initialize database  
init_sqlite_db()  
  
# Main app  
def main():  
    st.title("Employee Overtime & Uncovered Duties Management")  
      
    tab1, tab2, tab3 = st.tabs(["Submit Records", "View Reports", "Analytics"])  
      
    with tab1:  
        col1, col2 = st.columns(2)  
          
        with col1:  
            st.subheader("Submit Overtime")  
            employee_id = st.text_input("Employee ID", key="ot_emp_id")  
            name = st.text_input("Name", key="ot_name")  
            department = st.selectbox("Department", ["Operations", "Maintenance", "Customer Service", "Administration"])  
            date = st.date_input("Date", key="ot_date")  
            hours = st.number_input("Hours", min_value=0.0, max_value=24.0, step=0.5, key="ot_hours")  
            depot = st.selectbox("Depot", ["West", "East"])  
            approved_by = st.text_input("Approved By", key="ot_approved")  
            status = st.selectbox("Status", ["Pending", "Approved", "Rejected"], key="ot_status")  
            notes = st.text_area("Notes", key="ot_notes")  
              
            if st.button("Submit Overtime"):  
                overtime_id = str(uuid.uuid4())  
                data = (overtime_id, employee_id, name, department, date.strftime("%Y-%m-%d"),   
                       hours, depot, approved_by, status, notes)  
                save_overtime(data)  
                st.success("Overtime record submitted successfully!")  
                  
        with col2:  
            st.subheader("Submit Uncovered Duties")  
            duty_date = st.date_input("Date", key="duty_date")  
            duty_dept = st.selectbox("Department", ["Operations", "Maintenance", "Customer Service", "Administration"], key="duty_dept")  
            shift = st.selectbox("Shift", ["Morning", "Afternoon", "Night"])  
            hours_uncovered = st.number_input("Hours Uncovered", min_value=0.0, max_value=24.0, step=0.5)  
            reason = st.text_area("Reason")  
            duty_status = st.selectbox("Status", ["Open", "Covered", "Cancelled"], key="duty_status")  
              
            if st.button("Submit Uncovered Duty"):  
                duty_id = str(uuid.uuid4())  
                data = (duty_id, duty_date.strftime("%Y-%m-%d"), duty_dept, shift,   
                       hours_uncovered, reason, duty_status)  
                save_uncovered_duty(data)  
                st.success("Uncovered duty record submitted successfully!")  
      
    with tab2:  
        # Load data  
        df_overtime = load_data('overtime')  
        df_duties = load_data('uncovered_duties')  
          
        # Filters  
        st.sidebar.header("Filters")  
        date_range = st.sidebar.date_input(  
            "Select Date Range",  
            [df_overtime['date'].min(), df_overtime['date'].max()]  
        )  
        departments = st.sidebar.multiselect(  
            "Select Departments",  
            df_overtime['department'].unique()  
        )  
        depots = st.sidebar.multiselect(  
            "Select Depots",  
            df_overtime['depot'].unique()  
        )  
          
        # Apply filters  
        mask_overtime = (df_overtime['date'].dt.date >= date_range[0]) & (df_overtime['date'].dt.date <= date_range[1])  
        if departments:  
            mask_overtime &= df_overtime['department'].isin(departments)  
        if depots:  
            mask_overtime &= df_overtime['depot'].isin(depots)  
              
        df_overtime_filtered = df_overtime[mask_overtime]  
        df_duties_filtered = df_duties[  
            df_duties['date'].dt.date.between(date_range[0], date_range[1])  
        ]  
          
        # Summary metrics  
        col1, col2, col3 = st.columns(3)  
        with col1:  
            st.metric("Total Overtime Hours", f"{df_overtime_filtered['hours'].sum():.1f}")  
        with col2:  
            st.metric("Total Uncovered Hours", f"{df_duties_filtered['hours_uncovered'].sum():.1f}")  
        with col3:  
            st.metric("Total Records", len(df_overtime_filtered) + len(df_duties_filtered))  
          
        # Add Delete column and display editable tables  
        st.subheader("Overtime Records (Editable & Deletable)")  
        df_overtime_filtered['Delete'] = False  
        edited_overtime = st.data_editor(  
            df_overtime_filtered,  
            use_container_width=True,  
            num_rows="dynamic",  
            key="overtime_editor"  
        )  
          
        st.subheader("Uncovered Duties Records (Editable & Deletable)")  
        df_duties_filtered['Delete'] = False  
        edited_duties = st.data_editor(  
            df_duties_filtered,  
            use_container_width=True,  
            num_rows="dynamic",  
            key="duties_editor"  
        )  
          
        # Save and Delete buttons  
        col1, col2 = st.columns(2)  
        with col1:  
            if st.button("Save Changes"):  
                try:  
                    for idx, row in edited_overtime.iterrows():  
                        if not row['Delete']:  
                            update_overtime_record(row)  
                    for idx, row in edited_duties.iterrows():  
                        if not row['Delete']:  
                            update_duty_record(row)  
                    st.success("Changes saved successfully!")  
                    st.experimental_rerun()  
                except Exception as e:  
                    st.error(f"Error saving changes: {str(e)}")  
          
        with col2:  
            if st.button("Delete Selected Records"):  
                try:  
                    for idx, row in edited_overtime[edited_overtime['Delete']].iterrows():  
                        delete_overtime_record(row['overtime_id'])  
                    for idx, row in edited_duties[edited_duties['Delete']].iterrows():  
                        delete_duty_record(row['duty_id'])  
                    st.success("Selected records deleted successfully!")  
                    st.experimental_rerun()  
                except Exception as e:  
                    st.error(f"Error deleting records: {str(e)}")  
          
        # Download buttons  
        col1, col2 = st.columns(2)  
        with col1:  
            st.markdown(get_download_link(  
                edited_overtime[~edited_overtime['Delete']],   
                "Download Overtime Data"  
            ), unsafe_allow_html=True)  
        with col2:  
            st.markdown(get_download_link(  
                edited_duties[~edited_duties['Delete']],   
                "Download Uncovered Duties Data"  
            ), unsafe_allow_html=True)  
      
    with tab3:  
        if not df_overtime_filtered.empty:  
            # Overtime by Depot pie chart  
            st.subheader("Overtime Distribution by Depot")  
            overtime_by_depot = df_overtime_filtered.groupby('depot')['hours'].sum()  
            fig1, ax1 = plt.subplots(figsize=(8, 6))  
            plt.style.use('default')  
            colors = ['#2563EB', '#24EB84']  
            overtime_by_depot.plot(kind='pie', autopct='%1.1f%%', colors=colors)  
            plt.title('Overtime Hours by Depot', pad=15)  
            plt.ylabel('')  
            st.pyplot(fig1)  
            plt.close()  
              
            # Overtime by Department bar chart  
            st.subheader("Overtime by Department and Depot")  
            overtime_by_dept = df_overtime_filtered.pivot_table(  
                values='hours',  
                index='department',  
                columns='depot',  
                aggfunc='sum'  
            ).fillna(0)  
              
            fig2, ax2 = plt.subplots(figsize=(12, 6))  
            overtime_by_dept.plot(kind='bar', ax=ax2)  
            plt.title('Overtime Hours by Department and Depot', pad=15)  
            plt.xlabel('Department', labelpad=10)  
            plt.ylabel('Hours', labelpad=10)  
            plt.legend(title='Depot')  
            plt.xticks(rotation=45)  
            plt.tight_layout()  
            st.pyplot(fig2)  
            plt.close()  
  
if __name__ == "__main__":  
    main()  
