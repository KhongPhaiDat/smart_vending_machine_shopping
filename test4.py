import pytz
from datetime import datetime

# Set the timezone you want to use
timezone = pytz.timezone("America/New_York")

# Get the current time in that timezone
time_in_timezone = datetime.now(timezone)

print(time_in_timezone)
