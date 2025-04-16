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
    if department:  
        query += " WHERE department = ?"  
        df = pd.read_sql_query(query, conn, params=(department,))  
    else:  
        df = pd.read_sql_query(query, conn)  
    conn.close()  
    df.rename(columns={"discrepancy_comments": "Discrepancy/Comments", "reviewed_by": "Reviewed By", "audit_status": "Audit Status"}, inplace=True)  
    return df  
  
def import_data(file):  
    df = pd.read_csv(file)  
    conn = sqlite3.connect(DB_NAME)  
    df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)  
    conn.close()  
  
def export_data():  
    df = fetch_entries()  
    return df  
  
def update_audit_status(entry_id, new_status):  
    conn = sqlite3.connect(DB_NAME)  
    c = conn.cursor()  
    c.execute(f"UPDATE {TABLE_NAME} SET audit_status = ? WHERE entry_id = ?", (new_status, entry_id))  
    conn.commit()  
    conn.close()  
  
# --- TWO-PAGE FORM ---  
def entry_form(department=None):  
    st.subheader("Add Overtime Entry")  
    if "form_page" not in st.session_state:  
        st.session_state["form_page"] = 1  
        st.session_state["form_data"] = {}  
  
    if st.session_state["form_page"] == 1:  
        with st.form("form_page1", clear_on_submit=False):  
            date = st.date_input("Date", value=datetime.today())  
            week_start = st.date_input("Week Start", value=datetime.today())  
            week_end = st.date_input("Week End", value=datetime.today())  
            employee_id = st.text_input("Employee ID")  
            name = st.text_input("Name")  
            dept = department or st.selectbox("Department", ["Planning", "Ops", "OCC", "Training"])  
            roster_group = st.text_input("Roster Group")  
            next1 = st.form_submit_button("Next")  
            if next1:  
                st.session_state["form_data"].update({  
                    "date": str(date),  
                    "week_start": str(week_start),  
                    "week_end": str(week_end),  
                    "employee_id": employee_id,  
                    "name": name,  
                    "department": dept,  
                    "roster_group": roster_group  
                })  
                st.session_state["form_page"] = 2  
                st.experimental_rerun()  
    elif st.session_state["form_page"] == 2:  
        with st.form("form_page2", clear_on_submit=False):  
            overtime_type = st.text_input("Overtime Type")  
            hours = st.number_input("Hours", min_value=0.0, step=0.5)  
            depot = st.text_input("Depot")  
            notes = st.text_area("Notes")  
            reviewed_by = st.text_input("Reviewed By")  
            audit_status = st.selectbox("Audit Status", ["", "Pending", "Approved", "Rejected"])  
            discrepancy_comments = st.text_area("Discrepancy/Comments")  
            submit2 = st.form_submit_button("Submit")  
            back = st.form_submit_button("Back")  
            if back:  
                st.session_state["form_page"] = 1  
                st.experimental_rerun()  
            if submit2:  
                st.session_state["form_data"].update({  
                    "overtime_type": overtime_type,  
                    "hours": hours,  
                    "depot": depot,  
                    "notes": notes,  
                    "reviewed_by": reviewed_by,  
                    "audit_status": audit_status,  
                    "discrepancy_comments": discrepancy_comments  
                })  
                insert_entry(st.session_state["form_data"])  
                st.success("Entry added!")  
                st.session_state["form_page"] = 1  
                st.session_state["form_data"] = {}  
                st.experimental_rerun()  
  
# --- DEPARTMENT TAB ---  
def department_tab(dept):  
    st.subheader(dept + " Overtime Entries")  
    df = fetch_entries(dept)  
    st.dataframe(df.head(20))  
    st.markdown("---")  
    st.write("Add new entry for " + dept)  
    entry_form(department=dept)  
  
# --- SUMMARY TAB ---  
def summary_tab():  
    st.subheader("Summary Dashboard")  
    df = fetch_entries()  
    st.dataframe(df.head(20))  
    if not df.empty:  
        st.bar_chart(df.groupby("department")["hours"].sum())  
        st.line_chart(df.groupby("date")["hours"].sum())  
    # Optionally, allow audit status update  
    st.markdown("#### Update Audit Status")  
    entry_id = st.number_input("Entry ID to update", min_value=1, step=1)  
    new_status = st.selectbox("New Audit Status", ["Pending", "Approved", "Rejected"])  
    if st.button("Update Status"):  
        update_audit_status(entry_id, new_status)  
        st.success("Audit status updated.")  
  
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
    st.line_chart(df.groupby("date")["hours"].sum())  
    st.write("**Audit Status Distribution**")  
    st.dataframe(df["Audit Status"].value_counts())  
    st.write("**Department & Audit Status Pivot Table**")  
    pivot = pd.pivot_table(df, values="hours", index="department", columns="Audit Status", aggfunc="sum", fill_value=0)  
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
