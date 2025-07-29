#!/usr/bin/python3


import configparser
from datetime import datetime, timedelta


def parse_time_range(shift_range):
    """Convert 'HH:MM-HH:MM' into tuple of datetime.time objects."""
    start_str, end_str = shift_range.split("-")
    start = datetime.strptime(start_str.strip(), "%H:%M").time()
    end = datetime.strptime(end_str.strip(), "%H:%M").time()
    return start, end

def parse_shift_datetime_range(shift_range):
    """
    Convert '22:00-06:00' to datetime range for current shift
    """
    now = datetime.now()
    start_str, end_str = shift_range.split('-')
    
    # Updated parsing to match new format 'HH:MM'
    start_time = datetime.strptime(start_str.strip(), "%H:%M").time()
    end_time = datetime.strptime(end_str.strip(), "%H:%M").time()

    today = now.date()
    start_datetime = datetime.combine(today, start_time)
    end_datetime = datetime.combine(today, end_time)

    # Night shift case: start time > end time (e.g., 22:00-06:00)
    if start_time > end_time:
        if now.time() < end_time:
            # Current time is after midnight but before end (e.g., 01:00)
            start_datetime -= timedelta(days=1)
        else:
            # Current time is after start (e.g., 23:00), so end is next day
            end_datetime += timedelta(days=1)

    return start_datetime, end_datetime

def time_diff_in_hours(start, end):
    """Compute difference in hours between two time objects (handle overnight)."""
    today = datetime.today()
    start_dt = datetime.combine(today, start)
    end_dt = datetime.combine(today, end)
    if end < start:
        end_dt += timedelta(days=1)
    return (end_dt - start_dt).total_seconds() / 3600


def is_time_in_range(start, end, now):
    """Check if current time is in the time range. Handles overnight shifts."""
    if start < end:
        return start <= now < end
    else:
        return now >= start or now < end


def get_current_shift(config_path="settings/config.ini"):
    config = configparser.ConfigParser()
    config.read(config_path)
    print(config.sections())
    if 'SHIFTS' not in config or 'AppSettings' not in config:
        raise ValueError("Missing required config sections")

    working_hours_per_shift = float(config["AppSettings"].get("working_hours", 0))
    if working_hours_per_shift <= 0:
        raise ValueError("Invalid 'working_hours' value. Must be > 0.")

    total_shift_hours = 0
    shift_times = []

    for shift_name, shift_range in config["SHIFTS"].items():
        start, end = parse_time_range(shift_range)
        hours = time_diff_in_hours(start, end)
        total_shift_hours += hours
        shift_times.append((shift_name, start, end, shift_range))

        if abs(hours - working_hours_per_shift) > 0.1:
            raise ValueError(f"{shift_name} duration ({hours}h) does not match configured shift length ({working_hours_per_shift}h)")

    # Validate total coverage
    if abs(total_shift_hours - 24.0) > 0.1:
        raise ValueError(f"Total shift coverage ({total_shift_hours}h) does not span 24 hours.")

    # Find current shift
    now = datetime.now().time()
    for shift_name, start, end, shift_range in shift_times:
        if is_time_in_range(start, end, now):
            return shift_name, shift_range

    return None, None

def working_hours(config_path="settings/config.ini"):
    """Get the configured working hours per shift."""
    config = configparser.ConfigParser()
    config.read(config_path)
    print(config.sections())
    if 'SHIFTS' not in config or 'AppSettings' not in config:
        return None

    working_hours_per_shift = float(config["AppSettings"].get("working_hours", 0))
    if working_hours_per_shift <= 0:
        return None
    return working_hours_per_shift