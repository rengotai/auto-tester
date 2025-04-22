# slack_notifier.py 예시
import os
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackNotifier:
    def __init__(self, token=None, channel=None):
        self.token = token or os.environ.get("SLACK_API_TOKEN")
        if not self.token:
            raise ValueError("Slack API 토큰이 필요합니다")
        
        self.channel = channel or os.environ.get("SLACK_CHANNEL", "#go-tests")
        self.client = WebClient(token=self.token)
    
    def send_test_results(self, test_results):
        """테스트 결과를 Slack으로 전송"""
        # 결과 이모지 결정
        emoji = "✅" if test_results.get("success", False) else "❌"
        
        summary = test_results.get("summary", {})
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Go 테스트 결과: {'성공' if test_results.get('success', False) else '실패'}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*총 테스트:*\n{summary.get('total', 0)}"},
                    {"type": "mrkdwn", "text": f"*통과:*\n{summary.get('passed', 0)}"},
                    {"type": "mrkdwn", "text": f"*실패:*\n{summary.get('failed', 0)}"}
                ]
            }
        ]
        
        # 실패한 테스트 상세 정보 추가
        failed_tests = [t for t in test_results.get("tests", []) if t.get("Action") == "fail"]
        if failed_tests:
            failure_text = "*실패한 테스트:*\n"
            
            for test in failed_tests[:5]:  # 상위 5개만 표시
                test_name = test.get("Test", "Unknown")
                output = test.get("Output", "")
                
                failure_text += f"• `{test_name}`: {output[:100]}{'...' if len(output) > 100 else ''}\n"
            
            if len(failed_tests) > 5:
                failure_text += f"... 그리고 {len(failed_tests) - 5}개 더 실패"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": failure_text
                }
            })
        
        # 메시지 전송
        try:
            self.client.chat_postMessage(
                channel=self.channel,
                text=f"Go 테스트 결과: {summary.get('passed', 0)}/{summary.get('total', 0)} 통과",
                blocks=json.dumps(blocks)
            )
            return True
        except SlackApiError as e:
            print(f"Slack 메시지 전송 오류: {e.response['error']}")
            return False