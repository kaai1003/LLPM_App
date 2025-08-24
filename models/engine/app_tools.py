#!/usr/bin/python3
"""App Tools Functions"""

import configparser
import json
import os
from models.tracker import Tracker
from models.harness import Harness
from models.engine.db_manager import get_list_obj
from models.engine.db_manager import get_obj
from datetime import datetime, timedelta
from collections import defaultdict

CONFIG_FILE = "settings/config.ini"
LINES_CONFIG = "settings/lines.ini"
DASH_CONFIG = "settings/dashboard.ini"

def load_settings():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config

def check_app_type():
    """check App Type"""
    app_config = load_settings()
    try:
        app_type = app_config["AppSettings"]["app_type"]
        return app_type
    except:
        return None

def load_lines():
    config = configparser.ConfigParser()
    config.read(LINES_CONFIG)
    if not config.sections():
        print("No lines found in the configuration file.")
        return None
    return config.sections()

def check_db_conn(id):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config.sections()

def get_line_conn(line_id):
    config = configparser.ConfigParser()
    config.read(LINES_CONFIG)
    if line_id in config:
        print(f"{line_id} Exist")
        return {key: value if key != "port" else int(value) for key, value in config[line_id].items()}
    print(f"line {line_id} Not Exist")
    return None

def picking_db_conn():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if "DATABASE" in config:
        print("Database Exist")
        return {key: value if key != "port" else int(value) for key, value in config["DATABASE"].items()}
    print(f"DATABASE Not Exist")
    return None

def get_line_id():
    app_config = load_settings()
    try:
        line_id = app_config["AppSettings"]["line_id"]
        return line_id
    except:
        return None

def get_line_details(line_id):
    """Get Line Details"""
    line_details = get_obj("lines", "line_id", line_id)
    if line_details:
        print(f"Line Details: {line_details}")
        return line_details
    return None
    
def insert_harness_track(refrence, cpt, line_id, process, status, batch_id, usercard):
    """Insert Harness Track"""
    harness_track = {'reference': refrence,
                         'compteur': cpt,
                         'line_id': line_id,
                         'process': process,
                         'harness_status': status,
                         'batch_id': batch_id,
                         'usercard': usercard
                         }
    Tracker(**harness_track).save()
    print(f"Harness Track {refrence} Inserted with Compteur {cpt}")
    return True

def insert_harness_details(refrence, cpt, line_id, process, result, batch_id, usercard):
    """Insert Harness Track"""
    harness_details = {'reference': refrence,
                         'compteur': cpt,
                         'line_id': line_id,
                         'process': process,
                         'test_result': result,
                         'batch_id': batch_id,
                         'usercard': usercard
                         }
    Harness(**harness_details).save()
    print(f"Harness Track {refrence} Inserted with Compteur {cpt}")
    return True


def get_dashboard_config(config_path=DASH_CONFIG):
    """Retrieve Dashboard config as a dictionary from the INI file"""
    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        return {}

    config.read(config_path)

    if "Dashboard" not in config:
        return {}

    # Convert the values to int where possible
    result = {}
    for key, value in config["Dashboard"].items():
        value = value.strip()
        if value == "":
            result[key] = ""
        else:
            try:
                result[key] = int(value)
            except ValueError:
                result[key] = value
    return result

def set_dashboard_config(data, config_path=DASH_CONFIG):
    """Create or update the Dashboard section in the INI config file"""
    config = configparser.ConfigParser()
    
    # Load existing file if it exists
    if os.path.exists(config_path):
        config.read(config_path)

    if "Dashboard" not in config:
        config["Dashboard"] = {}

    for key, value in data.items():
        config["Dashboard"][key] = str(value)

    # Write back to the file
    with open(config_path, 'w') as configfile:
        config.write(configfile)

def get_expected_fx(shift_range, shift_target):
    """
    Calculate expected number of scanned FX based on elapsed time in shift.

    Parameters:
        shift_range (str): shift time range in format "HH:MM-HH:MM"
        shift_target (int): total expected scanned FX for the full shift

    Returns:
        int: expected FX count at current time
    """
    try:
        # Parse shift range
        start_str, end_str = shift_range.split('-')
        now = datetime.now()
        today = now.date()

        start_time = datetime.strptime(start_str, "%H:%M").time()
        end_time = datetime.strptime(end_str, "%H:%M").time()

        start_dt = datetime.combine(today, start_time)
        end_dt = datetime.combine(today, end_time)

        # Handle overnight shifts (e.g., 22:00–06:00)
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)
            if now.time() < start_time:
                now += timedelta(days=1)  # Treat 02:00 as after 22:00

        # Calculate elapsed time
        if now < start_dt:
            elapsed_minutes = 0
        elif now >= end_dt:
            elapsed_minutes = (end_dt - start_dt).total_seconds() / 60
        else:
            elapsed_minutes = (now - start_dt).total_seconds() / 60

        total_minutes = (end_dt - start_dt).total_seconds() / 60

        if total_minutes == 0:
            return 0

        expected = (elapsed_minutes / total_minutes) * shift_target
        return int(expected)

    except Exception as e:
        print("Error in get_expected_fx:", e)
        return 0

