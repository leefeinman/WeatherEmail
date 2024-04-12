#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 21:01:30 2024

@author: leefeinman

"""


#%% Imports
import os
os.chdir('<Path/to/WeatherEmail')

import requests
from datetime import datetime
import pytz
import pandas as pd
from email.message import EmailMessage
import ssl
import smtplib
from openai import OpenAI
import time
import shutil
import boto3
from botocore.exceptions import ClientError
import mimetypes
from addresses import addresses # dictionary of the names & emails

#%% Get the weather data
lat = 39.95  # latitude to Disque Hall, Drexel U.
lon = -75.18  # longitude to Disque Hall, Drexel U.
api_key = "<3HR FORECAST FOR 5 DAYS API KEY>
call = f"https://api.openweathermap.org/data/2.5/forecast?lat={
    lat}&lon={lon}&units=imperial&appid={api_key}"

json_url = call
response = requests.get(json_url)

if response.status_code == 200:
    # Parse JSON
    json_data = response.json()
else:
    print('Failed to fetch JSON data:', response.status_code)


    # %%% initialize our data
time_PHL = []
temp = []
humidity = []
wind = []
desc = []
icon_code = []

count = 1
for hour, _ in enumerate(json_data["list"]):
    weather_data = json_data["list"][hour]

    time_UTC = datetime.fromtimestamp(weather_data["dt"])
    local_timezone = pytz.timezone('US/Eastern')
     # convert UTC to local time
    time_PHL.append(time_UTC.astimezone(local_timezone))

    temp.append(round(weather_data["main"]["temp"]))  # F
    humidity.append(weather_data["main"]["humidity"])  # percent
    wind.append(round(weather_data["wind"]["speed"]))  # mph
     
    desc.append(weather_data["weather"][0]["description"]) # description of  weather
    icon_code.append(weather_data["weather"][0] # icon code for weather
                     ["icon"])  

    if hour == 6:
        break

# initialize  DataFrame
df = pd.DataFrame({
    'Time': time_PHL,
    'temp': temp,
    'humidity': humidity,
    'wind': wind,
    'desc': desc,
    'icon_code': icon_code
})

df.set_index('Time', inplace=True) # make datetime the index
df.index = df.index.strftime('%I:%M %p')  # setting format of time

    # %%% Create the plot
 # re-importing necessary libraries after code execution state reset
from PIL import Image, ImageDraw, ImageOps
import seaborn as sns
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.pyplot as plt

 # reset rcParams
plt.rcParams.update(plt.rcParamsDefault)
plt.rcParams.update({
    'font.family': 'Futura',
    'font.stretch': 'expanded',
    'figure.dpi': 100,
})

 # set  dark background
plt.style.use('dark_background')

 # colors :)
dblue = sns.color_palette("colorblind")[0]
lblue = sns.color_palette("colorblind")[9]

 # open a figure
plt.figure(figsize=(11, 5))

 # calculate ymax & ymin dynamically
max_temp = df['temp'].max()
if max_temp < 110:
    ymax = max_temp + 7
else:
    ymax = max_temp
min_temp = df['temp'].min()
if min_temp > 30:
    ymin = min_temp - 3
else:
    ymin = min_temp

 # plot temp
plt.plot(df.index, df['temp'], marker='o', linestyle='-',
         linewidth=4, color=dblue, label='Temperature')
plt.fill_between(df.index, df['temp'], color=lblue, alpha=0.4)
plt.tick_params(axis='x', labelsize=16, pad=8)
plt.tick_params(axis='y', labelsize=22, pad=8)
plt.gca().yaxis.set_major_locator(plt.MaxNLocator(6))

plt.ylim(0, ymax) # Set ymax dynamically
plt.ylim(ymin, None) # Set ymin dynamically

 # add relevent icons for each data point
for index, row in df.iterrows():
    img = Image.open(f"Appleicons/{row['icon_code']}.png")
    img.thumbnail((30, 30))
    imagebox = OffsetImage(img)
    ab = AnnotationBbox(imagebox, (index, row['temp']), frameon=False)
    plt.gca().add_artist(ab)

 # set labels and title
plt.ylabel('°F', fontsize=24, rotation=0, labelpad=30)

 # add grid
plt.grid(alpha=0.2, linewidth=2, zorder=0)
plt.tick_params(axis='both', which='both',
                bottom=False, top=False, left=False, right=False,
                )

 # get rid of the frame & tidy up
for spine in plt.gca().spines.values():
    spine.set_visible(False)           
plt.tight_layout(pad = 2)

# show/save plot
# plt.show()
plt.savefig('images/fig.jpg')

        #%%%% round the plot's corners
 # open the plot .jpg
img = Image.open('images/fig.jpg')

 # create mask with round corners
mask = Image.new('L', img.size, 0)
draw = ImageDraw.Draw(mask)
radius = 30  
draw.rounded_rectangle([(0, 0), img.size], radius, fill=255)

 # apply the mask
rounded_img = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
rounded_img.putalpha(mask)

# save
date = datetime.fromtimestamp(json_data["list"][0]["dt"]) # UTC but who cares !!! reusing this var later
plot_fn = "plot-" + date.strftime("%B-%d-%Y") + ".png"
rounded_img.save("images/" + plot_fn)

    #%%% Create the Table
df = df.rename(columns={'desc': 'description'}) # rename desc. column

 # reset rcParams
plt.rcParams.update(plt.rcParamsDefault)
plt.rcParams.update({
    'font.family': 'Futura',
    'font.stretch': 'expanded',
    'figure.dpi': 100,
})

 # set dark background
plt.style.use('dark_background')

 # create a figure
fig, ax = plt.subplots(figsize=(8, 2))
ax.axis('tight')
ax.axis('off')

 # make table from df
table = ax.table(cellText=df.values.T[:-1].T, rowLabels=df.index, colLabels=df.columns,
                 loc='center',
                 cellLoc='center',
                 # cellColours = "black"
                 )

 # change color of border lines and text
for key, cell in table.get_celld().items():
    cell.set_linewidth(0.75)  # set border width
    cell.set_edgecolor('white')  
    cell.set_facecolor('black')  # set cell background to black
    cell.set_text_props(color='white')  # set text to white

 # tidy up
plt.tight_layout()

 # save the plot as an image file with high resolution
plt.savefig("images/table.jpg", dpi = 150)

        #%%%% round the table's corners
 # open table as image
img2 = Image.open("images/table.jpg")

 # create another mask with round corners
mask2 = Image.new('L', img2.size, 0)
draw2 = ImageDraw.Draw(mask2)
radius = 30 # sameas before
draw2.rounded_rectangle([(0, 0), img2.size], radius, fill=255)

 # apply the new mask
rounded_img = ImageOps.fit(img2, mask2.size, centering=(0.5, 0.5))
rounded_img.putalpha(mask2)

 # save
table_fn = "table-" + date.strftime("%B-%d-%Y") + ".png"
rounded_img.save("images/" + table_fn)

#%% Prep data for email

 #### each tertiary cell below (#%%%) will create data input for AI assistant
 # --cont'd--> as well as the non-AI response material.

    #%%% Date
 # format the date (this will be the full statement for this section)
formatted_date = date.strftime("%A, %B %d, %Y")

    #%%% Location
 # (this will be the full statement for this section)
location = "The greatest city in the world. Philly, baby."

    #%%% Weather
  # for the input to the AI assistant (this is how it learns the weather data)
weather_forecast = ""
for t, description in df["description"].items():
    weather_forecast += f"at {t}: {description}, "
weather_forecast = weather_forecast[:-2]    
    
    #%%% Temp
 # for the input to the AI assistant (this is how it learns the temp data)
temp_forecast = ""
for t, temp in df["temp"].items():
    temp_forecast += f"at {t}: {temp} degrees F, "
temp_forecast = temp_forecast[:-2]
temp_forecast


# to supplement to the AI response: 
    # index of the max & min temp 
max_temp_index = df['temp'].idxmax()
min_temp_index = df['temp'].idxmin()
    # max & min temp
max_temp = df.loc[max_temp_index, 'temp']
min_temp = df.loc[min_temp_index, 'temp']

    # statement
temp_statement = f"(high of {max_temp} at {max_temp_index} and low of {min_temp} at {min_temp_index})"

    #%%% Wind
 # for the input to the AI assistant (this is how it learns the wind data)
wind_forecast = ""
for t, wind_speed in df["wind"].items():
    wind_forecast += f"at {t}: {wind_speed} mph, "
wind_forecast = wind_forecast[:-2]
wind_forecast

# to supplement to the AI response: 
    # max wind speed and its time
max_wind_time = df["wind"].idxmax()
max_wind_speed = df["wind"].max()
max_wind = f"(wind will max out at {max_wind_time}. Around {max_wind_speed} mph is expected)"

    #%%% Humidity
 # for the input to the AI assistant (this is how it learns the humidity data)
humidity_forecast = ""
for t, humidity in df["humidity"].items():
    humidity_forecast += f"At {t}: {humidity} %, "
humidity_forecast = humidity_forecast[:-2]
humidity_forecast

# to supplement to the AI response: 
    # max humidity % and its time
max_humid_time = df["humidity"].idxmax()
max_humidity_val = df["humidity"].max()
max_humidity = f"(humidity will max out at {max_humid_time} at about {max_humidity_val} %)"

#%%Draft email
    #%%%Initialize OpenAI client
client = OpenAI(
    api_key='<YOUR OPENAI API KEY'
)

 # make the table .pdf so the assistant can view it
img3 = Image.open('images/table.jpg')
img3.save('images/table.pdf', 'PDF')

 # open the table
file = client.files.create(
    file=open('images/weatherforphl.pdf', "rb"),
    purpose='assistants'
)

assistant = client.beta.assistants.create(
    instructions="""
