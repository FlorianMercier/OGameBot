from datetime import datetime, timedelta


def get_time():
    """Return current time"""
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


class Date:
    """Operations on datetime"""

    def __init__(self, time):
        """Create a datetime with the current year, month and day and the given [hour, minute, second]"""
        now = datetime.now()
        self.date = datetime(now.year, now.month, now.day, time[0], time[1], time[2])

    def get_next_day(self):
        """Increment the datetime by one day and return the new value"""
        self.date += timedelta(days=1)
        return self.date

    def is_after(self, time):
        """Check if a given datetime is after the class event time"""
        return time > self.date

    def is_after_string(self, time_string):
        """Check if a given string date is after the class event time"""
        return time_string > self.date.strftime("%d/%m/%Y %H:%M:%S")

    def is_now(self):
        """Check if the current time is after the class event time"""
        return datetime.now() > self.date
