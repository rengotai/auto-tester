# main.py 예시
import os
import asyncio
from fastapi import FastAPI, Request, BackgroundTasks
from dotenv import load_dotenv
from go_tester import GoTester
from slack_notifier import SlackNotifier

# 환경 변수 로드
load_dotenv()

app = FastAPI()
tester = GoTester()
notifier = SlackNotifier()

@app.post("/trigger/test")
async def trigger_test(request: Request, background_tasks: BackgroundTasks):
    """테스트 트리거 엔드포인트"""
    data = await request.json()
    
    # 백그라운드에서 테스트 실행
    background_tasks.add_task(run_test_and_notify, data)
    
    return {"status": "테스트가 시작됐습니다", "data": data}

@app.post("/slack/commands")
async def slack_command(request: Request, background_tasks: BackgroundTasks):
    """슬랙 커맨드 처리"""
    form_data = await request.form()
    command = form_data.get("command")
    text = form_data.get("text", "")
    
    if command == "/gotest":
        # 텍스트 파싱 (예: "/gotest path/to/package")
        package_path = text.strip() if text else None
        
        # 백그라운드에서 테스트 실행
        background_tasks.add_task(
            run_test_and_notify, {"package_path": package_path}
        )
        
        return {
            "response_type": "in_channel",
            "text": f"Go 테스트를 시작합니다 {package_path or '(모든 패키지)'}"
        }
    
    return {"text": "지원되지 않는 명령어입니다"}

async def run_test_and_notify(data):
    """테스트 실행 및 결과 알림"""
    package_path = data.get("package_path")
    use_mock = data.get("use_mock", True)
    
    # 테스트 실행
    results = tester.run_tests(package_path, use_mock)
    
    # Slack으로 결과 전송
    notifier.send_test_results(results)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)