You are an jokester physical chemistry student from Australia who loves to surf.
You are being tasked with giving a weather report based off some information
about the weather at a particular location. This information is from the early 
morning and spans all day, so you have a good idea of what the weather forecast
will be. Be brief and be funny. DO NOT use fowl language!

This message will be sent to a class of physical chemistry students with their
professor. 

All of the weather information is available in the form of a table. 
""",
    model="gpt-4-turbo-preview",
    tools=[{"type": "retrieval"}],
    file_ids=[file.id]
)

thread = client.beta.threads.create()

questions = [
f"""Here is some weather forecast data for Philadelphia, PA (the greatest city ever) today.

Temperature: {temp_forecast}
Wind: {wind_forecast}
humidity: {humidity_forecast}
Description of weather: {weather_forecast}
""",
"""So, what's the weather like today?
Is it going to be good weather for time spent outside?
Will we be able to surf?
Should we bring an umbrella to campus? A jacket?
Should I try tanning today? 

**Please answer in 3 sentences or less.
Do not format your response with bullets or dashes.
Just respond with sentences. Also, please refrain from just reiterating data.**

""",
"""What about will the temps be?
What's a good activity in Philadelphia to do at these temps?
(please do not share the high and low temperatures.) 

**Please answer in 3 sentences or less.
Do not format your response with bullets or dashes.
Just respond with sentences. Also, please refrain from just reiterating data.**
""",
"""Is it windy outside? Will the wind impact the bikers? The surfers?
Please compare today's wind data to a Category 5 hurricane. If Benjamin Franklin were to fly his kite in today's wind, what would be the outcome?


