import streamlit as st
from database import (
    create_tables, add_project, add_task, add_account,
    get_projects, get_tasks, get_accounts, mark_task_done,
    get_done_tasks, reset_recurring_tasks, get_project_name_by_id,delete_project,delete_task,delete_account,download_db
)

# Initialize the database
create_tables()
reset_recurring_tasks()
st.set_page_config(layout="wide")

# Multi-page app structure
PAGES = ["Dashboard", "Projects", "Tasks", "Accounts", "Edit Data"]

st.sidebar.title("Task Management App")
page = st.sidebar.selectbox("Navigate", PAGES)

download_db()

if page == "Dashboard":
    st.title("Dashboard")

    # Filters
    st.header("Filters")
    
    # Account filter
    accounts = get_accounts()
    account_options = ["All"] + [account[1] for account in accounts]
    selected_account = st.selectbox("Filter by Account", account_options)

    # Project filter
    projects = get_projects()
    project_options = ["All"] + [project[1] for project in projects]
    selected_project_name = st.selectbox("Filter by Project", project_options)

    # Retrieve the project_id based on the selected project name
    if selected_project_name != "All":
        for project in projects:
            if project[1] == selected_project_name:  # Match the name
                selected_project_id = project[0]  # Get the project_id
                break

    st.header("Pending Tasks")
    tasks = get_tasks()

    # Filter tasks based on selected account and project
    if selected_account != "All":
        tasks = [task for task in tasks if task[6] == selected_account]
    if selected_project_name != "All":
        tasks = [task for task in tasks if task[1] == selected_project_id]

    # Display tasks in columns (group multiple tasks per row)
    num_columns = 4  # Number of tasks per row
    columns = st.columns(num_columns)

    for idx, task in enumerate(tasks):
        project_name = get_project_name_by_id(task[1])

        # Assign each task to a column in the current row
        col = columns[idx % num_columns]
        with col:
            # Add a white border box around each task with a fixed height and scrollable overflow
            task_html = f"""
            <div style="
                border: 2px solid white; 
                padding: 10px; 
                border-radius: 5px; 
                margin: 10px; 
                height: 400px; 
                overflow-y: auto; 
                display: flex; 
                flex-direction: column;
            ">
                <h3>{task[2]}</h3>
                <p><strong>Account:</strong> {task[6]}</p>
                <p><a href="{task[7]}" target="_blank">Task Link</a></p>
                <p><strong>Description:</strong> {task[3]}</p>
                <p><strong>Frequency:</strong> {task[4]}</p>
                <p><strong>Project:</strong> {project_name}</p>
            </div>
            """
            st.markdown(task_html, unsafe_allow_html=True)

            # Button to mark task as done (outside of the markdown)
            if st.button(f"Mark as Done: {task[2]}", key=f"done_{task[0]}"):
                mark_task_done(task[0])
                st.rerun()  # Trigger a rerun to refresh the app

    st.header("Completed Tasks")
    done_tasks = get_done_tasks()

    # Filter completed tasks based on selected account and project
    if selected_account != "All":
        done_tasks = [task for task in done_tasks if task[6] == selected_account]
    if selected_project_name != "All":
        done_tasks = [task for task in done_tasks if task[1] == selected_project_id]

    # Display completed tasks in columns (group multiple tasks per row)
    columns = st.columns(num_columns)

    for idx, task in enumerate(done_tasks):
        project_name = get_project_name_by_id(task[1])

        # Assign each task to a column in the current row
        col = columns[idx % num_columns]
        with col:
            # Add a white border box around each completed task with a fixed height and scrollable overflow
            task_html = f"""
            <div style="
                border: 2px solid white; 
                padding: 10px; 
                border-radius: 5px; 
                margin: 10px; 
                height: 400px; 
                overflow-y: auto; 
                display: flex; 
                flex-direction: column;
            ">
                <h3>{task[2]}</h3>
                <p><a href="{task[7]}" target="_blank">Task Link</a></p>
                <p><strong>Account:</strong> {task[6]}</p>
                <p><strong>Project:</strong> {project_name}</p>
                <p><strong>Description:</strong> {task[3]}</p>
                <p><strong>Completed On:</strong> {task[5]}</p>
            </div>
            """
            st.markdown(task_html, unsafe_allow_html=True)


