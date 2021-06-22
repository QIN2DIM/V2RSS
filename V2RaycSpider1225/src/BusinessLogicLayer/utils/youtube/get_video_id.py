import datetime
import time

from selenium.webdriver import Chrome, ChromeOptions

from src.BusinessCentralLayer.setting import CHROMEDRIVER_PATH

url = "https://www.youtube.com/user/CBCtv/videos"

channel_id = url.split('/')[4]

options = ChromeOptions()

# options.add_argument("--user-data-dir=chrome-data")

driver = Chrome(executable_path=CHROMEDRIVER_PATH, options=options)

driver.get(url)

time.sleep(5)

dt = datetime.datetime.now().strftime("%Y%m%d%H%M")

height = driver.execute_script("return document.documentElement.scrollHeight")

last_height = 0

while True:
    if last_height == height:
        break
    last_height = height
    driver.execute_script("window.scrollTo(0, " + str(height) + ");")
    time.sleep(2)
    height = driver.execute_script("return document.documentElement.scrollHeight")

user_data = driver.find_elements_by_xpath('//*[@id="video-title"]')

for i in user_data:
    print(i.get_attribute('href'))
    file_name = f"{channel_id}-{dt}.list"
    with open(file_name, "a+") as f:
        f.write((i.get_attribute('href')) + "\n")

if __name__ == '__main__':
    pass