**Please answer in 3 sentences or less.
Do not format your response with bullets or dashes.
Just respond with sentences. Also, please refrain from just reiterating data.**
""",
"""In the same light as the prior questions, how is the humidity?
Are we closer to the Amazon Rainforest humidity-wise or the Sahara Desert humidity-wise?
Analyze today's humidity in the context of its effect on urban air quality and the formation of photochemical smog. How do these conditions alter the concentration of pollutants or the formation of ozone in the lower atmosphere?

**Please answer in 3 sentences or less.
Do not format your response with bullets or dashes.
Just respond with sentences. Also, please refrain from just reiterating data. Please keep your answer light-hearted and funny!**
"""
]

answers = []
ind = 0
for answer in range(len(questions)):
    # Send the question to the assistant
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=questions[ind]
    )

    # Create a run to process the question
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Answer the user's questions to the best of your ability using the instructions provided."
    )

    # Wait for the run to complete
    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run.status == "completed":
            print("Needed info gathered. Starting response.")
            break
        elif run.status == ("failed" or "canceled"):
            print("Run failed/cancelled... moving on ")
            raise TimeoutError("Run failed...")
            break

        time.sleep(0.1)

    # Retrieve the assistant's response
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    answers.append(messages.data[0].content[0].text.value)

    ind += 1
    

 # clean up
client.beta.assistants.files.delete(
    assistant_id=assistant.id,
    file_id=file.id
)


    #%%% Load the HTML template
with open('WeatherEmailTemplate.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

    #%%% Edit the HTML file

 # IT'S UGLY I KNOW. SHUT UP. IT'S A SMALL HTML FILE.
html_content = html_content.replace('{DATE}', formatted_date)
html_content = html_content.replace('{LOCATION}', location)
html_content = html_content.replace('{WEATHER}', answers[1])
html_content = html_content.replace('{TEMPERATURE}', answers[2]+"<br>" + '<b>' + temp_statement + '</b>')
html_content = html_content.replace('{WIND}', answers[3]+"<br>" + '<b>' + max_wind + '</b>')
html_content = html_content.replace('{HUMIDITY}', answers[4]+ "<br>" + '<b>' + max_humidity + '</b>')
html_content = html_content.replace('{PLOT}', plot_fn)
html_content = html_content.replace('{TABLE}', table_fn)

#%% Send Email 

    #%%% Upload images to website host
website_dir = '/Users/lvf27/Documents/personalwebsite/html5up-dimension/images'
 # copying images to proper directory
shutil.copy("images/" + plot_fn, website_dir) 
shutil.copy("images/" + table_fn, website_dir)
    

  # accessing & updating AWS S3 bucket
s3_client = boto3.client('s3')
def upload_file(file_path, bucket, s3_path):
    try:
        mimetype, _ = mimetypes.guess_type(file_path)
        s3_client.upload_file(
            file_path,
            bucket,
            s3_path,
            ExtraArgs={
                "ContentType": mimetype
            } if mimetype != None else {})
        print(f"{file_path} uploaded")
    except ClientError as e:
        print(f"Error uploading {file_path} to {s3_path}: {e}")


def upload_directory(local_directory, bucket, s3_directory):
    for root, dirs, files in os.walk(local_directory):
        for file in files:
            if "caas" in file:
                pass
            
            local_path = os.path.join(root, file)
            s3_path = os.path.join(s3_directory, os.path.relpath(local_path, local_directory))
            upload_file(local_path, bucket, s3_path)


local_directory = "your directory for AWS s3 bucket update"
bucket = "your bucket name"
s3_directory = ""
upload_directory(local_directory, bucket, s3_directory)

    #%%% Loop the dict & send the emails!

 # email subject and error message
subject = "Daily Weather Update!"
body = """ 
Weather information should be here. Sorry if it's not!
""" # this is only seen if there is an html error

 # a little security b/c it has never hurt nobody
context = ssl.create_default_context()
    
for name, email in addresses.items():
     # adding name
    final_html = html_content.replace('[Recipient Name]', name)
    
    email_receiver = email # email address
    email_sender = "sender@gemailservice.com" # sending account
    email_password = "email service access code/password" # secret info!

     # create + format the EmailMessage() object
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)
    em.add_alternative(final_html,
                        subtype='html')

     # just gonna send it
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
                
              
    