elif page == "Projects":
    st.title("Projects")
    st.header("Add New Project")
    project_name = st.text_input("Project Name")
    project_description = st.text_area("Project Description")
    if st.button("Add Project"):
        add_project(project_name, project_description)
        st.success("Project added!")
    
    st.header("All Projects")
    projects = get_projects()
    for project in projects:
        st.markdown(f"### {project[1]}")
        st.write(f"Description: {project[2]}")

elif page == "Tasks":
    st.title("Tasks")
    st.header("Add New Task")
    projects = get_projects()
    accounts = get_accounts()
    project_options = {project[0]: project[1] for project in projects}
    account_options = [account[1] for account in accounts]
    selected_project = st.selectbox("Project", options=project_options.keys(), format_func=lambda x: project_options[x])
    task_name = st.text_input("Task Name")
    task_description = st.text_area("Task Description")
    task_frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly","One Time"])
    task_account = st.selectbox("Account", account_options)
    task_link = st.text_input("Task Link")
    if st.button("Add Task"):
        add_task(selected_project, task_name, task_description, task_frequency, task_account, task_link)
        st.success("Task added!")

elif page == "Accounts":
    st.title("Accounts")
    st.header("Add New Account")
    account_name = st.text_input("Account Name")
    if st.button("Add Account"):
        add_account(account_name)
        st.success("Account added!")

    st.header("All Accounts")
    accounts = get_accounts()
    for account in accounts:
        st.markdown(f"### {account[1]}")

elif page == "Edit Data":
    st.title("Edit Data")

    # Edit Project
    st.header("Edit Project")
    projects = get_projects()
    project_options = {project[0]: project[1] for project in projects}
    selected_project_id = st.selectbox("Select Project to Edit", options=project_options.keys(), format_func=lambda x: project_options[x])

    if selected_project_id:
        # Retrieve the project details
        project = next((project for project in projects if project[0] == selected_project_id), None)
        if project:
            project_name = st.text_input("Project Name", value=project[1])
            project_description = st.text_area("Project Description", value=project[2])

            if st.button("Save Changes for Project"):
                add_project(project_name, project_description, selected_project_id)  # Pass selected_project_id for update
                st.success(f"Project '{project_name}' updated successfully!")
            if st.button(f"Delete Project: {project_name}"):
                delete_project(selected_project_id)
                st.success(f"Project '{project_name}' deleted successfully!")


    # Edit Task
    st.header("Edit Task")
    tasks = get_tasks()
    task_options = {task[0]: task[2] for task in tasks}  # task[2] is the task name
    selected_task_id = st.selectbox("Select Task to Edit", options=task_options.keys(), format_func=lambda x: task_options[x])

    if selected_task_id:
        # Retrieve the task details
        task = next((task for task in tasks if task[0] == selected_task_id), None)
        if task:
            task_name = st.text_input("Task Name", value=task[2])
            task_description = st.text_area("Task Description", value=task[3])
            task_frequency = st.selectbox("Frequency", options=["daily", "weekly", "monthly", "One Time"], index=["daily", "weekly", "monthly", "One Time"].index(task[4]))
            task_account = st.selectbox("Account", options=[account[1] for account in get_accounts()], index=[account[1] for account in get_accounts()].index(task[6]))
            task_link = st.text_input("Task Link", value=task[7])

            if st.button("Save Changes for Task"):
                # Update task in the database
                add_task(task[1], task_name, task_description, task_frequency, task_account, task_link, selected_task_id)  # Pass selected_task_id for update
                st.success(f"Task '{task_name}' updated successfully!")
            if st.button(f"Delete Task: {task_name}"):
                delete_task(selected_task_id)
                st.success(f"Task '{task_name}' deleted successfully!")


    # Edit Account
    st.header("Edit Account")
    accounts = get_accounts()
    account_options = {account[0]: account[1] for account in accounts}
    selected_account_id = st.selectbox("Select Account to Edit", options=account_options.keys(), format_func=lambda x: account_options[x])

    if selected_account_id:
        # Retrieve the account details
        account = next((account for account in accounts if account[0] == selected_account_id), None)
        if account:
            account_name = st.text_input("Account Name", value=account[1])

            if st.button("Save Changes for Account"):
                add_account(account_name, selected_account_id)  # Pass selected_account_id for update
                st.success(f"Account '{account_name}' updated successfully!")
            if st.button(f"Delete Account: {account_name}"):
                delete_account(selected_account_id)
                st.success(f"Account '{account_name}' deleted successfully!")