def calculate_hourly_efficiency(shift_range, scanned_fx, ref_range_times, num_operators):
    shift_start_str, shift_end_str = shift_range.split("-")
    shift_start_time = datetime.strptime(shift_start_str, "%H:%M").time()
    shift_end_time = datetime.strptime(shift_end_str, "%H:%M").time()

    if not scanned_fx:
        # If no scanned_fx, return empty slots for current shift
        now = datetime.now()
        base_date = now.date()
        shift_start = datetime.combine(base_date, shift_start_time)
        shift_end = datetime.combine(base_date, shift_end_time)
        if shift_end <= shift_start:
            shift_end += timedelta(days=1)
        slots = []
        current = shift_start
        while current < shift_end:
            slots.append((current.strftime("%H:%M"), 0.0))
            current += timedelta(hours=1)
        return slots

    # Use the date of the first scan as reference
    first_scan_time = scanned_fx[0]["created_at"]
    base_date = first_scan_time.date()
    shift_start = datetime.combine(base_date, shift_start_time)
    shift_end = datetime.combine(base_date, shift_end_time)
    if shift_end <= shift_start:
        shift_end += timedelta(days=1)

    # Handle scans that occurred after midnight (e.g., 02:00 of next day)
    for fx in scanned_fx:
        if fx["created_at"] < shift_start:
            # That means the scan was likely after midnight in a night shift
            shift_start -= timedelta(days=1)
            shift_end -= timedelta(days=1)
            break

    # Generate hourly slots
    current = shift_start
    hourly_slots = []
    while current < shift_end:
        hourly_slots.append(current)
        current += timedelta(hours=1)

    ref_time_map = dict(ref_range_times)
    hourly_refs = {slot.strftime("%H:%M"): [] for slot in hourly_slots}

    for item in scanned_fx:
        scan_time = item["created_at"]
        ref = item["reference"]

        if ref not in ref_time_map:
            continue  # Unknown reference

        for slot in hourly_slots:
            if slot <= scan_time < slot + timedelta(hours=1):
                hour_key = slot.strftime("%H:%M")
                hourly_refs[hour_key].append(ref)
                break

    hourly_efficiencies = []
    for hour_str, refs in hourly_refs.items():
        total_time = sum(ref_time_map[ref] for ref in refs)
        efficiency = (total_time / num_operators) * 100 if num_operators else 0
        hourly_efficiencies.append((hour_str, round(efficiency, 2)))

    return hourly_efficiencies

def build_ref_range_times(scanned_fx, ref_info_list):
    # Extract unique references from scanned_fx
    scanned_refs = {item["reference"] for item in scanned_fx}

    # Create mapping from reference to range_time
    ref_map = {}
    for info in ref_info_list:
        ref = info.get("ref")
        range_time = info.get("cycle_time")
        if ref in scanned_refs and ref not in ref_map:
            ref_map[ref] = range_time  # Avoid duplicates

    # Convert to list of tuples
    return [(ref, ref_map[ref]) for ref in ref_map]

def compute_total_efficiency(shift_range, scanned_fx, ref_range_times, num_operators):
    """
    scanned_fx: list of scanned reference strings, e.g. ['12345 07', '12345 07', ...]
    ref_range_times: list of tuples -> [('12345 07', 2.6), ...]
    shift_range_str: string format 'HH:MM-HH:MM', e.g. '14:00-22:00'
    operators_count: int, number of present operators
    """
    # Parse shift start and end
    try:
        shift_start_str, shift_end_str = shift_range.strip().split('-')
    except ValueError:
        raise ValueError(f"Invalid shift_range format: {shift_range}, expected 'HH:MM-HH:MM'")

    # Create a mapping: ref -> range_time
    ref_range_dict = {ref: time for ref, time in ref_range_times}

    # Count each reference in scanned_fx only if it's in ref_range_dict
    ref_counts = {}
    for fx in scanned_fx:
        ref = fx.get("reference")  # or use the correct key name from your dicts
        if ref in ref_range_dict:
            ref_counts[ref] = ref_counts.get(ref, 0) + 1
    print(f"ref_count : {ref_counts}")
    # Compute numerator: sum(count * range_time) for each ref
    total_work_done = sum(ref_counts[ref] * ref_range_dict[ref] for ref in ref_counts)

    fmt = "%H:%M"
    now = datetime.now()
    current_time = datetime.strptime(now.strftime(fmt), fmt)
    shift_start = datetime.strptime(shift_start_str, fmt)
    shift_end = datetime.strptime(shift_end_str, fmt)

    # Handle overnight shift (e.g., 22:00-06:00)
    if shift_end <= shift_start:
        shift_end += timedelta(days=1)
        if current_time < shift_start:
            current_time += timedelta(days=1)

    if current_time < shift_start:
        elapsed_hours = 0  # shift hasn't started yet
    elif current_time > shift_end:
        elapsed_hours = (shift_end - shift_start).seconds / 3600
    else:
        elapsed_hours = (current_time - shift_start).seconds / 3600

    elapsed_hours = max(elapsed_hours, 1)  # avoid division by 0
    print(f"Elapsed Hours: {elapsed_hours}")

    # Compute efficiency
    denominator = num_operators * elapsed_hours
    if denominator == 0:
        return 0.0

    efficiency = (total_work_done / denominator) * 100
    return round(efficiency, 2)