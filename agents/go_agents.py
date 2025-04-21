import os
import subprocess
import tempfile
import json
from typing import Dict, Any, List, Optional
import re

from .base import BaseAgent
from .specialized_agents import RunnerAgent

class GoDevAgent(BaseAgent):
    """Agent specialized in Go code analysis and development."""
    
    def __init__(self, model: str = "gpt-4"):
        system_prompt = """
        You are GoDevAgent, an AI specialized in Go code analysis and development.
        Your tasks include:
        1. Analyzing Go code changes and understanding their purpose
        2. Providing context about existing Go code
        3. Suggesting improvements to Go code quality
        4. Identifying potential bugs or issues in Go code
        5. Communicating clearly with GoTestAgent about code functionality
        
        When analyzing Go code, focus on:
        - What the code does functionally
        - Key algorithms and data structures used
        - Go-specific patterns and idioms
        - Error handling approach
        - Concurrency patterns if applicable
        - Dependencies and side effects
        - Edge cases and potential failure points
        - Security considerations
        
        Be concise but thorough in your analysis.
        """
        super().__init__("GoDevAgent", model, system_prompt)
    
    async def analyze_go_code_diff(self, diff_content: str) -> str:
        """Analyze a Go code diff and provide insights.
        
        Args:
            diff_content (str): Git diff content
            
        Returns:
            str: Analysis of the code changes
        """
        prompt = f"""
        Please analyze this Go code diff and provide insights:
        
        ```
        {diff_content}
        ```
        
        Focus on:
        1. What functionality has changed?
        2. What are the key components affected?
        3. What edge cases should be tested?
        4. Are there any potential bugs or issues?
        5. What tests would be appropriate for these changes?
        6. Any Go-specific considerations (e.g., concurrency, error handling)?
        """
        
        return await self.send_message(prompt)
    
    async def provide_go_code_context(self, file_path: str, code_content: str) -> str:
        """Provide context about existing Go code.
        
        Args:
            file_path (str): Path to the file
            code_content (str): Content of the file
            
        Returns:
            str: Context about the code
        """
        prompt = f"""
        Please provide context about this Go code file:
        
        File: {file_path}
        
        ```go
        {code_content}
        ```
        
        Include:
        1. Purpose of this file/package
        2. Key functions/methods and their functionality
        3. Data structures and their usage
        4. Dependencies and interactions with other components
        5. Any concurrency patterns or considerations
        6. Error handling approach
        7. Any potential pain points for testing
        """
        
        return await self.send_message(prompt)


