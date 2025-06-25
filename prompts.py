from playwright.sync_api import sync_playwright

def get_prompt(user_story, test_type, format_type, expected_result="", severity="", category="", framework="", style=""):
    instructions = "You are a senior QA engineer. Based on the user story below, generate "

    if format_type == "Manual Only":
        instructions += "manual test cases"
    elif format_type == "Automation Only":
        instructions += f"automation test scripts using {framework}"
    elif format_type == "Both":
        instructions += f"manual test cases and automation test scripts using {framework}"

    if test_type == "BDD (Gherkin)":
        instructions += " in BDD style"

    instructions += ".\n\n"

    style_instructions = ""
    if format_type != "Manual Only" and style:
        style_instructions += f"Use the {style} testing approach in the automation code.\n"

    extras = ""
    if expected_result:
        extras += f"Expected Result: {expected_result}\n"
    if severity:
        extras += f"Severity: {severity}\n"
    if category:
        extras += f"Test Category: {category}\n"

    framework_notes = ""
    if framework == "Robot Framework" and test_type == "BDD (Gherkin)":
        framework_notes += (
            "- Use *** Settings *** and *** Test Cases *** sections.\n"
            "- Format each test case with Given / When / Then keywords.\n"
            "- Use keywords like 'Input Text', 'Click Button', and 'Element Should Be Visible'.\n"
            "- Include setup and teardown if necessary.\n"
        )
    elif framework == "Cypress" and test_type == "BDD (Gherkin)":
        framework_notes += (
            "- Use Cucumber-style syntax.\n"
            "- Provide both .feature file and step definitions in JavaScript.\n"
            "- Step definitions should use Cypress commands like cy.visit, cy.get, cy.type, etc.\n"
        )
    elif framework == "Playwright" and format_type != "Manual Only":
        framework_notes += (
            "- Use Playwright's sync Python API.\n"
            "- Implement setup, actions, and assertions.\n"
            "- Each test function should correspond to one scenario.\n"
        )

    return f"""{instructions}
User Story:
\"\"\"
{user_story}
\"\"\"

{extras}{style_instructions}
Instructions:
- Number all manual test cases.
- For automation, include clean, working code for at least 2 key test cases.
- For BDD, follow Given-When-Then format.
- Use best practices for the selected framework.
{framework_notes}
"""

def build_playwright_python_prompt(description, style="default", test_data=None, metadata=None):
    return f"""
# Author: {metadata.get("author", "Unknown")}
# Title: {metadata.get("title", "Playwright Python Test")}
# Severity: {metadata.get("severity", "Medium")}
# Category: {metadata.get("category", "Functional")}

from playwright.sync_api import sync_playwright

def test_successful_login():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://example.com")
        page.fill("#username", "{test_data.get('username', 'testuser') if test_data else 'testuser'}")
        page.fill("#password", "{test_data.get('password', 'testpassword') if test_data else 'testpassword'}")
        page.click("#login_button")
        assert page.is_visible("#welcome_message")
        browser.close()
"""