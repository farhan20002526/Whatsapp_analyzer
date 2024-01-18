import pandas as pd
from dateutil import parser
import re

# Updated Pattern
IS_STARTING_LINE = r"\[?(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4},?\s\d{1,2}[:.]\d{2}(\s?[apAP]\.?[mM]\.?)?)\]?\s?-\s?(.+)"

def preprocess(data):
    # Splitting data using the updated pattern
    matches = re.finditer(IS_STARTING_LINE, data)

    messages = []
    dates = []

    for match in matches:
        date_str, _, message = match.groups()
        dates.append(date_str.strip())
        messages.append(message.strip())

    # Creating DataFrame
    df = pd.DataFrame({'User_message': messages, 'message_date': dates})

    # Integration of parse_date logic into the preprocessing function
    df['message_date'] = df['message_date'].apply(parse_date)

    # Drop rows with None values in 'message_date'
    df = df.dropna(subset=['message_date'])

    # Convert 'message_date' to datetime type
    df['message_date'] = pd.to_datetime(df['message_date'], errors='coerce')

    # Drop rows with NaT (Not a Time) values in 'message_date'
    df = df.dropna(subset=['message_date'])

    # Now you can proceed with extracting additional date-related information
    df['year'] = df['message_date'].dt.year
    df['month'] = df['message_date'].dt.month_name()
    df['hour'] = df['message_date'].dt.hour
    df['minute'] = df['message_date'].dt.minute
    df['month_num'] = df['message_date'].dt.month
    df['only_date'] = df['message_date'].dt.date
    df['day_name'] = df['message_date'].dt.day_name()

    users = []
    messages = []

    for message in df['User_message']:
        entry = re.split('([\w\W]+?):\s', message, 1)  # Add maxsplit argument
        if entry[1:]:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['User_message'], inplace=True)

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df

def parse_date(date_str):
    try:
        # Attempt to parse the date string using dateutil.parser
        return parser.parse(date_str)
    except ValueError:
        # Handle parsing errors
        return None

# Example usage:
# Assuming 'chat_data' is your WhatsApp chat data
# df = preprocess(chat_data)
