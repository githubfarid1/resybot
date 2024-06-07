import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import logging
import random
import time
from playwright_stealth import stealth_sync
import logging
import re

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,id;q=0.8',
    'authorization': 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://resy.com',
    'priority': 'u=1, i',
    'referer': 'https://resy.com/',
    'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    'x-origin': 'https://resy.com',
}

payload = 'email=aseasease2005b%40gmail.com&password=6EAMGVu8mpwWb7*'


load_dotenv('settings.env')
email = os.getenv('RESY_EMAIL')
password = os.getenv('RESY_PASSWORD')
# PW_TEST_SCREENSHOT_NO_FONTS_READY = 1
# headless = False
headless = True
# made the file mode to overwrite the log file
logging.basicConfig(filename='bot.log', filemode='w', level=logging.INFO,  format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')

def random_delay(min_seconds, max_seconds):
    time.sleep(random.uniform(min_seconds, max_seconds))

def update_restaurant_link(restaurant_link, date, seats):
    # convert the date from string to datetime object and then return it to the correct format to avoid url errors
    date = datetime.strptime(date, "%Y-%m-%d").strftime('%Y-%m-%d')
    return restaurant_link.split("?")[0] + f"?seats={seats}&date={date}"


def login_to_resy(page, email, password):
    """Login to Resy with enhanced stability and error handling."""
    try:
        page.wait_for_selector('.AnnouncementModal__icon-close', timeout=5000)
        page.click('.AnnouncementModal__icon-close')
    except Exception:
        logging.info("No announcement modal to close.")
    # breakpoint()
    page.click("text=Log in", timeout=30000)
    page.click("text=Use Email and Password instead", timeout=30000)

    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)
    # breakpoint()
    # page.request.post("https://api.resy.com/3/auth/password", headers=headers, data=payload,)
    
    page.click('[name="login_form"] button', timeout=10000)
    # time.sleep(10)
    # page.get_by_role("button", name=re.compile("continue", re.IGNORECASE)).click()
    # page.click("text=Continue", timeout=5000)
    # page.click('/html/body/div[8]/div/div/div/div/div[2]/div[2]/div/form/div/button', timeout=5000)
    
    # breakpoint()
    # page.evaluate("document.querySelector('[name=\"login_form\"] button').click()")
    page.evaluate("() => document.fonts.ready")
    # breakpoint()
    
    page.screenshot(path='debugging_photos/screenshot2.png')
    logging.info("Logged in and screenshot taken.")


def reserve_restaurant(page, selected_reservation):
    """Reserve the restaurant with improved error handling and explicit waits."""
    try:
        selected_reservation.click()
        frame_element = page.wait_for_selector('iframe[title="Resy - Book Now"]', timeout=10000)
        frame = frame_element.content_frame()
        frame.wait_for_selector('[data-test-id="order_summary_page-button-book"]', timeout=10000).click()
        breakpoint()
        confirmation_message = frame.query_selector('.ConfirmationPage__header').inner_text()
        logging.info(f"Reservation confirmation message: {confirmation_message}")
        logging.info("Reservation confirmed.")
        page.evaluate("() => document.fonts.ready")
        page.screenshot(path='debugging_photos/screenshot3.png')
    except Exception as e:
        logging.exception("Failed to complete reservation")


def main(restaurant_link, date_wanted, seats, time_wanted, period_wanted, reservation_type):
    # breakpoint()
    try:
        # update the restaurant link
        restaurant_link = update_restaurant_link(restaurant_link, date_wanted, seats)

        # Rotate user agents or use more realistic ones
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
            # 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0'
            # More user agents can be added here
        ]
        user_agent = random.choice(user_agents)

        # Start the bot
        with sync_playwright() as p:
            wargs = []
            # wargs.append('--enable-logging=stderr')
            wargs.append('--v=1')
            wargs.append('--no-sandbox')
            wargs.append('--enable-features=NetworkService,NetworkServiceInProcess')
            wargs.append('--enable-automation')
            wargs.append('--disable-popup-blocking')
            wargs.append('--disable-web-security')

            browser = p.firefox.launch(headless=headless, args=wargs)
            proxy_server = "http://kpeqkzlp:0sdrl0jganhc@38.154.227.167:5868"

            context = browser.new_context(
                user_agent=user_agent,
                viewport={'width': random.randint(1200, 1920), 'height': random.randint(900, 1080)},
                # viewport={'width': 1920, 'height': 1080},
                permissions=['geolocation', 'notifications'],
                java_script_enabled=True,
                # no_viewport=True,
                # bypass_csp=True,
                locale='US_en',
                # geolocation=False,
                
                #proxy = {
                #'server': proxy_server
            #}
            )
            breakpoint()
            page = context.new_page()
            stealth_sync(page)
                        
            page.on("console", lambda msg: logging.debug(f"PAGE LOG: {msg.text}"))
            page.on("pageerror", lambda msg: logging.error(f"PAGE ERROR: {msg}"))
            page.on("response", lambda response: logging.debug(f"RESPONSE: {response.url} {response.status}"))
            page.on("requestfailed", lambda request: logging.error(f"REQUEST FAILED: {request.url} {request.failure}"))
            logging.info("Bot is running...")
            # Login to Resy
            # breakpoint()
            page.goto("https://resy.com", timeout=60000)
                    
            # breakpoint()
            login_to_resy(page, email, password)
            logging.info("Logged in successfully.")
            random_delay(2, 5)
            # Go to restaurant page
            page.goto(restaurant_link, wait_until='networkidle')
            # page.goto(restaurant_link)
            page.wait_for_timeout(20000)
            # Take screenshot for debugging
            # breakpoint()
            page.evaluate("() => document.fonts.ready")
            time.sleep(5)
            page.screenshot(path="debugging_photos/screenshot1.png", timeout=120000)
            # breakpoint()
            menu = page.wait_for_selector(f'//div[contains(@class,"ShiftInventory__shift")][h2[text()="{period_wanted.lower()}"]]', timeout=120000)
            selected_reservation = menu.query_selector(f'//button[div[text()="{time_wanted}"]][div[text()="{reservation_type.lower().title()}"]]')
            if selected_reservation:
                logging.info(
                    f"Reservation available at {time_wanted} for {seats} people {reservation_type.lower().title()}")
                reserve_restaurant(page, selected_reservation)
                random_delay(3, 6)

            else:
                logging.info("No reservation available")
    except Exception as e:
        # Show all error details in log file
        logging.exception("An error occurred")
        return e


if __name__ == '__main__':
    restaurant_link = "https://resy.com/cities/london-england/venues/granger-and-co-chelsea?date=2024-05-15&seats=2"
    # restaurant_link = "https://resy.com/cities/new-york-ny/venues/don-angie?seats=2&date=2024-05-15"
    date_wanted = "2024-06-1"
    seats = 2
    time_wanted = "10:00 PM"
    period_wanted = "Dinner"
    reservation_type = "Dining Room"
    main(restaurant_link, date_wanted, seats, time_wanted, period_wanted, reservation_type)
