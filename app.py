"""
Research Project Management System
Academic DBMS Course Project Simulation UI
Built with Streamlit, Python, and MySQL.
"""

from datetime import date, datetime
from decimal import Decimal
import pandas as pd
import streamlit as st

import database as db

# -----------------------------------------------------------------------------
# Configuration and Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Research Project Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Professional Academic / Enterprise DBMS Custom Styling
st.markdown(
    """
    <style>
        /* Base typography & clean background */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #1e293b;
        }

        /* Clean academic header */
        .academic-header {
            border-bottom: 2px solid #334155;
            padding-bottom: 0.75rem;
            margin-bottom: 1.5rem;
        }
        .academic-title {
            font-size: 1.75rem;
            font-weight: 700;
            color: #0f172a;
            letter-spacing: -0.02em;
            margin: 0;
        }
        .academic-subtitle {
            font-size: 0.95rem;
            color: #64748b;
            margin-top: 0.25rem;
            font-weight: 400;
        }

        /* Metric cards - Flat, clean, non-flashy */
        div[data-testid="stMetric"] {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            padding: 1rem;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #475569 !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.65rem !important;
            font-weight: 700 !important;
            color: #0f172a !important;
        }

        /* Clean tabs styling */
        button[data-baseweb="tab"] {
            font-weight: 600;
            font-size: 0.9rem;
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
        }

        /* Form section styling */
        .form-section-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1e293b;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 0.4rem;
            margin-top: 0.5rem;
            margin-bottom: 1rem;
        }

        /* Status badges */
        .status-badge {
            display: inline-block;
            font-size: 0.8rem;
            padding: 0.2rem 0.6rem;
            border-radius: 3px;
            font-weight: 600;
        }
        .status-badge-connected {
            background-color: #ecfdf5;
            color: #065f46;
            border: 1px solid #a7f3d0;
        }
        .status-badge-disconnected {
            background-color: #fef2f2;
            color: #991b1b;
            border: 1px solid #fecaca;
        }

        /* Tables enhancement */
        div[data-testid="stDataFrame"] {
            border: 1px solid #e2e8f0;
            border-radius: 4px;
        }

        /* Code block font */
        code {
            font-family: "Courier New", Courier, monospace !important;
            font-size: 0.88rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def format_currency(value) -> str:
    """Format decimal/float to standardized currency string."""
    try:
        val = float(value)
        return f"${val:,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


def safe_date_convert(d_val) -> date:
    """Ensure date objects are valid datetime.date."""
    if isinstance(d_val, (date, datetime)):
        return d_val if isinstance(d_val, date) else d_val.date()
    if isinstance(d_val, str):
        try:
            return datetime.strptime(d_val, "%Y-%m-%d").date()
        except Exception:
            return date.today()
    return date.today()


def render_page_header(title: str, subtitle: str):
    """Render consistent academic page header."""
    st.markdown(
        f"""
        <div class="academic-header">
            <h1 class="academic-title">{title}</h1>
            <div class="academic-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Sidebar Navigation and Configuration
# -----------------------------------------------------------------------------
def render_sidebar():
    """Render sidebar navigation and centralized database configuration controls."""
    st.sidebar.markdown("### Research Management")
    st.sidebar.markdown(
        "<small style='color: #64748b;'>DBMS Course Project Simulation</small>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    navigation_option = st.sidebar.radio(
        "Navigation Menu",
        options=[
            "Dashboard",
            "Researchers",
            "Projects",
            "Publications",
            "Grants",
            "SQL / Database Information",
        ],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("#### Database Connection")

    # Connection Test
    is_connected, status_msg = db.test_connection()
    if is_connected:
        st.sidebar.markdown(
            '<div class="status-badge status-badge-connected">Status: Connected</div>',
            unsafe_allow_html=True,
        )
        st.sidebar.caption(f"{status_msg}")
    else:
        st.sidebar.markdown(
            '<div class="status-badge status-badge-disconnected">Status: Offline / Error</div>',
            unsafe_allow_html=True,
        )
        st.sidebar.caption(f"Error: {status_msg}")

    # Settings Expander
    with st.sidebar.expander("Connection Settings", expanded=not is_connected):
        curr_cfg = db.get_db_config()
        new_host = st.text_input("Host", value=curr_cfg["host"])
        new_port = st.number_input("Port", value=curr_cfg["port"], step=1)
        new_user = st.text_input("User", value=curr_cfg["user"])
        new_password = st.text_input("Password", value=curr_cfg["password"], type="password")
        new_dbname = st.text_input("Database", value=curr_cfg["database"])

        if st.button("Apply & Reconnect", use_container_width=True):
            db.update_db_config(
                host=new_host,
                port=int(new_port),
                user=new_user,
                password=new_password,
                database=new_dbname,
            )
            st.rerun()

    # Database Initialization & Seed Controls
    st.sidebar.markdown("#### Database Maintenance")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Init Schema", use_container_width=True, help="Create database & tables"):
            with st.spinner("Initializing schema..."):
                success, msg = db.initialize_database()
                if success:
                    st.sidebar.success(msg)
                    st.rerun()
                else:
                    st.sidebar.error(msg)

    with col2:
        if st.button("Seed Data", use_container_width=True, help="Insert sample academic records"):
            with st.spinner("Seeding sample data..."):
                success, msg = db.seed_sample_data()
                if success:
                    st.sidebar.success(msg)
                    st.rerun()
                else:
                    st.sidebar.error(msg)

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Course: Database Management Systems\n\nDatabase: `ResearchManagement`\nEngine: MySQL 8.0 (InnoDB)"
    )

    return navigation_option, is_connected


# -----------------------------------------------------------------------------
# PAGE 1: DASHBOARD
# -----------------------------------------------------------------------------
def render_dashboard(is_connected: bool):
    render_page_header(
        "System Dashboard",
        "Overall statistics, recent activity records, and research funding overview",
    )

    if not is_connected:
        st.warning(
            "Database connection is currently unavailable. "
            "Please check MySQL status and credentials in the sidebar."
        )
        return

    try:
        metrics = db.get_dashboard_metrics()
    except Exception as e:
        st.error(f"Error fetching dashboard metrics: {e}")
        return

    # Metric Cards Row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric(label="Total Researchers", value=metrics["total_researchers"])
    with m2:
        st.metric(label="Total Projects", value=metrics["total_projects"])
    with m3:
        st.metric(label="Total Publications", value=metrics["total_publications"])
    with m4:
        st.metric(label="Total Grants", value=metrics["total_grants"])
    with m5:
        st.metric(label="Total Funding", value=format_currency(metrics["total_funding"]))

    st.markdown("<br>", unsafe_allow_html=True)

    # Tables: Recent Projects & Recent Publications
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Recent Projects")
        try:
            recent_projects = db.get_recent_projects(limit=5)
            if recent_projects:
                df_proj = pd.DataFrame(recent_projects)
                df_proj = df_proj.rename(
                    columns={
                        "ProjectID": "ID",
                        "ProjectName": "Project Name",
                        "StartDate": "Start Date",
                        "EndDate": "End Date",
                        "LeadResearcher": "Lead Researcher",
                    }
                )
                st.dataframe(df_proj, use_container_width=True, hide_index=True)
            else:
                st.info("No projects recorded in database.")
        except Exception as e:
            st.error(f"Error loading recent projects: {e}")

    with col_right:
        st.subheader("Recent Publications")
        try:
            recent_pubs = db.get_recent_publications(limit=5)
            if recent_pubs:
                df_pubs = pd.DataFrame(recent_pubs)
                df_pubs = df_pubs.rename(
                    columns={
                        "PublicationID": "ID",
                        "Title": "Publication Title",
                        "Journal": "Journal",
                        "PublicationYear": "Year",
                        "AuthorName": "Author",
                        "ProjectName": "Project",
                    }
                )
                st.dataframe(df_pubs, use_container_width=True, hide_index=True)
            else:
                st.info("No publications recorded in database.")
        except Exception as e:
            st.error(f"Error loading recent publications: {e}")

    st.markdown("---")

    # Grant Summary Table
    st.subheader("Grant Summary by Funding Agency")
    try:
        grant_summary = db.get_grant_summary()
        if grant_summary:
            df_grants = pd.DataFrame(grant_summary)
            df_grants["TotalFunding"] = df_grants["TotalFunding"].apply(format_currency)
            df_grants["AverageGrantAmount"] = df_grants["AverageGrantAmount"].apply(format_currency)
            df_grants = df_grants.rename(
                columns={
                    "FundingAgency": "Funding Agency",
                    "GrantCount": "Grants Awarded",
                    "TotalFunding": "Total Funding Amount",
                    "AverageGrantAmount": "Average Grant Size",
                }
            )
            st.dataframe(df_grants, use_container_width=True, hide_index=True)
        else:
            st.info("No grant records found to summarize.")
    except Exception as e:
        st.error(f"Error loading grant summary: {e}")


# -----------------------------------------------------------------------------
# PAGE 2: RESEARCHERS
# -----------------------------------------------------------------------------
def render_researchers_page(is_connected: bool):
    render_page_header(
        "Researchers Management",
        "Faculty and academic researcher registry with relational project associations",
    )

    if not is_connected:
        st.warning("Database connection offline. Please check connection in sidebar.")
        return

    tab_view, tab_add, tab_update, tab_delete = st.tabs(
        ["View All Researchers", "Add Researcher", "Update Researcher", "Delete Researcher"]
    )

    # 1. VIEW TAB
    with tab_view:
        try:
            researchers = db.get_all_researchers()
            if researchers:
                df = pd.DataFrame(researchers)
                search_query = st.text_input(
                    "Search researchers by name, department, or email",
                    placeholder="Enter keywords...",
                    key="search_researcher",
                )
                if search_query.strip():
                    q = search_query.strip().lower()
                    df = df[
                        df["Name"].str.lower().str.contains(q, na=False)
                        | df["Department"].str.lower().str.contains(q, na=False)
                        | df["Email"].str.lower().str.contains(q, na=False)
                    ]

                st.caption(f"Showing {len(df)} researcher record(s)")
                st.dataframe(
                    df.rename(
                        columns={
                            "ResearcherID": "ID",
                            "Name": "Full Name",
                            "Email": "Email Address",
                            "Department": "Department",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No researchers registered yet. Use the 'Add Researcher' tab to create records.")
        except Exception as e:
            st.error(f"Failed to fetch researchers: {e}")

    # 2. ADD TAB
    with tab_add:
        st.markdown('<div class="form-section-title">New Researcher Details</div>', unsafe_allow_html=True)
        with st.form("form_add_researcher", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                r_id = st.number_input(
                    "Researcher ID *",
                    min_value=1,
                    step=1,
                    value=105,
                    help="Unique integer primary key",
                )
                name = st.text_input("Full Name *", placeholder="e.g. Dr. Jane Doe")
            with col2:
                email = st.text_input("Email Address", placeholder="e.g. j.doe@university.edu")
                department = st.text_input(
                    "Department *", placeholder="e.g. Computer Science & Engineering"
                )

            submitted = st.form_submit_button("Add Researcher", use_container_width=False)
            if submitted:
                if not name.strip():
                    st.error("Validation Error: Full Name is required.")
                elif not department.strip():
                    st.error("Validation Error: Department is required.")
                else:
                    success, msg = db.add_researcher(
                        int(r_id), name.strip(), email.strip(), department.strip()
                    )
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

    # 3. UPDATE TAB
    with tab_update:
        st.markdown('<div class="form-section-title">Modify Existing Researcher</div>', unsafe_allow_html=True)
        try:
            researchers = db.get_all_researchers()
            if not researchers:
                st.info("No researchers available to update.")
            else:
                options = {f"ID {r['ResearcherID']} - {r['Name']}": r for r in researchers}
                selected_label = st.selectbox(
                    "Select Researcher to Edit", options=list(options.keys()), key="update_r_select"
                )
                selected_r = options[selected_label]

                with st.form("form_update_researcher"):
                    u_id = st.number_input(
                        "Researcher ID (Primary Key - Read Only)",
                        value=selected_r["ResearcherID"],
                        disabled=True,
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        u_name = st.text_input("Full Name *", value=selected_r["Name"])
                        u_email = st.text_input("Email Address", value=selected_r.get("Email") or "")
                    with col2:
                        u_dept = st.text_input("Department *", value=selected_r.get("Department") or "")

                    btn_update = st.form_submit_button("Save Changes")
                    if btn_update:
                        if not u_name.strip():
                            st.error("Validation Error: Full Name cannot be empty.")
                        elif not u_dept.strip():
                            st.error("Validation Error: Department cannot be empty.")
                        else:
                            success, msg = db.update_researcher(
                                selected_r["ResearcherID"],
                                u_name.strip(),
                                u_email.strip(),
                                u_dept.strip(),
                            )
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
        except Exception as e:
            st.error(f"Error loading researchers for update: {e}")

    # 4. DELETE TAB
    with tab_delete:
        st.markdown('<div class="form-section-title">Remove Researcher Record</div>', unsafe_allow_html=True)
        try:
            researchers = db.get_all_researchers()
            if not researchers:
                st.info("No researchers available to delete.")
            else:
                options = {f"ID {r['ResearcherID']} - {r['Name']} ({r['Department']})": r for r in researchers}
                selected_label = st.selectbox(
                    "Select Researcher to Delete", options=list(options.keys()), key="delete_r_select"
                )
                selected_r = options[selected_label]

                st.warning(
                    f"Warning: Deleting Researcher #{selected_r['ResearcherID']} ('{selected_r['Name']}') "
                    "will fail if referenced by active Projects or Publications due to Foreign Key integrity constraints."
                )

                if st.button("Confirm Delete Researcher", type="primary"):
                    success, msg = db.delete_researcher(selected_r["ResearcherID"])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        except Exception as e:
            st.error(f"Error loading researchers for deletion: {e}")


# -----------------------------------------------------------------------------
# PAGE 3: PROJECTS
# -----------------------------------------------------------------------------
def render_projects_page(is_connected: bool):
    render_page_header(
        "Research Projects Management",
        "Manage institutional and funded research projects with foreign-key links to researchers",
    )

    if not is_connected:
        st.warning("Database connection offline. Please check connection in sidebar.")
        return

    tab_view, tab_add, tab_update, tab_delete = st.tabs(
        ["View All Projects", "Add Project", "Update Project", "Delete Project"]
    )

    # 1. VIEW TAB
    with tab_view:
        try:
            projects = db.get_all_projects()
            if projects:
                df = pd.DataFrame(projects)
                search_query = st.text_input(
                    "Search projects by project name or lead researcher",
                    placeholder="Enter keywords...",
                    key="search_projects",
                )
                if search_query.strip():
                    q = search_query.strip().lower()
                    df = df[
                        df["ProjectName"].str.lower().str.contains(q, na=False)
                        | df["LeadResearcher"].str.lower().str.contains(q, na=False)
                    ]

                st.caption(f"Showing {len(df)} project record(s)")
                st.dataframe(
                    df.rename(
                        columns={
                            "ProjectID": "Project ID",
                            "ProjectName": "Project Title",
                            "StartDate": "Start Date",
                            "EndDate": "End Date",
                            "ResearcherID": "Lead Researcher ID",
                            "LeadResearcher": "Lead Researcher Name",
                            "ResearcherDepartment": "Department",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No projects found in database. Use 'Add Project' tab to create one.")
        except Exception as e:
            st.error(f"Failed to fetch projects: {e}")

    # 2. ADD TAB
    with tab_add:
        st.markdown('<div class="form-section-title">New Project Details</div>', unsafe_allow_html=True)
        try:
            researchers = db.get_all_researchers()
            if not researchers:
                st.warning(
                    "No researchers found. Please add a researcher first before creating a project."
                )
            else:
                researcher_options = {
                    f"ID {r['ResearcherID']} - {r['Name']} ({r['Department']})": r["ResearcherID"]
                    for r in researchers
                }

                with st.form("form_add_project", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        p_id = st.number_input(
                            "Project ID *",
                            min_value=1,
                            step=1,
                            value=205,
                            help="Unique project primary key",
                        )
                        p_name = st.text_input(
                            "Project Name *",
                            placeholder="e.g. Distributed Consensus in Cloud Systems",
                        )
                        selected_res_label = st.selectbox(
                            "Lead Researcher * (Foreign Key)",
                            options=list(researcher_options.keys()),
                        )

                    with col2:
                        start_d = st.date_input("Start Date *", value=date.today())
                        end_d = st.date_input(
                            "End Date *",
                            value=date(date.today().year + 2, date.today().month, date.today().day),
                        )

                    btn_add = st.form_submit_button("Add Project")
                    if btn_add:
                        if not p_name.strip():
                            st.error("Validation Error: Project Name is required.")
                        elif end_d < start_d:
                            st.error("Validation Error: End Date cannot be earlier than Start Date.")
                        else:
                            r_id = researcher_options[selected_res_label]
                            success, msg = db.add_project(
                                int(p_id), p_name.strip(), start_d, end_d, r_id
                            )
                            if success:
                                st.success(msg)
                            else:
                                st.error(msg)
        except Exception as e:
            st.error(f"Error loading researchers for project form: {e}")

    # 3. UPDATE TAB
    with tab_update:
        st.markdown('<div class="form-section-title">Modify Project Details</div>', unsafe_allow_html=True)
        try:
            projects = db.get_all_projects()
            researchers = db.get_all_researchers()

            if not projects:
                st.info("No projects available to update.")
            elif not researchers:
                st.error("No researchers found in database.")
            else:
                proj_options = {f"ID {p['ProjectID']} - {p['ProjectName']}": p for p in projects}
                sel_proj_label = st.selectbox(
                    "Select Project to Edit", options=list(proj_options.keys()), key="update_p_select"
                )
                sel_proj = proj_options[sel_proj_label]

                # Map researcher options
                res_options = {
                    f"ID {r['ResearcherID']} - {r['Name']}": r["ResearcherID"] for r in researchers
                }

                # Find current researcher index
                curr_res_idx = 0
                for idx, (lbl, rid) in enumerate(res_options.items()):
                    if rid == sel_proj["ResearcherID"]:
                        curr_res_idx = idx
                        break

                with st.form("form_update_project"):
                    u_pid = st.number_input(
                        "Project ID (Primary Key - Read Only)",
                        value=sel_proj["ProjectID"],
                        disabled=True,
                    )
                    u_pname = st.text_input("Project Name *", value=sel_proj["ProjectName"])

                    col1, col2 = st.columns(2)
                    with col1:
                        u_start = st.date_input(
                            "Start Date *", value=safe_date_convert(sel_proj["StartDate"])
                        )
                        u_res = st.selectbox(
                            "Lead Researcher * (Foreign Key)",
                            options=list(res_options.keys()),
                            index=curr_res_idx,
                        )
                    with col2:
                        u_end = st.date_input(
                            "End Date *", value=safe_date_convert(sel_proj["EndDate"])
                        )

                    btn_save_p = st.form_submit_button("Save Changes")
                    if btn_save_p:
                        if not u_pname.strip():
                            st.error("Validation Error: Project Name cannot be empty.")
                        elif u_end < u_start:
                            st.error("Validation Error: End Date cannot be earlier than Start Date.")
                        else:
                            chosen_rid = res_options[u_res]
                            success, msg = db.update_project(
                                sel_proj["ProjectID"],
                                u_pname.strip(),
                                u_start,
                                u_end,
                                chosen_rid,
                            )
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
        except Exception as e:
            st.error(f"Error loading project update form: {e}")

    # 4. DELETE TAB
    with tab_delete:
        st.markdown('<div class="form-section-title">Remove Project Record</div>', unsafe_allow_html=True)
        try:
            projects = db.get_all_projects()
            if not projects:
                st.info("No projects available to delete.")
            else:
                proj_options = {f"ID {p['ProjectID']} - {p['ProjectName']}": p for p in projects}
                sel_del_label = st.selectbox(
                    "Select Project to Delete", options=list(proj_options.keys()), key="del_p_select"
                )
                sel_p = proj_options[sel_del_label]

                st.warning(
                    f"Warning: Deleting Project #{sel_p['ProjectID']} ('{sel_p['ProjectName']}') "
                    "will fail if referenced by Publications or Grants due to Foreign Key integrity constraints."
                )

                if st.button("Confirm Delete Project", type="primary"):
                    success, msg = db.delete_project(sel_p["ProjectID"])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        except Exception as e:
            st.error(f"Error loading project deletion: {e}")


# -----------------------------------------------------------------------------
# PAGE 4: PUBLICATIONS
# -----------------------------------------------------------------------------
def render_publications_page(is_connected: bool):
    render_page_header(
        "Publications Management",
        "Research publication records linking researchers and funded projects",
    )

    if not is_connected:
        st.warning("Database connection offline. Please check connection in sidebar.")
        return

    tab_view, tab_add, tab_update, tab_delete = st.tabs(
        ["View All Publications", "Add Publication", "Update Publication", "Delete Publication"]
    )

    # 1. VIEW TAB
    with tab_view:
        try:
            pubs = db.get_all_publications()
            if pubs:
                df = pd.DataFrame(pubs)
                search_query = st.text_input(
                    "Search publications by title, journal, or author",
                    placeholder="Enter keywords...",
                    key="search_pubs",
                )
                if search_query.strip():
                    q = search_query.strip().lower()
                    df = df[
                        df["Title"].str.lower().str.contains(q, na=False)
                        | df["Journal"].str.lower().str.contains(q, na=False)
                        | df["AuthorName"].str.lower().str.contains(q, na=False)
                    ]

                st.caption(f"Showing {len(df)} publication record(s)")
                st.dataframe(
                    df.rename(
                        columns={
                            "PublicationID": "Publication ID",
                            "Title": "Paper Title",
                            "Journal": "Journal / Conference",
                            "PublicationYear": "Year",
                            "AuthorName": "Author",
                            "ProjectName": "Research Project",
                        }
                    )[["Publication ID", "Paper Title", "Journal / Conference", "Year", "Author", "Research Project"]],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No publications found. Use 'Add Publication' tab to register one.")
        except Exception as e:
            st.error(f"Failed to fetch publications: {e}")

    # 2. ADD TAB
    with tab_add:
        st.markdown('<div class="form-section-title">New Publication Details</div>', unsafe_allow_html=True)
        try:
            researchers = db.get_all_researchers()
            projects = db.get_all_projects()

            if not researchers or not projects:
                st.warning(
                    "Both Researchers and Projects must exist before creating a Publication. "
                    "Please ensure both tables have records."
                )
            else:
                res_options = {
                    f"ID {r['ResearcherID']} - {r['Name']}": r["ResearcherID"] for r in researchers
                }
                proj_options = {
                    f"ID {p['ProjectID']} - {p['ProjectName']}": p["ProjectID"] for p in projects
                }

                with st.form("form_add_pub", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        pub_id = st.number_input(
                            "Publication ID *",
                            min_value=1,
                            step=1,
                            value=306,
                            help="Unique publication primary key",
                        )
                        title = st.text_input(
                            "Paper Title *",
                            placeholder="e.g. Robust Optimization under Uncertainty",
                        )
                        journal = st.text_input(
                            "Journal / Venue *",
                            placeholder="e.g. IEEE Transactions on Knowledge & Data Engineering",
                        )

                    with col2:
                        pub_year = st.number_input(
                            "Publication Year *",
                            min_value=1950,
                            max_value=2050,
                            value=datetime.now().year,
                            step=1,
                        )
                        sel_res = st.selectbox(
                            "Author (Researcher ID - Foreign Key) *",
                            options=list(res_options.keys()),
                        )
                        sel_proj = st.selectbox(
                            "Associated Project (Project ID - Foreign Key) *",
                            options=list(proj_options.keys()),
                        )

                    btn_add_pub = st.form_submit_button("Add Publication")
                    if btn_add_pub:
                        if not title.strip():
                            st.error("Validation Error: Paper Title is required.")
                        elif not journal.strip():
                            st.error("Validation Error: Journal / Venue is required.")
                        else:
                            r_id = res_options[sel_res]
                            p_id = proj_options[sel_proj]
                            success, msg = db.add_publication(
                                int(pub_id),
                                title.strip(),
                                journal.strip(),
                                int(pub_year),
                                r_id,
                                p_id,
                            )
                            if success:
                                st.success(msg)
                            else:
                                st.error(msg)
        except Exception as e:
            st.error(f"Error loading publication form dependencies: {e}")

    # 3. UPDATE TAB
    with tab_update:
        st.markdown('<div class="form-section-title">Modify Publication Details</div>', unsafe_allow_html=True)
        try:
            pubs = db.get_all_publications()
            researchers = db.get_all_researchers()
            projects = db.get_all_projects()

            if not pubs:
                st.info("No publications available to update.")
            elif not researchers or not projects:
                st.error("Missing researchers or projects required for reference.")
            else:
                pub_opts = {f"ID {p['PublicationID']} - {p['Title']}": p for p in pubs}
                sel_pub_lbl = st.selectbox(
                    "Select Publication to Edit", options=list(pub_opts.keys()), key="update_pub_sel"
                )
                sel_pub = pub_opts[sel_pub_lbl]

                res_opts = {
                    f"ID {r['ResearcherID']} - {r['Name']}": r["ResearcherID"] for r in researchers
                }
                proj_opts = {
                    f"ID {p['ProjectID']} - {p['ProjectName']}": p["ProjectID"] for p in projects
                }

                # Find researcher index
                curr_r_idx = 0
                for idx, (lbl, rid) in enumerate(res_opts.items()):
                    if rid == sel_pub["ResearcherID"]:
                        curr_r_idx = idx
                        break

                # Find project index
                curr_p_idx = 0
                for idx, (lbl, pid) in enumerate(proj_opts.items()):
                    if pid == sel_pub["ProjectID"]:
                        curr_p_idx = idx
                        break

                with st.form("form_update_pub"):
                    st.number_input(
                        "Publication ID (Primary Key - Read Only)",
                        value=sel_pub["PublicationID"],
                        disabled=True,
                    )
                    u_title = st.text_input("Paper Title *", value=sel_pub["Title"])
                    col1, col2 = st.columns(2)
                    with col1:
                        u_journal = st.text_input("Journal / Venue *", value=sel_pub["Journal"])
                        u_year = st.number_input(
                            "Publication Year *",
                            min_value=1950,
                            max_value=2050,
                            value=int(sel_pub["PublicationYear"]),
                            step=1,
                        )
                    with col2:
                        u_res = st.selectbox(
                            "Author (Researcher ID) *",
                            options=list(res_opts.keys()),
                            index=curr_r_idx,
                        )
                        u_proj = st.selectbox(
                            "Associated Project (Project ID) *",
                            options=list(proj_opts.keys()),
                            index=curr_p_idx,
                        )

                    btn_upd_pub = st.form_submit_button("Save Changes")
                    if btn_upd_pub:
                        if not u_title.strip():
                            st.error("Validation Error: Paper Title cannot be empty.")
                        elif not u_journal.strip():
                            st.error("Validation Error: Journal cannot be empty.")
                        else:
                            chosen_r = res_opts[u_res]
                            chosen_p = proj_opts[u_proj]
                            success, msg = db.update_publication(
                                sel_pub["PublicationID"],
                                u_title.strip(),
                                u_journal.strip(),
                                int(u_year),
                                chosen_r,
                                chosen_p,
                            )
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
        except Exception as e:
            st.error(f"Error loading publication update form: {e}")

    # 4. DELETE TAB
    with tab_delete:
        st.markdown('<div class="form-section-title">Remove Publication Record</div>', unsafe_allow_html=True)
        try:
            pubs = db.get_all_publications()
            if not pubs:
                st.info("No publications available to delete.")
            else:
                pub_opts = {f"ID {p['PublicationID']} - {p['Title']}": p for p in pubs}
                sel_del_pub = st.selectbox(
                    "Select Publication to Delete", options=list(pub_opts.keys()), key="del_pub_sel"
                )
                sel_p = pub_opts[sel_del_pub]

                st.write(
                    f"**ID:** {sel_p['PublicationID']} | **Title:** {sel_p['Title']} | **Journal:** {sel_p['Journal']}"
                )

                if st.button("Confirm Delete Publication", type="primary"):
                    success, msg = db.delete_publication(sel_p["PublicationID"])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        except Exception as e:
            st.error(f"Error loading publication deletion: {e}")


# -----------------------------------------------------------------------------
# PAGE 5: GRANTS
# -----------------------------------------------------------------------------
def render_grants_page(is_connected: bool):
    render_page_header(
        "Grants & Funding Management",
        "Manage research grant allocations, sponsoring agencies, and project investments",
    )

    if not is_connected:
        st.warning("Database connection offline. Please check connection in sidebar.")
        return

    tab_view, tab_add, tab_update, tab_delete = st.tabs(
        ["View All Grants", "Add Grant", "Update Grant", "Delete Grant"]
    )

    # 1. VIEW TAB
    with tab_view:
        try:
            grants = db.get_all_grants()
            if grants:
                df = pd.DataFrame(grants)
                search_query = st.text_input(
                    "Search grants by grant title, funding agency, or project",
                    placeholder="Enter keywords...",
                    key="search_grants",
                )
                if search_query.strip():
                    q = search_query.strip().lower()
                    name_s = df["Grant Name"] if "Grant Name" in df.columns else df.get("GrantName", pd.Series([""] * len(df)))
                    agency_s = df["Funding Agency"] if "Funding Agency" in df.columns else df.get("FundingAgency", pd.Series([""] * len(df)))
                    proj_s = df["Funded Project"] if "Funded Project" in df.columns else df.get("ProjectName", pd.Series([""] * len(df)))
                    df = df[
                        name_s.astype(str).str.lower().str.contains(q, na=False)
                        | agency_s.astype(str).str.lower().str.contains(q, na=False)
                        | proj_s.astype(str).str.lower().str.contains(q, na=False)
                    ]

                st.caption(f"Showing {len(df)} grant record(s)")
                # Format currency for table display without creating duplicate columns
                display_df = df.copy()
                if "Amount" in display_df.columns:
                    display_df["Amount"] = display_df["Amount"].apply(format_currency)

                display_cols = [
                    "Grant ID",
                    "Grant Name",
                    "Amount",
                    "Funding Agency",
                    "Project ID",
                    "Funded Project",
                ]
                st.dataframe(
                    display_df[display_cols],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No grant records found. Use 'Add Grant' tab to create one.")
        except Exception as e:
            st.error(f"Failed to fetch grants: {e}")

    # 2. ADD TAB
    with tab_add:
        st.markdown('<div class="form-section-title">New Grant Details</div>', unsafe_allow_html=True)
        try:
            projects = db.get_all_projects()
            if not projects:
                st.warning(
                    "No projects exist. A grant must be associated with an existing project. "
                    "Please create a project first."
                )
            else:
                proj_options = {
                    f"ID {p['ProjectID']} - {p['ProjectName']}": p["ProjectID"] for p in projects
                }

                with st.form("form_add_grant", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        g_id = st.number_input(
                            "Grant ID *",
                            min_value=1,
                            step=1,
                            value=406,
                            help="Unique grant primary key",
                        )
                        g_name = st.text_input(
                            "Grant Name *", placeholder="e.g. Advanced Research Infrastructure Grant"
                        )
                        amount = st.number_input(
                            "Amount ($) *", min_value=1.0, value=150000.0, step=5000.0, format="%.2f"
                        )

                    with col2:
                        agency = st.text_input(
                            "Funding Agency *", placeholder="e.g. National Science Foundation"
                        )
                        sel_proj = st.selectbox(
                            "Target Project (Project ID - Foreign Key) *",
                            options=list(proj_options.keys()),
                        )

                    btn_add_g = st.form_submit_button("Add Grant")
                    if btn_add_g:
                        if not g_name.strip():
                            st.error("Validation Error: Grant Name is required.")
                        elif not agency.strip():
                            st.error("Validation Error: Funding Agency is required.")
                        elif amount <= 0:
                            st.error("Validation Error: Amount must be greater than zero.")
                        else:
                            p_id = proj_options[sel_proj]
                            success, msg = db.add_grant(
                                int(g_id), g_name.strip(), float(amount), agency.strip(), p_id
                            )
                            if success:
                                st.success(msg)
                            else:
                                st.error(msg)
        except Exception as e:
            st.error(f"Error loading grant form dependencies: {e}")

    # 3. UPDATE TAB
    with tab_update:
        st.markdown('<div class="form-section-title">Modify Grant Details</div>', unsafe_allow_html=True)
        try:
            grants = db.get_all_grants()
            projects = db.get_all_projects()

            if not grants:
                st.info("No grants available to update.")
            elif not projects:
                st.error("No projects available for foreign key reference.")
            else:
                grant_opts = {
                    f"ID {g.get('Grant ID', g.get('GrantID'))} - {g.get('Grant Name', g.get('GrantName'))}": g
                    for g in grants
                }
                sel_g_lbl = st.selectbox(
                    "Select Grant to Edit", options=list(grant_opts.keys()), key="update_g_sel"
                )
                sel_g = grant_opts[sel_g_lbl]

                proj_opts = {
                    f"ID {p['ProjectID']} - {p['ProjectName']}": p["ProjectID"] for p in projects
                }

                # Find project index
                curr_p_idx = 0
                sel_proj_id = sel_g.get("Project ID", sel_g.get("ProjectID"))
                for idx, (lbl, pid) in enumerate(proj_opts.items()):
                    if pid == sel_proj_id:
                        curr_p_idx = idx
                        break

                with st.form("form_update_grant"):
                    sel_grant_id = sel_g.get("Grant ID", sel_g.get("GrantID"))
                    st.number_input(
                        "Grant ID (Primary Key - Read Only)",
                        value=sel_grant_id,
                        disabled=True,
                    )
                    u_gname = st.text_input(
                        "Grant Name *", value=sel_g.get("Grant Name", sel_g.get("GrantName"))
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        u_amount = st.number_input(
                            "Amount ($) *",
                            min_value=1.0,
                            value=float(sel_g["Amount"]),
                            step=5000.0,
                            format="%.2f",
                        )
                        u_agency = st.text_input(
                            "Funding Agency *",
                            value=sel_g.get("Funding Agency", sel_g.get("FundingAgency")),
                        )
                    with col2:
                        u_proj = st.selectbox(
                            "Target Project (Project ID) *",
                            options=list(proj_opts.keys()),
                            index=curr_p_idx,
                        )

                    btn_upd_g = st.form_submit_button("Save Changes")
                    if btn_upd_g:
                        if not u_gname.strip():
                            st.error("Validation Error: Grant Name cannot be empty.")
                        elif not u_agency.strip():
                            st.error("Validation Error: Funding Agency cannot be empty.")
                        elif u_amount <= 0:
                            st.error("Validation Error: Amount must be greater than zero.")
                        else:
                            chosen_pid = proj_opts[u_proj]
                            success, msg = db.update_grant(
                                sel_grant_id,
                                u_gname.strip(),
                                float(u_amount),
                                u_agency.strip(),
                                chosen_pid,
                            )
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
        except Exception as e:
            st.error(f"Error loading grant update form: {e}")

    # 4. DELETE TAB
    with tab_delete:
        st.markdown('<div class="form-section-title">Remove Grant Record</div>', unsafe_allow_html=True)
        try:
            grants = db.get_all_grants()
            if not grants:
                st.info("No grants available to delete.")
            else:
                grant_opts = {
                    f"ID {g.get('Grant ID', g.get('GrantID'))} - {g.get('Grant Name', g.get('GrantName'))}": g
                    for g in grants
                }
                sel_del_g = st.selectbox(
                    "Select Grant to Delete", options=list(grant_opts.keys()), key="del_g_sel"
                )
                sel_g = grant_opts[sel_del_g]
                sel_grant_id = sel_g.get("Grant ID", sel_g.get("GrantID"))
                sel_gname = sel_g.get("Grant Name", sel_g.get("GrantName"))
                sel_agency = sel_g.get("Funding Agency", sel_g.get("FundingAgency"))

                st.write(
                    f"**ID:** {sel_grant_id} | **Grant:** {sel_gname} | "
                    f"**Amount:** {format_currency(sel_g['Amount'])} | **Agency:** {sel_agency}"
                )

                if st.button("Confirm Delete Grant", type="primary"):
                    success, msg = db.delete_grant(sel_grant_id)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        except Exception as e:
            st.error(f"Error loading grant deletion: {e}")


# -----------------------------------------------------------------------------
# PAGE 6: SQL / DATABASE INFORMATION
# -----------------------------------------------------------------------------
def render_sql_info_page(is_connected: bool):
    render_page_header(
        "SQL & Database Information",
        "Database architectural design, relational schema, constraints, and live query demonstrations",
    )

    # 1. Architectural & Schema Overview
    st.markdown("### 1. Database Architecture")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Database Name:** `ResearchManagement`")
    with c2:
        st.markdown("**Storage Engine:** `InnoDB` (ACID Compliant)")
    with c3:
        st.markdown("**Character Set:** `utf8mb4`")

    st.markdown(
        """
        The **Research Project Management System** database is organized in **Third Normal Form (3NF)**.
        It eliminates data redundancy and update anomalies by decomposing entities into dedicated relational tables:
        - **Researcher**: Stores academic identity and department affiliation.
        - **Project**: Represents funded research initiatives with defined timelines, linked to a primary investigator.
        - **Publication**: Models scholarly dissemination, recording journals and referencing both author and project.
        - **Grant**: Tracks monetary awards and sponsoring agencies assigned to specific research projects.
        """
    )

    st.markdown("---")

    # 2. Table Definitions & Relationships
    st.markdown("### 2. Relational Schema & Entity Relationships")

    schema_data = [
        {
            "Table": "Researcher",
            "Columns & Types": "ResearcherID (INT, PK), Name (VARCHAR(50)), Email (VARCHAR(100)), Department (VARCHAR(50))",
            "Primary Key": "ResearcherID",
            "Foreign Keys": "None",
            "Relationship Cardinality": "1 : N with Project, 1 : N with Publication",
        },
        {
            "Table": "Project",
            "Columns & Types": "ProjectID (INT, PK), ProjectName (VARCHAR(100)), StartDate (DATE), EndDate (DATE), ResearcherID (INT, FK)",
            "Primary Key": "ProjectID",
            "Foreign Keys": "ResearcherID -> Researcher(ResearcherID)",
            "Relationship Cardinality": "N : 1 with Researcher, 1 : N with Publication, 1 : N with Grant",
        },
        {
            "Table": "Publication",
            "Columns & Types": "PublicationID (INT, PK), Title (VARCHAR(150)), Journal (VARCHAR(100)), PublicationYear (INT), ResearcherID (INT, FK), ProjectID (INT, FK)",
            "Primary Key": "PublicationID",
            "Foreign Keys": "ResearcherID -> Researcher(ResearcherID), ProjectID -> Project(ProjectID)",
            "Relationship Cardinality": "N : 1 with Researcher, N : 1 with Project",
        },
        {
            "Table": "`Grant`",
            "Columns & Types": "GrantID (INT, PK), GrantName (VARCHAR(100)), Amount (DECIMAL(12,2)), FundingAgency (VARCHAR(100)), ProjectID (INT, FK)",
            "Primary Key": "GrantID",
            "Foreign Keys": "ProjectID -> Project(ProjectID)",
            "Relationship Cardinality": "N : 1 with Project",
        },
    ]

    st.dataframe(pd.DataFrame(schema_data), use_container_width=True, hide_index=True)

    st.markdown(
        """
        **Referential Integrity Constraints:**
        - Foreign keys enforce `ON UPDATE CASCADE` to propagate primary key modifications automatically.
        - Foreign keys enforce `ON DELETE RESTRICT` to protect against accidental orphan records. A parent record cannot be removed while referenced by dependent records.
        """
    )

    st.markdown("---")

    # 3. Demonstration SQL Queries (SELECT, JOIN, SUM, GROUP BY, etc.)
    st.markdown("### 3. Demonstration SQL Queries (Live Execution)")
    st.write(
        "Select an example SQL query below to inspect its purpose, query syntax, and execute it against MySQL."
    )

    query_labels = [f"[{q['category']}] {q['title']}" for q in db.DEMO_QUERIES]
    selected_idx = st.selectbox(
        "Choose Query Demonstration",
        options=range(len(query_labels)),
        format_func=lambda i: query_labels[i],
    )

    active_query = db.DEMO_QUERIES[selected_idx]

    st.markdown(f"**Category:** `{active_query['category']}`")
    st.markdown(f"**Description:** {active_query['description']}")
    st.code(active_query["sql"], language="sql")

    if st.button("Execute Demonstration Query", type="primary", key="btn_run_demo"):
        if not is_connected:
            st.error("Cannot execute: Database connection is offline.")
        else:
            success, result_rows, cols = db.execute_custom_query(active_query["sql"])
            if success:
                if cols and result_rows:
                    df_res = pd.DataFrame(result_rows, columns=cols)
                    st.success(f"Query returned {len(df_res)} row(s).")
                    st.dataframe(df_res, use_container_width=True, hide_index=True)
                else:
                    st.info("Query executed successfully. Result set is empty.")
            else:
                st.error(f"Execution Error: {result_rows}")

    st.markdown("---")

    # 4. Interactive Read-Only SQL Query Console for Evaluator
    st.markdown("### 4. Interactive SQL Console (Read-Only)")
    st.caption(
        "Evaluator console for testing custom `SELECT` queries directly against the `ResearchManagement` schema."
    )

    custom_sql = st.text_area(
        "Enter SQL Query",
        value="SELECT r.Name, COUNT(p.ProjectID) AS ProjectsLed\nFROM Researcher r\nLEFT JOIN Project p ON r.ResearcherID = p.ResearcherID\nGROUP BY r.ResearcherID, r.Name;",
        height=120,
    )

    if st.button("Run Custom Query", key="btn_run_custom"):
        if not is_connected:
            st.error("Cannot execute: Database connection is offline.")
        else:
            clean_query = custom_sql.strip()
            # Simple safety check for read-only evaluator console
            first_word = clean_query.split()[0].upper() if clean_query else ""
            if first_word not in ["SELECT", "SHOW", "DESCRIBE", "EXPLAIN"]:
                st.warning(
                    "Only read-only queries (`SELECT`, `SHOW`, `DESCRIBE`, `EXPLAIN`) are permitted in the interactive console."
                )
            else:
                success, result_rows, cols = db.execute_custom_query(clean_query)
                if success:
                    if cols and result_rows:
                        df_res = pd.DataFrame(result_rows, columns=cols)
                        st.success(f"Query returned {len(df_res)} row(s).")
                        st.dataframe(df_res, use_container_width=True, hide_index=True)
                    else:
                        st.info("Query executed successfully. Result set is empty.")
                else:
                    st.error(f"Execution Error: {result_rows}")


# -----------------------------------------------------------------------------
# MAIN APPLICATION ROUTING
# -----------------------------------------------------------------------------
def main():
    selected_page, is_connected = render_sidebar()

    if selected_page == "Dashboard":
        render_dashboard(is_connected)
    elif selected_page == "Researchers":
        render_researchers_page(is_connected)
    elif selected_page == "Projects":
        render_projects_page(is_connected)
    elif selected_page == "Publications":
        render_publications_page(is_connected)
    elif selected_page == "Grants":
        render_grants_page(is_connected)
    elif selected_page == "SQL / Database Information":
        render_sql_info_page(is_connected)


if __name__ == "__main__":
    main()
