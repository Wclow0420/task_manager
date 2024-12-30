import sqlite3
import datetime
import shutil
import os
import streamlit as st
import git
import subprocess

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

def commit_and_push_db():
    db_path = 'projects.db'  # Path to your local projects.db file
    username = "Wclow0420"  # Your GitHub username
    personal_access_token = "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"  # Your GitHub PAT

    # Check if the projects.db file exists
    if os.path.exists(db_path):
        # Prepare the git commands to commit and push
        repo_url = f"https://{username}:{personal_access_token}@github.com/Wclow0420/task_manager.git"
        
        # Initialize a new Git repository or use an existing one
        subprocess.run(['git', 'config', '--global', 'user.name', 'Wclow0420'])
        subprocess.run(['git', 'config', '--global', 'user.email', 'wclow0420@gmail.com'])

        subprocess.run(['git', 'remote', 'set-url', 'origin', f'https://Wclow0420:{personal_access_token}@github.com/Wclow0420/task_manager.git'])
        subprocess.run(['git', 'init'])  # Initialize git if not done already
        subprocess.run(['git', 'remote', 'add', 'origin', repo_url])  # Add remote repository
        
        # Stage the database file
        subprocess.run(['git', 'add', db_path])
        
        # Commit the changes
        commit_message = "Updated projects.db"
        subprocess.run(['git', 'commit', '-m', commit_message])

        # Push to the remote GitHub repository
        subprocess.run(['git', 'push', 'origin', 'main'])

        st.write("projects.db has been committed and pushed to GitHub!")
    else:
        st.write("projects.db file not found!")


        
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
