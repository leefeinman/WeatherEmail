# WeatherEmail

## Setting up
For the .py script to work there are a few things that need to be setup:
- API's: OpenWeatherMap api key for the 3hr-5days forecast; OpenAI api key (make sure there are no restrictions; specifically for "assistants"), email "app password"
- Emails: should be saved in the adresses.py file (which is effectively just a dictionary imported by the main file)
- Icons: should be saved in a folder called "Appleicons" (at the same directory level). The icons chosen should have filenames matching those here https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2 .
- AWS: I am using my personal website (www.leefeinman.com) to host the images that will appear in the emails. This is why there is an AWS bucket updating section in the script. You may choose to remove this section and upload your images to another place for web hosting.

## True automation
For daily automation of the emails I am using:
- pmset (macOS): _pmset repeat wakeorpoweron 06:28 MTWRF_ -- this command will wake up OR turn on my computer at 6:28 every weekday in anticipation for... 
- crontab: _crontab -e_ --then--> (open VIM) --then--> _29 6 * * * /path/to/virtualenvironment/python3 /path/to/WeatherData.py_ -- the crontab job is scheduled to run the python script immediately after the computer wakeup.

## Important notes
Embedding images in an email is HARD. I've tried everything and the only thing that works consistently across email services (gmail, outlook, etc.) is making the HTML href source a web URL. This means that any images intended to be shared in the email must be hosted on the internet. I am using my own website (see AWS section above). Other options are Google Drive (see https://support.exclaimer.com/hc/en-gb/articles/4445816657309-How-to-host-images-using-Google-Drive) and Imgur.