class GoTestAgent(BaseAgent):
    """Agent specialized in writing and analyzing Go tests."""
    
    def __init__(self, model: str = "gpt-4"):
        system_prompt = """
        You are GoTestAgent, an AI specialized in Go software testing.
        Your tasks include:
        1. Creating comprehensive test cases for Go code changes
        2. Writing idiomatic Go tests including unit, integration, and table-driven tests
        3. Utilizing the standard Go testing package and popular libraries like testify, gomock
        4. Focusing on edge cases and potential failure points
        5. Analyzing test failures and suggesting fixes
        6. Following Go testing best practices
        
        Write tests that are:
        - Comprehensive (cover main functionality and edge cases)
        - Isolated (don't depend on other tests)
        - Deterministic (same result each time)
        - Fast and efficient
        - Easy to understand and maintain
        - Idiomatic to Go
        
        Always include assertions and clear documentation in your tests.
        """
        super().__init__("GoTestAgent", model, system_prompt)
    
    async def generate_go_test_cases(self, code_context: str, code_changes: str = None) -> str:
        """Generate Go test cases based on code context and changes.
        
        Args:
            code_context (str): Context about the code
            code_changes (str, optional): Description of code changes
            
        Returns:
            str: Generated test cases
        """
        if code_changes:
            prompt = f"""
            Please generate Go test cases for the following code changes:
            
            CODE CONTEXT:
            {code_context}
            
            CODE CHANGES:
            {code_changes}
            
            For each test case:
            1. Provide a descriptive name (following Go's TestXxx naming convention)
            2. Specify inputs and expected outputs
            3. Identify edge cases to test
            4. Highlight any setup requirements (e.g., mocks, fixtures)
            
            Focus on table-driven tests where appropriate and follow Go testing best practices.
            """
        else:
            prompt = f"""
            Please generate Go test cases for the following code:
            
            CODE CONTEXT:
            {code_context}
            
            For each test case:
            1. Provide a descriptive name (following Go's TestXxx naming convention)
            2. Specify inputs and expected outputs
            3. Identify edge cases to test
            4. Highlight any setup requirements (e.g., mocks, fixtures)
            
            Focus on table-driven tests where appropriate and follow Go testing best practices.
            """
        
        return await self.send_message(prompt)
    
    async def write_go_test_code(self, code_context: str, test_cases: str, use_mock: bool = True) -> str:
        """Write Go test code based on test cases.
        
        Args:
            code_context (str): Context about the code
            test_cases (str): Test cases to implement
            use_mock (bool): Whether to use mocking libraries
            
        Returns:
            str: Generated Go test code
        """
        mock_library = ""
        if use_mock:
            mock_library = """
            Consider using gomock for interface mocking, or testify/mock where appropriate.
            Include proper mock setup and teardown.
            """
            
        prompt = f"""
        Please write Go test code for the following test cases:
        
        CODE CONTEXT:
        {code_context}
        
        TEST CASES:
        {test_cases}
        
        Please provide complete, runnable Go test code following best practices:
        1. Include proper imports
        2. Use table-driven tests where appropriate
        3. Include proper error checking
        4. Use descriptive failure messages
        5. Follow Go testing conventions and naming
        {mock_library}
        
        Make sure the tests would compile and run in a Go environment.
        """
        
        return await self.send_message(prompt)
    
    async def analyze_go_test_failures(self, test_output: str, test_code: str) -> str:
        """Analyze Go test failures and suggest fixes.
        
        Args:
            test_output (str): Output from failed tests
            test_code (str): The test code that was run
            
        Returns:
            str: Analysis and suggestions
        """
        prompt = f"""
        Please analyze these Go test failures and suggest fixes:
        
        TEST CODE:
        ```go
        {test_code}
        ```
        
        TEST OUTPUT:
        ```
        {test_output}
        ```
        
        For each failure:
        1. What caused the test to fail?
        2. Is the issue in the test or in the code under test?
        3. How should it be fixed?
        4. Are there any other tests that might be affected?
        
        Include Go-specific considerations in your analysis.
        """
        
        return await self.send_message(prompt)


