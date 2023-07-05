import streamlit as st
import requests
from github import Github
from pylint import epylint as lint

def main():
    st.title("Source Code Error Detector")
    st.write("Enter the GitHub repository URL to scan for errors.")
    repo_url = st.text_input("GitHub Repository URL")
    
    if st.button("Scan Repository"):
        scan_repository(repo_url)

def scan_repository(repo_url):
    try:
        owner, name = extract_owner_and_name(repo_url)
        g = Github()
        repo = g.get_repo(f"{owner}/{name}")
        default_branch = repo.default_branch
        contents = repo.get_contents("", ref=default_branch)
        errors_found = False
        
        for content in contents:
            if content.type == "file" and content.name.endswith(".py"):
                file_contents = requests.get(content.download_url).text
                errors = detect_errors(file_contents, content.name)
                if errors:
                    errors_found = True
                    st.write(f"Errors found in file: {content.name}")
                    for error in errors:
                        st.write(f"Line {error['line']}: {error['message']}")
        
        if not errors_found:
            st.success("No errors found in the repository.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

def extract_owner_and_name(repo_url):
    parts = repo_url.strip("/").split("/")
    owner = parts[-2]
    name = parts[-1]
    return owner, name

def detect_errors(code, file_name):
    (pylint_stdout, _) = lint.py_run(code, return_std=True)
    output = pylint_stdout.getvalue()
    
    errors = parse_output(output)
    return errors

def parse_output(output):
    errors = []
    lines = output.split("\n")
    
    for line in lines:
        parts = line.split(":")
        
        if len(parts) >= 3:
            line_number = int(parts[1].strip())
            error_message = parts[2].strip()
            errors.append({"line": line_number, "message": error_message})
    
    return errors

if __name__ == "__main__":
    main()
