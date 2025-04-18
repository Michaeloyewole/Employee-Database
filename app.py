import streamlit as st  
import pandas as pd  
import sqlite3  
from datetime import datetime  
import io  
  
# --- CONFIGURATION ---  
st.set_page_config(page_title="Overtime Management App", page_icon="🕒", layout="wide")  
DB_NAME = "overtime_app.db"  
TABLE_NAME = "overtime_entries"  
  
# --- DATABASE FUNCTIONS ---  
def init_db():  
    conn = sqlite3.connect(DB_NAME)  
    c = conn.cursor()  
    c.execute(f"""  
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (  
            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,  
            date TEXT,  
            week_start TEXT,  
            week_end TEXT,  
            employee_id TEXT,  
            name TEXT,  
            department TEXT,  
            roster_group TEXT,  
            overtime_type TEXT,  
            hours REAL,  
            depot TEXT,  
            notes TEXT,  
            reviewed_by TEXT,  
            audit_status TEXT,  
            discrepancy_comments TEXT  
        )  
    """)  
    conn.commit()  
    conn.close()  
  
def insert_entry(entry):  
    conn = sqlite3.connect(DB_NAME)  
    c = conn.cursor()  
    c.execute(f"""  
        INSERT INTO {TABLE_NAME} (  
            date, week_start, week_end, employee_id, name, department, roster_group,  
            overtime_type, hours, depot, notes, reviewed_by, audit_status, discrepancy_comments  
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)  
    """, (  
        entry['date'], entry['week_start'], entry['week_end'], entry['employee_id'], entry['name'],  
        entry['department'], entry['roster_group'], entry['overtime_type'], entry['hours'],  
        entry['depot'], entry['notes'], entry['reviewed_by'], entry['audit_status'], entry['discrepancy_comments']  
    ))  
    conn.commit()  
    conn.close()  
  
def fetch_entries(department=None):  
    conn = sqlite3.connect(DB_NAME)  
    query = f"SELECT * FROM {TABLE_NAME}"  
    params = ()  
    if department:  
        query += " WHERE department = ?"  
        params = (department,)  
    df = pd.read_sql_query(query, conn, params=params)  
    conn.close()  
    return df  
  
def import_data(uploaded_file):  
    df = pd.read_csv(uploaded_file)  
    conn = sqlite3.connect(DB_NAME)  
    df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)  
    conn.close()  
  
def delete_entry(entry_id):  
    conn = sqlite3.connect(DB_NAME)  
    c = conn.cursor()  
    c.execute(f"DELETE FROM {TABLE_NAME} WHERE entry_id = ?", (entry_id,))  
    conn.commit()  
    conn.close()  
  
# --- TWO-PAGE FORM ---  
def entry_form(department):  
    st.subheader("Add Overtime Entry for " + department)  
    # Use department in form keys to ensure uniqueness  
    with st.form("form_page1_" + department, clear_on_submit=False):  
        date = st.date_input("Date")  
        week_start = st.date_input("Week Start")  
        week_end = st.date_input("Week End")  
        employee_id = st.text_input("Employee ID")  
        name = st.text_input("Name")  
        next_page = st.form_submit_button("Next")  
    if next_page:  
        st.session_state["form1_data_" + department] = {  
            "date": str(date),  
            "week_start": str(week_start),  
            "week_end": str(week_end),  
            "employee_id": employee_id,  
            "name": name  
        }  
        st.session_state["show_page2_" + department] = True  
    if st.session_state.get("show_page2_" + department, False):  
        with st.form("form_page2_" + department, clear_on_submit=False):  
            roster_group = st.text_input("Roster Group")  
            overtime_type = st.selectbox("Overtime Type", ["Planned", "Unplanned"])   
            hours = st.number_input("Hours", min_value=0.0, step=0.25)  
            depot = st.text_input("Depot")  
            notes = st.text_area("Notes")  
            reviewed_by = st.text_input("Reviewed By")  
            audit_status = st.selectbox("Audit Status", ["Pending", "Approved", "Rejected"])   
            discrepancy_comments = st.text_area("Discrepancy Comments")  
            submit = st.form_submit_button("Submit")  
        if submit:  
            entry = st.session_state["form1_data_" + department]  
            entry.update({  
                "department": department,  
                "roster_group": roster_group,  
                "overtime_type": overtime_type,  
                "hours": hours,  
                "depot": depot,  
                "notes": notes,  
                "reviewed_by": reviewed_by,  
                "audit_status": audit_status,  
                "discrepancy_comments": discrepancy_comments  
            })  
            insert_entry(entry)  
            st.success("Entry added!")  
            st.session_state["show_page2_" + department] = False  
  