class GoRunnerAgent(RunnerAgent):
    """Agent specialized in running Go tests and analyzing results."""
    
    def __init__(self, model: str = "gpt-4"):
        system_prompt = """
        You are GoRunnerAgent, an AI specialized in running Go tests and analyzing results.
        Your tasks include:
        1. Setting up Go test environments
        2. Executing Go tests
        3. Collecting and reporting Go test results
        4. Analyzing test failures
        5. Providing clear, actionable feedback to developers and test engineers
        
        Be thorough in your analysis and clear in your reporting.
        """
        super().__init__(model)
        self.system_prompt = system_prompt
        self.reset_conversation()
    
    async def execute_go_tests(self, test_code: str, source_code: str = None, package_path: str = None) -> Dict[str, Any]:
        """Execute Go tests and report results.
        
        Args:
            test_code (str): Go test code to execute
            source_code (str, optional): Source code being tested, if needed
            package_path (str, optional): Path to package, if available
            
        Returns:
            Dict[str, Any]: Test results including stats and failures
        """
        # Create temporary directory for test files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a Go module
            subprocess.run(
                ["go", "mod", "init", "test_module"],
                capture_output=True,
                text=True,
                cwd=temp_dir
            )
            
            # Create a directory structure for the test
            pkg_dir = os.path.join(temp_dir, "pkg")
            os.makedirs(pkg_dir, exist_ok=True)
            
            # If source code is provided, write it to a file
            if source_code:
                source_file_path = os.path.join(pkg_dir, "source.go")
                with open(source_file_path, "w") as f:
                    f.write(source_code)
            
            # Write test code to a file
            test_file_path = os.path.join(pkg_dir, "source_test.go")
            with open(test_file_path, "w") as f:
                f.write(test_code)
            
            # Get dependencies
            subprocess.run(
                ["go", "mod", "tidy"],
                capture_output=True,
                text=True,
                cwd=temp_dir
            )
            
            # Run the tests with verbose output and JSON output
            result = subprocess.run(
                ["go", "test", "./pkg", "-v"],
                capture_output=True,
                text=True,
                cwd=temp_dir
            )
            
            # Create basic result structure
            output = result.stdout + result.stderr
            results = {
                "success": result.returncode == 0,
                "output": output,
                "return_code": result.returncode
            }
            
            # Parse the output to extract test results
            results.update(self._parse_go_test_output(output))
            
            return results
    
    def _parse_go_test_output(self, output: str) -> Dict[str, Any]:
        """Parse Go test output to extract test results.
        
        Args:
            output (str): Go test output
            
        Returns:
            Dict[str, Any]: Structured test results
        """
        # Initialize counts
        total = 0
        passed = 0
        failed = 0
        skipped = 0
        failing_tests = []
        
        # Regular expressions for parsing test output
        test_pattern = r"--- (PASS|FAIL|SKIP): ([\w\.\/]+) \(([0-9\.]+)s\)"
        
        # Parse each line
        for line in output.splitlines():
            test_match = re.search(test_pattern, line)
            if test_match:
                total += 1
                status, test_name, duration = test_match.groups()
                
                if status == "PASS":
                    passed += 1
                elif status == "FAIL":
                    failed += 1
                    # Find failure message (usually within a few lines after the failure)
                    failure_msg = "Unknown failure reason"
                    lines = output.splitlines()
                    for i, l in enumerate(lines):
                        if test_name in l and "FAIL" in l:
                            # Try to get a few lines after the failure for context
                            failure_context = lines[i:i+5]
                            failure_msg = "\n".join(failure_context)
                            break
                    
                    failing_tests.append({
                        "name": test_name,
                        "message": failure_msg,
                        "duration": duration
                    })
                elif status == "SKIP":
                    skipped += 1
        
        # If we couldn't parse any tests but the return code is non-zero, we have a failure
        if total == 0 and "FAIL" in output:
            failed = 1
            total = 1
            failing_tests.append({
                "name": "CompilationOrSetupFailure",
                "message": output,
                "duration": "0.0"
            })
        
        # If we found a "ok" line with timing, it means all tests passed
        ok_match = re.search(r"ok\s+\S+\s+([0-9\.]+)s", output)
        if ok_match and total == 0:
            passed = 1
            total = 1
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "failing_tests": failing_tests
        }
    
    async def analyze_go_test_results(self, results: Dict[str, Any]) -> str:
        """Analyze Go test results and provide insights.
        
        Args:
            results (Dict[str, Any]): Test results from execute_go_tests
            
        Returns:
            str: Analysis and insights
        """
        prompt = f"""
        Please analyze these Go test results and provide insights:
        
        ```
        {json.dumps(results, indent=2)}
        ```
        
        Include in your analysis:
        1. Overall test health (pass rate)
        2. Patterns in failing tests (if any)
        3. Go-specific issues (e.g., race conditions, goroutine leaks)
        4. Recommendations for improving test quality
        5. Next steps for the development team
        
        Focus on Go-specific insights and be concise but informative.
        """
        
        return await self.send_message(prompt)
