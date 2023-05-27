import streamlit as st
import subprocess
import os
from datetime import datetime

# Initialize session state variables if they don't exist
if 'repo_path' not in st.session_state:
    st.session_state['repo_path'] = ''
if 'github_repo_url' not in st.session_state:
    st.session_state['github_repo_url'] = ''
if 'commit_date' not in st.session_state:
    st.session_state['commit_date'] = datetime.today()
if 'commit_number' not in st.session_state:
    st.session_state['commit_number'] = 1
if 'commit_data' not in st.session_state:
    st.session_state['commit_data'] = [{'file_name': '', 'commit_msg': '', 'commit_time': datetime.now().time()} for _ in range(st.session_state['commit_number'])]

# Display fields for user input
repo_path = st.text_input("Enter repository path:", value=st.session_state['repo_path'])
github_repo_url = st.text_input("Enter Github repository URL:", value=st.session_state['github_repo_url'])
commit_date = st.date_input("Select date for commit:", value=st.session_state['commit_date'])
commit_number = st.number_input("Number of commits:", min_value=1, value=st.session_state['commit_number'], step=1)

if commit_number != st.session_state['commit_number']:
    st.session_state['commit_number'] = commit_number
    st.session_state['commit_data'] = [{'file_name': '', 'commit_msg': '', 'commit_time': datetime.now().time()} for _ in range(st.session_state['commit_number'])]

for i in range(commit_number):
    file_name = st.text_input(f"Enter file name for commit {i+1}:", value=st.session_state['commit_data'][i]['file_name'])
    commit_msg = st.text_input(f"Enter commit message for commit {i+1}:", value=st.session_state['commit_data'][i]['commit_msg'])
    commit_time = st.time_input(f"Select time for commit {i+1}:", value=st.session_state['commit_data'][i]['commit_time'])
    st.session_state['commit_data'][i] = {'file_name': file_name, 'commit_msg': commit_msg, 'commit_time': commit_time}

if st.button("Make Commit"):
    st.session_state['repo_path'] = repo_path
    st.session_state['github_repo_url'] = github_repo_url
    st.session_state['commit_date'] = commit_date
    for i in range(commit_number):
        # Create a file
        touch_command = f"touch {os.path.join(repo_path, st.session_state['commit_data'][i]['file_name'])}"
        # Add file to git
        git_add_command = f"git -C {repo_path} add {st.session_state['commit_data'][i]['file_name']}"
        # Concatenate date and time in ISO format
        # We'll use UTC timezone as an example
        commit_datetime = datetime.combine(commit_date, st.session_state['commit_data'][i]['commit_time']).isoformat() + "+00:00"
        git_commit_command = f"git -C {repo_path} commit -m {st.session_state['commit_data'][i]['commit_msg']}"
        git_amend_command = f'GIT_COMMITTER_DATE="{commit_datetime}" git -C {repo_path} commit --amend --date="{commit_datetime}"'
        try:
            # Run commands and capture output
            touch_result = subprocess.run(touch_command, shell=True, check=True, text=True, capture_output=True)
            st.write(touch_result.stdout)
            print("created file " + touch_result)
            add_result = subprocess.run(git_add_command, shell=True, check=True, text=True, capture_output=True)
            st.write(add_result.stdout)
            print("git add "+ add_result)
            commit_result = subprocess.run(git_commit_command, shell=True, check=True, text=True, capture_output=True)
            st.write(commit_result.stdout)
            amend_result = subprocess.run(git_amend_command, shell=True, check=True, text=True, capture_output=True)
            st.write(amend_result.stdout)
        except subprocess.CalledProcessError as e:
            st.error(f"An error occurred while attempting to commit. Details: {e}")
            break
    else:
        # If all commits successful, then push to remote
        git_push_command = f"git -C {repo_path} push https://{os.getenv('GITHUB_TOKEN')}@{github_repo_url}"
        print(git_push_command)
        try:
            push_result = subprocess.run(git_push_command, shell=True, check=True, text=True, capture_output=True)
            st.write(push_result.stdout)
            st.success(f"{commit_number} commits were successful and pushed to remote!")
        except subprocess.CalledProcessError as e:
            st.error(f"An error occurred while attempting to push to remote. Details: {e}")
