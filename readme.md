# 프로젝트 첫 실행 법

### 1. 가상환경을 만든다
`python -m venv .venv`

### 2. 가상환경 진입 후 패키지를 설치한다.
`.venv\Scripts\activate`
`pip install streamlit openai python-dotenv pytrends beautifulsoup4 pandas`
- 추후에 설치 패키지는 수정하겠습니다.
- 아니면 requirements.txt를 만들겠습니다.
- requirements.txt를 만들었으나 streamlit 배포를 위해 LINUX용 requirements.txt를 만들게 되어 windows 사용자는 위 코드를 cmd에 입력하세요.

### 3. .env파일을 만든다
파일을 만든 후 
`OPENAI_API_KEY = "자신의 OPENAI API KEY"`
`NAVER_CLIENT_ID = "네이버 API CLIENT ID"`
`NAVER_CLIENT_SECRET = "네이버 API CLIENT ID"`

위 내용 작성@yulmii