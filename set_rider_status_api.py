import configparser
import os
import time

from flask import Flask
from flask import jsonify
from flask import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
app = Flask(__name__)

config_path = "/app/config/settings.cfg"

geo_params = {}
geo_perms = {}
url = ""
username = ""
password = ""

@app.route('/get_status')
def get_status():
    # Load config options from the config file
    try:
        global url, username, password, geo_params, geo_perms

        if(os.path.exists(config_path)):
            config = configparser.ConfigParser()
            config.read(config_path)

            # Get the website details
            url = config.get('SITE', 'url')
            username = config.get('SITE', 'username')
            password = config.get('SITE', 'password')

            # Get the geolocation items from the config file
            geo_params = {
                "latitude": float(config.get('GEOLOCATION', 'latitude')),
                "longitude": float(config.get('GEOLOCATION', 'longitude')),
                "accuracy": int(config.get('GEOLOCATION', 'accuracy'))
            }

            geo_perms = {
                "origin": url,
                "permissions": ["geolocation"]
            }
        else:
            raise Exception("Config file not found in specified location")
    except Exception as ex:
        return_data = {
            "availability": "Unknown",
            "message": str(ex)
        }
        return str(return_data), 500

    # Open the Selenium browser and log in
    try:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option("prefs", { \
            "profile.default_content_setting_values.geolocation": 1
        })
        chrome_options.add_argument("--remote-debugging-port=9222")

        browser = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver', options=chrome_options)
        
        browser.execute_cdp_cmd("Page.setGeolocationOverride", geo_params)
        browser.execute_cdp_cmd("Browser.grantPermissions", geo_perms)
        browser.get(url)

        assert 'Bloodbikes - Riders - Set your availability' in browser.title

        menu_button = browser.find_element(By.ID, 'dropdownMenu1')  # Find the search box
        menu_button.click()

        user_input = browser.find_element(By.ID, 'emailInput')
        password_input = browser.find_element(By.ID, 'passwordInput')

        user_input.send_keys(username)
        password_input.send_keys(password)

        submit_button = browser.find_element(By.XPATH, "//form[@id='frm-login']/div[3]/div")
        submit_button.click()
    except Exception as ex:
        return_data = {
            "availability": "Unknown",
            "message": str(ex)
        }
        return str(return_data), 500

    # Once logged in, look at the visibility of he map
    try:
        time.sleep(3)
        assert 'As a rider' in browser.page_source

        map_element = browser.find_element(By.ID, 'mapid')
        map_element_visibility = map_element.is_displayed()

        return_data = {
            "available": str(map_element_visibility),
            "message": ""
        }
        return jsonify(return_data), 200
    except Exception as ex:
        return_data = {
            "availability": "Unknown",
            "message": str(ex)
        }
        return str(return_data), 500
    
@app.route('/set_status/<status_value>')
def set_status(status_value):      
    # Load config options from the config file
    try:
        global url, username, password, geo_params, geo_perms

        if(os.path.exists(config_path)):
            config = configparser.ConfigParser()
            config.read(config_path)

            # Get the website details
            url = config.get('SITE', 'url')
            username = config.get('SITE', 'username')
            password = config.get('SITE', 'password')

            # Get the geolocation items from the config file
            geo_params = {
                "latitude": float(config.get('GEOLOCATION', 'latitude')),
                "longitude": float(config.get('GEOLOCATION', 'longitude')),
                "accuracy": int(config.get('GEOLOCATION', 'accuracy'))
            }

            geo_perms = {
                "origin": url,
                "permissions": ["geolocation"]
            }
        else:
            raise Exception("Config file not found in specified location")
    except Exception as ex:
        return_data = {
            "result": "Error",
            "message": str(ex)
        }
        return str(return_data), 500

    # Determine what status we are trying to set
    try:
        print(f"Setting rider status to {status_value}")
        if (status_value == 'available'):
            availability_status = 'btnAvailable'
        elif (status_value == 'unavailable'):
            availability_status = 'btnUnavailable'
        else:       
            raise Exception("Unable to determine status to set")
    except Exception as ex:
        return_data = {
                "result": "Error",
                "message": str(ex)
            }
        return str(return_data), 500
    
    # Open the Selenium browser and log in
    try:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option("prefs", { \
            "profile.default_content_setting_values.geolocation": 1
        })
        chrome_options.add_argument("--remote-debugging-port=9222")

        browser = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver', options=chrome_options)

        browser.execute_cdp_cmd("Page.setGeolocationOverride", geo_params)
        browser.execute_cdp_cmd("Browser.grantPermissions", geo_perms)
        browser.get(url)

        assert 'Bloodbikes - Riders - Set your availability' in browser.title

        menu_button = browser.find_element(By.ID, 'dropdownMenu1')  # Find the search box
        menu_button.click()

        user_input = browser.find_element(By.ID, 'emailInput')
        password_input = browser.find_element(By.ID, 'passwordInput')

        user_input.send_keys(username)
        password_input.send_keys(password)

        submit_button = browser.find_element(By.XPATH, "//form[@id='frm-login']/div[3]/div")
        submit_button.click()
    except Exception as ex:
        return_data = {
            "result": "Error",
            "message": str(ex)
        }
        return str(return_data), 500

    # Call the JavaScript to set the appropriate status
    try:
        time.sleep(3)
        assert 'As a rider' in browser.page_source

        browser.execute_script(f"SetAvailability({availability_status})")
        return_data = {
            "result": "Success",
            "message": ""
        }
        return str(return_data), 200
    except Exception as ex:
        return_data = {
            "result": "Error",
            "message": str(ex)
        }
        return str(return_data), 500
    
if __name__ == "__main__":
    #app.debug = True
    app.run(host = '0.0.0.0')
