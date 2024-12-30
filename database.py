import sqlite3
import datetime
import shutil
import os
import streamlit as st
import git

def connect_db():
    return sqlite3.connect("projects.db")

def get_project_name_by_id(project_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM projects WHERE id = ?', (project_id,))
    project_name = cursor.fetchone()
    conn.close()
    
    if project_name:
        return project_name[0]  # Return the project name
    return None  # Return None if no project is found



# Function to handle the download of the file
import os
import git
import streamlit as st

def download_and_commit_db():
    db_path = 'projects.db'
    repo_path = "D:/Personal Detail/Project/crypto-task/task_manager"  # Local clone path of your GitHub repository
    username = "Wclow0420"
    personal_access_token = "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"


    # Use the PAT in the repo_url
    repo_url = f"https://{username}:{personal_access_token}@github.com/Wclow0420/task_manager.git"  # GitHub URL with PAT for authentication

    if os.path.exists(db_path):
        # Provide download option
        with open(db_path, "rb") as f:
            st.download_button(
                label="Download projects.db",
                data=f,
                file_name="projects.db",
                mime="application/octet-stream"
            )

        # Commit and push to GitHub
        if st.button("Commit and Push to GitHub"):
            try:
                if not os.path.exists(repo_path):
                    # Clone the repository if it doesn't exist locally
                    st.info(f"Cloning the repository from {repo_url}")
                    git.Repo.clone_from(repo_url, repo_path)

                repo = git.Repo(repo_path)
                
                # Stage changes
                repo.git.add(db_path)
                
                # Commit with a message
                commit_message = st.text_input("Enter commit message:", value="Updated projects.db")
                if commit_message:
                    repo.index.commit(commit_message)
                    
                    # Set up remote repository and push
                    origin = repo.remote(name='origin')
                    origin.push()
                    
                    st.success("projects.db has been committed and pushed to GitHub!")
                else:
                    st.error("Please provide a commit message.")
            except git.exc.GitCommandError as e:
                st.error(f"Git error: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
    else:
        st.error("Database file not found!")


        
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            name TEXT,
            description TEXT,
            frequency TEXT, -- "daily", "weekly", "monthly"
            last_completed_date DATE,
            account TEXT,
            link TEXT,
            status TEXT, -- "Pending" or "Done"
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_project(name, description, project_id=None):
    conn = connect_db()
    cursor = conn.cursor()
    
    if project_id:  # If project_id is passed, update the project
        cursor.execute('''
            UPDATE projects
            SET name = ?, description = ?
            WHERE id = ?
        ''', (name, description, project_id))
    else:  # If no project_id, add a new project
        cursor.execute('''
            INSERT INTO projects (name, description)
            VALUES (?, ?)
        ''', (name, description))
    
    conn.commit()
    conn.close()


def add_task(project_id, name, description, frequency, account, link, task_id=None):
    conn = connect_db()
    cursor = conn.cursor()
    
    if task_id:  # If task_id is passed, update the task
        cursor.execute('''
            UPDATE tasks
            SET project_id = ?, name = ?, description = ?, frequency = ?, account = ?, link = ?
            WHERE id = ?
        ''', (project_id, name, description, frequency, account, link, task_id))
    else:  # If no task_id, add a new task
        cursor.execute('''
            INSERT INTO tasks (project_id, name, description, frequency, account, link, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Pending')
        ''', (project_id, name, description, frequency, account, link))
    
    conn.commit()
    conn.close()


def add_account(name, account_id=None):
    conn = connect_db()
    cursor = conn.cursor()
    
    if account_id:  # If account_id is passed, update the account
        cursor.execute('''
            UPDATE accounts
            SET name = ?
            WHERE id = ?
        ''', (name, account_id))
    else:  # If no account_id, add a new account
        cursor.execute('''
            INSERT INTO accounts (name)
            VALUES (?)
        ''', (name,))
    
    conn.commit()
    conn.close()


def get_projects():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects')
    projects = cursor.fetchall()
    conn.close()
    return projects

def get_tasks():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE status = "Pending"')
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def get_accounts():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM accounts')
    accounts = cursor.fetchall()
    conn.close()
    return accounts

def delete_project(project_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def delete_account(account_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
    conn.commit()
    conn.close()


def mark_task_done(task_id):
    today = datetime.date.today()
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tasks
        SET status = "Done", last_completed_date = ?
        WHERE id = ?
    ''', (today, task_id))
    conn.commit()
    conn.close()

def get_done_tasks():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE status = "Done"')
    done_tasks = cursor.fetchall()
    conn.close()
    return done_tasks

def reset_recurring_tasks():
    today = datetime.date.today()
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tasks
        SET status = "Pending"
        WHERE (
            (frequency = "daily" AND (last_completed_date IS NULL OR last_completed_date < ?))
            OR (frequency = "weekly" AND (last_completed_date IS NULL OR last_completed_date < ?))
            OR (frequency = "monthly" AND (last_completed_date IS NULL OR last_completed_date < ?))
        ) AND status = "Done"
    ''', (today, today - datetime.timedelta(days=7), today - datetime.timedelta(days=30)))
    conn.commit()
    conn.close()
