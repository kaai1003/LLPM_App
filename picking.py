#!/usr/bin/python3

from models.job import Job
import datetime
import keyboard
from models.engine.db_manager import get_connection
from models.engine.db_manager import set_db_conn
from models.engine.app_tools import load_settings
from models.engine.app_tools import picking_db_conn
from models.engine.app_tools import get_line_id
from models.engine.app_tools import insert_harness_track
from models.engine.app_tools import insert_harness_details
from models.engine.db_manager import get_obj
from models.engine.picking_manager import display_jobs
from models.engine.picking_manager import update_orders

# check App Settings
app_config = load_settings()
try:
    app_type = app_config["AppSettings"]["app_type"]
except:
    app_type = None
if app_type != "picking":
    print("Error Settings ! please go to Setting")
    exit(1)
print("Welcome to Harness Picking Application")

# load database settings
db_settings = picking_db_conn()

if db_settings is None:
    print("Error Loading Database Settings")
    exit(1)
print(get_connection(db_settings) is not None)
set_db_conn(db_settings)
line_id = get_line_id()
if line_id is None:
    print("Error Loading Line Settings")
    exit(1)
print(f"Line ID: {line_id}")
display = True
while True:
    if display:
        current_job = display_jobs(line_id)
        if current_job is None:
            print("No Jobs Found")
            exit(1)
    print("Please Press Enter to Pick Harness")
    print("Press ESC to Exit")
    key = keyboard.read_key()
    if key == "enter":
        ref = get_obj("reference", "ref", current_job["reference"])
        if ref is None:
            print(f"Reference {current_job['reference']} does not exist.")
            continue
        if ref["fuse_box"] != "NULL":
            fuse_box = input("Scan Fuse Box: ")
            if fuse_box != ref["fuse_box"]:
                print(f"Fuse Box {fuse_box} does not match with Reference {current_job['reference']}")
                display = False
                continue
        current_job["picked"] += 1
        current_job["remain"] -= 1
        if current_job["remain"] == 0:
            current_job["job_status"] = "closed"
            current_job["job_order"] = 0
            Job(**current_job).update()
            update_orders(line_id)
        else:
            Job(**current_job).update()
        print(f"Harness From Ref : {current_job['reference']} is Picked")
        cpt = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        insert_harness_track(current_job["reference"], cpt, line_id, 'Picking', 'OK')
        insert_harness_details(current_job["reference"], cpt, line_id, 'Picking', 'OK')
        display = True
        continue
    elif key == "esc":
        print("Exiting...")
        exit(0)
    else:
        print("Invalid Key Pressed")
        display = False
        continue