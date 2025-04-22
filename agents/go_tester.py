# go_tester.py 예시
import os
import subprocess
import tempfile
import json
from typing import Dict, Any

class GoTester:
    def __init__(self, project_path=None):
        self.project_path = project_path or os.getcwd()
    
    def run_tests(self, package_path=None, use_mock=True):
        """Go 테스트 실행
        
        Args:
            package_path: 테스트할 패키지 경로
            use_mock: gomock 사용 여부
        
        Returns:
            Dict: 테스트 결과
        """
        cmd = ["go", "test"]
        
        if use_mock:
            # gomock이 설치되어 있는지 확인
            try:
                subprocess.run(
                    ["mockgen", "--version"], 
                    capture_output=True, 
                    check=True
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                # gomock 설치
                subprocess.run(
                    ["go", "install", "github.com/golang/mock/mockgen@latest"],
                    check=True
                )
        
        if package_path:
            cmd.append(package_path)
        
        cmd.extend(["-v", "-json"]) # JSON 형식으로 출력
        
        # 테스트 실행
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.project_path
        )
        
        # 결과 파싱
        return self._parse_test_output(result.stdout, result.stderr, result.returncode)
    
    def _parse_test_output(self, stdout, stderr, return_code):
        """테스트 출력 파싱"""
        results = {
            "success": return_code == 0,
            "output": stdout + stderr,
            "return_code": return_code,
            "tests": []
        }
        
        # JSON 라인 파싱
        for line in stdout.splitlines():
            try:
                data = json.loads(line)
                if data.get("Action") == "run" or data.get("Action") == "pass" or data.get("Action") == "fail":
                    results["tests"].append(data)
            except json.JSONDecodeError:
                continue
        
        # 테스트 통계
        passed = sum(1 for t in results["tests"] if t.get("Action") == "pass")
        failed = sum(1 for t in results["tests"] if t.get("Action") == "fail")
        
        results["summary"] = {
            "total": passed + failed,
            "passed": passed,
            "failed": failed
        }
        
        return results
    
    def generate_mocks(self, interface_file, package, destination=None):
        """Mock 생성
        
        Args:
            interface_file: 인터페이스가 정의된 파일
            package: 패키지 이름
            destination: 목적지 파일 경로
        
        Returns:
            bool: 성공 여부
        """
        if not destination:
            # 기본 Mock 경로 생성
            dirname = os.path.dirname(interface_file)
            basename = os.path.basename(interface_file)
            name_without_ext = os.path.splitext(basename)[0]
            destination = os.path.join(dirname, f"mock_{name_without_ext}.go")
        
        # mockgen 실행
        cmd = [
            "mockgen",
            "-source", interface_file,
            "-package", package,
            "-destination", destination
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.project_path
        )
        
        return result.returncode == 0, result.stdout, result.stderr
  