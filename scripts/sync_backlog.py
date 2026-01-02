import os
import json
import urllib.request
import datetime

# Configuration
REPO = "The-Band-Solution/ResearchDomain"
BACKLOG_PATH = "docs/backlog.md"
GH_TOKEN = os.getenv("GH_TOKEN")

def fetch_issues():
    url = f"https://api.github.com/repos/{REPO}/issues?state=all&per_page=100"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GH_TOKEN:
        headers["Authorization"] = f"token {GH_TOKEN}"
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def format_issue_row(issue):
    number = issue["number"]
    url = issue["html_url"]
    title = issue["title"]
    state = issue["state"]
    
    # Simple status mapping
    status_icon = "🟢" if state == "open" else "✅"
    
    # Extract labels for extra context if needed
    labels = [l["name"] for l in issue.get("labels", [])]
    
    # Mock sprint and milestone for now or extract from issue data if available
    milestone = issue.get("milestone")
    milestone_title = milestone["title"] if milestone else "-"
    
    executor = issue.get("assignee")
    executor_name = f"@{executor['login']}" if executor else "-"
    
    return f"| [# {number}]({url}) | {status_icon} | {title} | {executor_name} | - | {milestone_title} |"

def update_backlog(issues):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Filter out Pull Requests (GitHub API returns PRs in the issues endpoint)
    only_issues = [i for i in issues if "pull_request" not in i]
    
    header = f"""# Project Backlog - ResearchDomain

This document is automatically synchronized with GitHub Issues. Last updated: {now}

## 📋 Master Issue List
Overview of all demands, their states and executors.

| # | Status | Title | Executor | Sprint | Milestone |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
    
    rows = [format_issue_row(i) for i in only_issues]
    
    content = header + "\n".join(rows) + "\n\n---\n"
    
    # Add workflow states section
    in_progress = [i for i in only_issues if i["state"] == "open"]
    done = [i for i in only_issues if i["state"] == "closed"]
    
    content += "\n## 📂 Workflow States\n\n### 🟢 In Progress / Todo\n"
    if not in_progress:
        content += "_No issues in this state._\n"
    for i in in_progress:
        content += f"- [#{i['number']}]({i['html_url']}) **{i['title']}**\n"
        
    content += "\n### ✅ Done / Released\n"
    if not done:
        content += "_No issues in this state._\n"
    for i in done:
        content += f"- [#{i['number']}]({i['html_url']}) **{i['title']}**\n"

    content += "\n---\n\n## 📝 Detailed Backlog\n"
    for i in only_issues:
        content += f"\n### [{i['state'].upper()}] [#{i['number']}]({i['html_url']}) {i['title']}\n"
        content += f"- **Executor**: {i.get('assignee', {}).get('login', '-') if i.get('assignee') else '-'}\n"
        content += f"- **Labels**: {', '.join([l['name'] for l in i.get('labels', [])])}\n"
        content += f"- **Milestone**: {i.get('milestone', {}).get('title', '-') if i.get('milestone') else '-'}\n"
        content += f"\n**Description**:\n{i.get('body', 'No description provided.')}\n"
        content += "\n---\n"

    with open(BACKLOG_PATH, "w") as f:
        f.write(content)

if __name__ == "__main__":
    print("Fetching issues...")
    try:
        issues = fetch_issues()
        print(f"Found {len(issues)} issues/PRs. Updating backlog...")
        update_backlog(issues)
        print("Backlog updated successfully.")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
