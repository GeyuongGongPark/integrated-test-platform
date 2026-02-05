# -*- coding: utf-8 -*-
"""Playwright test_steps JSON 실행 (코드 없이 실행 버튼용). routes와 tasks에서 공통 사용."""
import os
import json
import subprocess
import tempfile


def run_playwright_steps(steps_data, base_url=None, timeout=300):
    """
    test_steps JSON으로 Playwright 단계 실행.

    Args:
        steps_data: list of step dicts (e.g. [{"action": "navigate", "url": "..."}, ...])
        base_url: 기본 URL (미지정 시 환경변수 또는 http://localhost:3000)
        timeout: 실행 제한 시간(초)

    Returns:
        dict: {'status': 'Pass'|'Fail', 'output': str, 'error': str|None}
    """
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(backend_dir)
    runner_dir = os.path.join(project_root, 'test-scripts', 'playwright', 'step-runner')
    runner_script = os.path.join(runner_dir, 'run-steps.mjs')
    if not os.path.exists(runner_script):
        return {'status': 'Fail', 'output': '', 'error': f'단계 실행기가 없습니다: {runner_script}'}

    base_url = base_url or os.environ.get('PLAYWRIGHT_BASE_URL', 'http://localhost:3000')
    env = os.environ.copy()
    env['BASE_URL'] = base_url
    env['HEADLESS'] = 'true'

    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(steps_data, f, ensure_ascii=False)
            steps_path = f.name
        try:
            result = subprocess.run(
                ['node', 'run-steps.mjs', steps_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=runner_dir,
                env=env
            )
            return {
                'status': 'Pass' if result.returncode == 0 else 'Fail',
                'output': result.stdout or '',
                'error': result.stderr if result.returncode != 0 else None
            }
        finally:
            try:
                os.unlink(steps_path)
            except Exception:
                pass
    except subprocess.TimeoutExpired:
        return {'status': 'Fail', 'output': '', 'error': '단계 실행 시간이 초과되었습니다.'}
    except Exception as e:
        return {'status': 'Fail', 'output': '', 'error': str(e)}
