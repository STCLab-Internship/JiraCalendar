from jira import JIRA
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pprint import pprint
import json
import os
import random, logging

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_USER = os.getenv("JIRA_USER")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")

def fetch_data(project_id, start_date, end_date):
    # Jira 인스턴스 생성
    jira = JIRA(server=JIRA_URL, basic_auth=(JIRA_USER, JIRA_TOKEN))

    # 릴리즈 가져오기
    all_releases = jira.project_versions(project_id)
    jira_results = all_releases
    
    # 특정 기간 내의 릴리즈 필터링
    targeted_releases = []

    for release in all_releases:   
        try :
            release_endDate = release.releaseDate
        except: # 릴리즈에서 마감기한을 정하지 않은 경우 release.startDate로 지정
            release_endDate = release.startDate
              
        if (
            (release.startDate >= start_date and release.startDate <= end_date) or
            (release_endDate >= start_date and release_endDate <= end_date) or
            (release.startDate <= start_date and release_endDate >= end_date)
        ):
            targeted_releases.append(release)

    jira_results = []

    for release in targeted_releases:
        
        try :
            release_endDate = release.releaseDate
        except: # 릴리즈에서 마감기한을 정하지 않은 경우 release.startDate로 지정
            release_endDate = release.startDate

        status_counts = {
            "진행 중": 0,
            "완료됨": 0,
            "해야 할 일": 0,
            "개발 Review": 0,
            "Deploy Success": 0,
            "Not Issued": 0
        }

        release_data = {
            "release_id" : release.id,
            "release_name": release.name,
            "release_startDate": release.startDate,
            "release_endDate": release_endDate,
            "release_status": release.released,
            "release_url": f"{JIRA_URL}/projects/{project_id}/versions/{release.id}",
            "release_issues": [],
            "release_statusCounts": []
        }

        # 릴리즈에 연결된 이슈 가져오기
        try :
            jql_query = f'fixVersion = "{release.id}"'
            issues = jira.search_issues(jql_str=jql_query, fields="key,summary,status")
            
            for issue in issues:
                issue_data = {
                    "issue_key": issue.key,
                    "issue_summary": issue.fields.summary,
                    "issue_status": issue.fields.status.name,
                    "issue_url": issue.permalink()
                }
                release_data["release_issues"].append(issue_data)

                if issue.fields.status.name in status_counts:
                    status_counts[issue.fields.status.name] += 1
        except :
            issues = []
            
        release_data["release_statusCounts"].append(status_counts)
        jira_results.append(release_data)

    return jira_results

def insert_data(start_date, end_date) :
    projects = ["NF4","SF1", "BAL","HI"] 
    GoogleCalendar_Insert = []
    
    for project in projects:
        print("-" * 100, project)
        result = fetch_data(project, start_date, end_date)
        
        for r in result :
            pprint(r)
            GoogleCalendar_Insert.append({
                'summary': str(r['release_name']),
                # 'description': str(r['release_url']),
                'description': r['release_url'] +"\n"+ 
                    'Deploy Success : ' + str(r['release_statusCounts'][0]['Deploy Success'])+ "\n" +
                    'Not Issued : ' + str(r['release_statusCounts'][0]['Not Issued'])+ "\n" +
                    '개발 Review : ' + str(r['release_statusCounts'][0]['개발 Review'])+ "\n" +
                    '완료됨 : ' + str(r['release_statusCounts'][0]['완료됨'])+ "\n" +
                    '진행 중 : ' + str(r['release_statusCounts'][0]['진행 중'])+ "\n" +
                    '해야 할 일 : ' + str(r['release_statusCounts'][0]['해야 할 일'])+ "\n"
                ,
                'start': {
                    'date': str(r['release_startDate']),
                    'timeZone': 'Asia/Seoul',
                },
                'end': {
                    'date': str(r['release_endDate']),
                    'timeZone': 'Asia/Seoul',
                },
                "colorId": random.randint(1,11)
            })
            
    return GoogleCalendar_Insert


if __name__ == "__main__":
    
    now = datetime.now()
    one_month_ago = now - timedelta(days=30)
    one_month_later = now + timedelta(days=30)
    start_date = one_month_ago.strftime("%Y-%m-%d")
    end_date = one_month_later.strftime("%Y-%m-%d")
    
    GoogleCalendar_Insert = insert_data(start_date, end_date)
            
    file_path = "JiraData.json"
    with open(file_path, 'w') as f :
        json.dump(GoogleCalendar_Insert, f)
            

