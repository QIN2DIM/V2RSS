from playwright.sync_api import sync_playwright, Page

register_url = "https://m.lemon77.im/auth/register"
login_url = "https://m.lemon77.im/auth/login"
user_url = "https://m.lemon77.im/user"

_email = "lemon77@gmail.com"
_password = "lemon77lemon77"


def login(page: Page, email: str, password: str):
    page.fill("#email", email)
    page.fill("#password", password)
    page.click("//button[@type='submit']")


def go():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(login_url)

        login(page, _email, _password)

        page.wait_for_url(user_url)

        print(page.locator("//span[@class='counter']").all_text_contents())


if __name__ == "__main__":
    go()
