# Jira - Google Calendar 일정관리

### Jira release 내용을 기준으로 Google Calendar와 연동하여 일정을 공유하기 위한 용도입니다.

Jira release에 따른 상세한 이슈 내용은 링크를 통해 확인하실 수 있습니다.
```
status_counts 
{
    "진행 중": 0,
    "완료됨": 0,
    "해야 할 일": 0,
    "개발 Review": 0,
    "Deploy Success": 0,
    "Not Issued": 0
}
```

`crontab`을 통해 Jira 일정변경 및 새로운 개발일정을 확인하여 주기적으로 구글캘린더에 업데이트합니다.
```
crontab -e 

0 */8 * * * /usr/bin/python3 /path/to/fetch-jira-data.py
0 */8 * * * /usr/bin/python3 /path/to/quickstart.py
```

⚠️ 터미널 환경에서의 python3 환경변수에 주의해주세요!