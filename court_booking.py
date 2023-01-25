from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from rich import print
import time
import schedule
import json

# Username and password are stored in a json file, used for login.
with open('config.json') as config_file:
    config = json.load(config_file)

username = config['username']
password = config['password']

# Print day and time program was started
print(time.strftime("%d %B %Y %H:%M:%S") + " - Program Started")


def automated_booking():
    # print current time
    print(time.strftime("%H:%M:%S") + " - Booking Process Started")

    # ChromeDriver executable
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # Open the booking website
    driver.get('https://sportsbookings.ncl.ac.uk/Connect/mrmLogin.aspx')

    # Login buttons
    login_button = driver.find_element(By.XPATH, '//*[@id="form_1"]/div[1]/div/a')
    login_button.click()
    second_login_button = driver.find_element(By.XPATH, '//*[@id="Authenticate"]/fieldset/div[1]/div[2]/a')
    second_login_button.click()

    # Enter username, password then login
    username_field = driver.find_element(By.ID, 'username')
    username_field.send_keys(username)
    password_field = driver.find_element(By.ID, 'password')
    password_field.send_keys(password)
    final_login_button = driver.find_element(By.XPATH, '//*[@id="loginform"]/div[3]/button')
    final_login_button.send_keys(Keys.RETURN)

    # Load Volleyball Booking Page
    volleyball_button = driver.find_element(By.XPATH,
                                            '//*[@id="ctl00_MainContent__advanceSearchResultsUserControl_Activities_ctrl15_lnkActivitySelect_lg"]')
    volleyball_button.click()
    time.sleep(1)  # This sleep is necessary to allow the page to load

    # Move ahead 14 days
    for i in range(13):
        next_button = driver.find_element(By.ID, 'ctl00_MainContent_Button2')
        next_button.click()

    # At 00:00, refresh the page so that the new bookings are loaded
    schedule.every().day.at("00:00").do(driver.refresh)
    print(time.strftime("%H:%M:%S") + " - Refreshing Page")
    print("------------------------")

    # ----------------------------------------------------------------------------------------- #
    # //*[@id="ctl00_MainContent_grdResourceView"]/tbody/tr[7]/td/input xpath for 12:00 button  #
    # //*[@id="ctl00_MainContent_grdResourceView"]/tbody/tr[16]/td/input xpath for 21:00 button #
    # ----------------------------------------------------------------------------------------- #

    xpath_base = '//*[@id="ctl00_MainContent_grdResourceView"]/tbody/tr['

    # Checks 21:00 booking then works down to 12:00, will pick the first available booking
    for slot in range(16, 6, -1):
        xpath = xpath_base + str(slot) + ']/td/input'
        try:
            driver.find_element(By.XPATH, xpath).click()
        except:
            print(str(slot + 5) + ":00 slot not available")
        else:
            print(str(slot + 5) + ":00 slot took")
            break

    # Click the confirm button to take the booking, if no booking is available, the program will go back to waiting for the next day.
    try:
        confirm_button = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_btnBasket"]')
        confirm_button.click()
    except:
        print("------------------------")
        print("No bookings available")

    # Close the browser
    driver.close()


# Runs the program every day at 23:59
try:
    schedule.every().day.at("23:59").do(automated_booking)
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print(time.strftime("%d %B %Y %H:%M:%S") + " - Program Stopped")
except:
    print("An error has occurred")
