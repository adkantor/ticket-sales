import json
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib, ssl

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from config import settings

PATH_TO_OUTFILE = 'outfile.json'
PATH_TO_IMAGE = 'report.png'
TOTAL_SEATS = 660


def get_data() -> list[dict] | None:
    try:
        with open(PATH_TO_OUTFILE, 'r') as f:
            return json.load(f)
    except:
        return None


def convert_to_df(data:list[dict] ) -> pd.DataFrame:
    timestamps = [datetime.datetime.fromisoformat(data_item['timestamp']) for data_item in data]
    remaining_seats = [data_item['data']['prices']['5000'] for data_item in data]

    return pd.DataFrame({
        'timestamp': timestamps,
        'remaining_seat': remaining_seats,
    })


def get_daily_df(df: pd.DataFrame) -> pd.DataFrame:
    result = df.resample('D', on='timestamp').last()
    return result


def get_hourly_df(df: pd.DataFrame) -> pd.DataFrame:
    result = df.resample('h', on='timestamp').last()
    return result


def plot_daily_df(df: pd.DataFrame):    
    fig, ax = plt.subplots()

    # set datetime axis
    fig.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))


    # add data
    bars = ax.bar(x=df.index, height=df['remaining_seat'], color='#f8bbd0', zorder=3)
    # add labels within box
    ax.bar_label(bars, label_type='center', rotation='vertical', fontsize=6)
    # add gridlines
    ax.yaxis.grid(which='major', color='lightgrey', zorder=0)
    # remove spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    # remove y axis ticks
    ax.tick_params(axis=u'both', which=u'both',length=0)
    # format x axis
    plt.gcf().autofmt_xdate(rotation=90, ha='center')


def plot_hourly_df(df: pd.DataFrame):    
    #x = pd.date_range(start='2024-09-03', end='2024-12-19', freq='h') # df.index
    x = df.index
    y = df['remaining_seat']

    fig, ax = plt.subplots()

    # set datetime axis
    fig.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))


    # add data
    ax.plot(x, y, color='#f8bbd0', zorder=3)
    plt.xticks(pd.date_range(start='2024-09-03', end='2024-12-19', freq='7D'))
    # add gridlines
    ax.yaxis.grid(which='major', color='lightgrey', zorder=0)
    # remove spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    # remove y axis ticks
    ax.tick_params(axis=u'both', which=u'both',length=0)
    # format x axis
    plt.gcf().autofmt_xdate(rotation=90, ha='center')
    # add y axis limits
    ax.set_ylim([0, 660])
    # show last value as annotation
    value = df['remaining_seat'].iloc[-1]
    coord_x = df.index[-1] + datetime.timedelta(days=3)
    coord_y = value - 10
    ann = ax.annotate(value, [coord_x, coord_y])
    ann.set_bbox(dict(facecolor='white', alpha=0.5, edgecolor='grey'))



def send_report(markdown_text: str, image_path: str):
    sender_email = settings.EMAIL_SENDER
    receiver_email = settings.EMAIL_RECEIVER
    password = settings.EMAIL_PASSWORD

    # Create the root message and fill in the from, to, and subject headers
    message = MIMEMultipart('related')
    message['Subject'] = 'MOM LC koncert - report'
    message['From'] = sender_email
    message['To'] = receiver_email
    message.preamble = 'This is a multi-part message in MIME format.'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    message_alternative = MIMEMultipart('alternative')
    message.attach(message_alternative)

    text = markdown_text
    part_text = MIMEText(text)
    message_alternative.attach(part_text)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    html = '<img src="cid:image1">'
    part_html = MIMEText(html, 'html')
    message_alternative.attach(part_html)

    # This example assumes the image is in the current directory
    with open(image_path, 'rb') as f:
        part_img = MIMEImage(f.read())
 

    # Define the image's ID as referenced above
    part_img.add_header('Content-ID', '<image1>')
    message.attach(part_img)

    # Send the email (this example assumes SMTP authentication is required)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(host=settings.EMAIL_HOST, port=settings.EMAIL_PORT, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            from_addr=sender_email, 
            to_addrs=receiver_email, 
            msg=message.as_string()
        )


# read file
data = get_data()
if data is None:
    raise SystemExit(0)

# convert to pandas df
raw_df = convert_to_df(data)
df_daily = get_daily_df(raw_df)
df_hourly = get_hourly_df(raw_df)

# visualize and save result
#plot_daily_df(df_daily)
plot_hourly_df(df_hourly)
plt.savefig(PATH_TO_IMAGE, dpi=300, bbox_inches='tight')
# convert to markdown
markdown_text = df_daily.to_markdown(index=True, tablefmt='pipe', colalign=['center'] * len(df_daily.columns))

# send report in email
send_report(markdown_text=markdown_text, image_path=PATH_TO_IMAGE)