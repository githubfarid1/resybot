import os
import time
import random
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager as CM
from selenium.webdriver.chrome.service import Service

load_dotenv('settings.env')
email = os.getenv('RESY_EMAIL')
password = os.getenv('RESY_PASSWORD')

logging.basicConfig(filename='bot.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')

def random_delay(min_seconds, max_seconds):
    time.sleep(random.uniform(min_seconds, max_seconds))

def update_restaurant_link(restaurant_link, date, seats):
    date = datetime.strptime(date, "%Y-%m-%d").strftime('%Y-%m-%d')
    return restaurant_link.split("?")[0] + f"?seats={seats}&date={date}"

def login_to_resy(driver, email, password):
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.AnnouncementModal__icon-close'))).click()
    except Exception:
        logging.info("No announcement modal to close.")

    driver.find_element(By.CSS_SELECTOR, '[data-test-id="menu_container-button-log_in"]').click()
    driver.find_element(By.LINK_TEXT, "Use Email and Password instead").click()
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, '[name="login_form"] button').click()
    driver.save_screenshot('debugging_photos/screenshot2.png')
    logging.info("Logged in and screenshot taken.")

def reserve_restaurant(driver, selected_reservation):
    try:
        selected_reservation.click()
        frame_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[title="Resy - Book Now"]')))
        driver.switch_to.frame(frame_element)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test-id="order_summary_page-button-book"]'))).click()
        confirmation_message = driver.find_element(By.CSS_SELECTOR, '.ConfirmationPage__header').text
        logging.info(f"Reservation confirmation message: {confirmation_message}")
        logging.info("Reservation confirmed.")
        driver.save_screenshot('debugging_photos/screenshot3.png')
    except Exception as e:
        logging.exception("Failed to complete reservation")

def main(restaurant_link, date_wanted, seats, time_wanted, period_wanted, reservation_type):
    try:
        restaurant_link = update_restaurant_link(restaurant_link, date_wanted, seats)

        options = webdriver.ChromeOptions()
        # adding headless mode
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--mute-audio")
        options.add_argument("--headless=new") 
        options.binary_location=" /usr/bin/google-chrome"
        # driver = webdriver.Chrome(options=options)
        breakpoint()
        driver = webdriver.Chrome(service=Service(executable_path=os.path.join(os.getcwd(), "webdriver", "chromedriver")), options=options)
   
        # breakpoint()
        driver.get("https://resy.com")
        login_to_resy(driver, email, password)
        random_delay(2, 5)

        driver.get(restaurant_link)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'ShiftInventory__shift') and .//h2[contains(text(),'" + period_wanted.lower() + "')]]")))
        selected_reservation = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[.//div[contains(text(), '" + time_wanted + "')]]")))

        if selected_reservation:
            logging.info(f"Reservation available at {time_wanted} for {seats} people {reservation_type.lower().title()}")
            reserve_restaurant(driver, selected_reservation)
            random_delay(3, 6)
        else:
            logging.info("No reservation available")
    except Exception as e:
        logging.exception("An error occurred")
        return e
    finally:
        driver.quit()

if __name__ == '__main__':
    restaurant_link = "https://resy.com/cities/london-england/venues/granger-and-co-chelsea?date=2024-05-15&seats=2"
    date_wanted = "2024-06-1"
    seats = 2
    time_wanted = "10:00 PM"
    period_wanted = "Dinner"
    reservation_type = "Dining Room"
    main(restaurant_link, date_wanted, seats, time_wanted, period_wanted, reservation_type)
