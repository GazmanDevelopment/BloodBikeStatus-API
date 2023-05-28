# Blood Bike Status API
I volunteer for [Blood Bikes Australia](http://www.bloodbikesaustralia.com.au/) and we need to flag our availability using a website that has been built for us.  The website is simple enough - login in, click a button to say "Available" or "Unavailable", if available it uses the location of your device to flag to potential users of the service where you are.

I happen to run a [Home Assistant](https://www.home-assistant.io/) setup at home and thought it would be cool to add the ability to view and change my status from any screen running the HASS interface.  Rather than code up a custom integration in HASS, I decided to learn Python and build an API that it can call.  This has also allowed me to code an automation that sets my status to "Unavailable" autmatically at 2030.  This avoids any issues where I forget to do so manually!

The result is this API which is designed to run on a Pi Zero W using Flask with gunicorn as the production QSGI server.  Using a Pi Zero W does have performance issues - a basic call takes about 90 seconds to respond.  Using a more powerful Pi would improve this (most of the time is spent spooling up selenium / chrome drivers) but would also be overkill unless you happen to have one spare or using it for something else.

## IMPORTANT
This API has no authentication on it.  It is designed to run in your local home network.  If you want to make this available from outside your home network, you *WILL* need to add authentication and encryption to the API / gunicorn.  This is beyond the scope of my project.

## Requirements
First you will need a Pi Zero W.  I used the following to build my mini-server.

- [Pi Zero W](https://core-electronics.com.au/raspberry-pi-zero-w-wireless.html)
- [Micro SD Card](https://core-electronics.com.au/32gb-microsd-card-with-noobs-for-all-raspberry-pi-boards.html)
- [Flirc Case](https://core-electronics.com.au/flirc-raspberry-pi-zero-case.html)

You will also need a way to flash the SD Card.  I use the below, but whatever works for you:

- [Micro SD Card Reader](https://core-electronics.com.au/usb-microsd-card-reader-writer-microsd-microsdhc-microsdxc.html)

## Initial Setup
1. Start by flashing the SD Card
   - The default version of the Raspberry Pi OS appears to have an issue with Selenium (used to interact with the website)
   - Download, install and run the Raspberry Pi Imager from [here](https://www.raspberrypi.com/software/)
   - Install the Buster version of the Pi OS
2. Insert the SD card in to the Pi and fire it up
   - Run through the initial steps to get the Pi running and connected to the network
   - Make sure you enable SSH access, you don't want to be connecting monitor, keyboard, mouse etc everytime you need to check something
     - Instructions [here](https://www.raspberrypi.com/documentation/computers/remote-access.html#setting-up-an-ssh-server)
3. Create a new directory to store the relevant files
   - You can either clone the respository, or manually create the three required files
   - You'll need to edit two fo the three anyway, so whatever goes!
5. Create a new text file in the directory called `requirements.txt`
   - Copy the contents of the `requirements.txt` file in GitHub in to the new file
   - Save and exit the file
6. Open a command prompt and type `sudo pip3 install -r requirements.txt`
   - This will install all the required components
   - There will be a few time-out / connection errors for some reason
7. Once that has finished type `sudo apt install --reinstall chromium-chromedriver`
   - Failing to do this results in weird selenium / chrome-driver errors 
8. Create a new folder called `config`
   - Create a new file in this folder called `settings.cfg`
   - Copy the contents of the in GitHub to this file
   - Edit the relevant values
     - Use Google to get the lat / long of your address
     - I use 10 as the accuracy
     - Use the username / password and URL provided by your coordinator
9. Create a new file called `set_rider_status_api.py`
   - Copy the contents of the `set_rider_status_api.py` to this file
   - Adjust the path to the congfig file
   - Use the full path from root for this

## Configure gunicorn
Instructions have been sourced from this tutorial: [Code Monk](https://www.javacodemonk.com/part-2-deploy-flask-api-in-production-using-wsgi-gunicorn-with-nginx-reverse-proxy-4cbeffdb)
1. Install `gunicorn`
    - At a command prompt type `sudo pip3 install gunicorn`
2. Test the process by typing `sudo gunicorn -w 4 -b 0.0.0.0:8000 set_rider_status_api:app`
   - If everything starts up, you should be OK to proceed
   - On another computer open a browser and type `<IP Address of Pi>:8000/get_status`
     - On a Pi Zero W, this will take about 90 seconds to get a response.  If you're using a more powerful Pi, you can expect a quicker response
     - If you get back something like `{"available":"True","message":""}`, the API is working
 3. At a command line type `sudo nano /etc/systemd/system/bloodbike.service`
 4. Enter the following, adjusting for your particular user

```[Unit]
Description=Gunicorn instance to serve the Blood Bikes Flask App
After=network.target

[Service]
User=your_username_here
Group=www-data
WorkingDirectory=/home/your_username_here/path_to_file
ExecStart=gunicorn -w 3 --timeout 120 --bind 0.0.0.0:8000 set_rider_status_api:app

[Install]
WantedBy=multi-user.target
```
5. Reload the configuration files by typing the following at a command line `sudo systemctl daemon-reload`
6. Start the service by typing the following at a command line `sudo systemctl start bloodbike.service`
7. Give service a minute or two then type `sudo systemctl status bloodbike.service`
   - You should see (in green) `active (running)`, and no errors listed
8. You can test the service is running by browsing to `<IP Address of Pi>:8000/get_status`, same as the step above
9. If you get the correct response, set this service to run on system start by typing the folloing at a command line `sudo systemctl enable bloodbike.service`
10. Restart the Pi and give it 5 minutes to reboot and start everything
11. Test the service again, you should now be up and running!
