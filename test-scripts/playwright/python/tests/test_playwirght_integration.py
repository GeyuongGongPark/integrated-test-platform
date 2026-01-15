import subprocess

def test_playwright_script():
    result = subprocess.run(["playwright", "test", "playwirght/test/js/test.js"], capture_output=True, text=True)
    assert result.returncode == 0, f"Playwright test failed: {result.stderr}"
    assert "All tests passed" in result.stdout, "Some tests failed"
    print(result.stdout)