# --- DEPARTMENT TAB WITH DELETE ---  
def department_tab(dept):  
    st.subheader(dept + " Overtime Entries")  
    df = fetch_entries(dept)  
    st.dataframe(df.tail(20))  
    st.markdown("---")  
    # Record deletion UI  
    if not df.empty:  
        st.markdown("#### Delete a Record")  
        entry_ids = df['entry_id'].tolist()  
        selected_id = st.selectbox("Select Entry ID to Delete", entry_ids, key="delete_select_" + dept)  
        if st.button("Delete Selected Entry", key="delete_btn_" + dept):  
            delete_entry(selected_id)  
            st.success("Entry deleted!")  
            st.experimental_rerun()  
    entry_form(dept)  
  
# --- SUMMARY TAB ---  
def summary_tab():  
    st.header("Summary")  
    df = fetch_entries()  
    if not df.empty:  
        st.dataframe(df.tail(20))  
    else:  
        st.info("No entries yet.")  
  
# --- REPORT MODULE ---  
def report_tab():  
    st.subheader("Reports & Visualizations")  
    df = fetch_entries()  
    if df.empty:  
        st.info("No data available for reporting.")  
        return  
    st.write("**Total Overtime Hours by Department**")  
    st.bar_chart(df.groupby("department")["hours"].sum())  
    st.write("**Overtime Hours Trend**")  
    df['date'] = pd.to_datetime(df['date'], errors='coerce')  
    trend = df.groupby("date")["hours"].sum().sort_index()  
    st.line_chart(trend)  
    st.write("**Audit Status Distribution**")  
    st.dataframe(df["audit_status"].value_counts())  
    st.write("**Department & Audit Status Pivot Table**")  
    pivot = pd.pivot_table(df, values="hours", index="department", columns="audit_status", aggfunc="sum", fill_value=0)  
    st.dataframe(pivot)  
  
# --- IMPORT/EXPORT MODULE ---  
def import_export_tab():  
    st.subheader("Import/Export Data")  
    # Export  
    df = fetch_entries()  
    csv = df.to_csv(index=False).encode("utf-8")  
    st.download_button("Download Data as CSV", data=csv, file_name="overtime_data.csv", mime="text/csv")  
    # Import  
    uploaded_file = st.file_uploader("Upload CSV to Import Data", type=["csv"])  
    if uploaded_file is not None:  
        import_data(uploaded_file)  
        st.success("Data imported successfully! Please refresh the page to see updates.")  
  
# --- MAIN APP ---  
init_db()  
st.title("Employee Overtime & Uncovered Duties Tool")  
tabs = st.tabs(["Summary", "Planning", "Ops", "OCC", "Training", "Reports", "Import/Export"])  
  
with tabs[0]:  
    summary_tab()  
with tabs[1]:  
    department_tab("Planning")  
with tabs[2]:  
    department_tab("Ops")  
with tabs[3]:  
    department_tab("OCC")  
with tabs[4]:  
    department_tab("Training")  
with tabs[5]:  
    report_tab()  
with tabs[6]:  
    import_export_tab()  
