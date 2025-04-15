#!/usr/bin/python3

from models.job import Job
from models.engine.db_manager import get_connection
from models.engine.db_manager import set_db_conn
from models.engine.app_tools import load_settings
from models.engine.app_tools import load_lines
from models.engine.app_tools import get_line_conn
from models.engine.job_manager import create_job
from models.engine.job_manager import get_all_jobs
from models.engine.job_manager import jobs_by_line
from models.engine.job_manager import check_job_order
from models.engine.job_manager import sort_jobs_by_order

# check App Settings
app_config = load_settings()
try:
    app_type = app_config["AppSettings"]["app_type"]
except:
    app_type = None
if app_type != "orders_manager":
    print("Error Settings ! please go to Setting")
    exit(1)
print("Welcome to Production Orders Manager")
# Load Lines
lines = load_lines()
if lines is None:
    print("no Lines Found! please add new Lines on Settings")
    exit(1)
for line in lines:
    print(line)
line_id = input("please Choose Line to Manage: ")
if line_id not in lines:
    print("Incorrect Line!!")
    exit(1)
db_conn = get_line_conn(line_id)
conn = get_connection(db_conn)
if conn is None:
    print("Connection to Database Failed")
    exit(1)
set_db_conn(db_conn)
print(f"Line {line_id} is Selected")
print("--------------------------")
while True:
    line_jobs = jobs_by_line(line_id)
    line_jobs = sort_jobs_by_order(line_jobs)
    if line_jobs is None:
        print("No Jobs Found")
        exit(1)
    print("Please Select Option:")
    print("1- Create New Job")
    print("2- Show Jobs")
    print("3- Update Job")
    print("4- Delete Job")

    option = input("Please Type Option Number: ")

    if option == "1":
        ref = input("Reference Input : ")
        quantity = input("Quantity to Produce: ")
        job_order = input("Order of the Job: ")
        check_job_order(int(job_order), line_jobs)
        if create_job(ref, line_id, quantity, job_order) is None:
            print("Job Creation Failed")
            continue
        print("Job Created Successfully")
        continue
    elif option == "2":
        line_jobs = jobs_by_line(line_id)
        line_jobs = sort_jobs_by_order(line_jobs)
        if line_jobs is None:
            print(f"No Jobs Found on {line_id}")
            continue
        for job in line_jobs:
            job_ref = job["reference"]
            job_line = job["line_id"]
            job_q = job["quantity"]
            job_p = job["picked"]
            job_r = job["remain"]
            job_s = job["job_status"]
            job_or = job["job_order"]
            print(f"Ref : {job_ref} | Line: {job_line} | Quantity: {job_q} | Picked: {job_p} | Remain: {job_r} | Status: {job_s} | Order: {job_or}")
            continue
    elif option == "3":
        if line_jobs is None:
            print(f"No Jobs Found on {line_id}")
            continue
        for job in line_jobs:
            job_id = job["id"]
            job_ref = job["reference"]
            job_line = job["line_id"]
            job_q = job["quantity"]
            job_p = job["picked"]
            job_r = job["remain"]
            job_s = job["job_status"]
            job_or = job["job_order"]
            print(f"ID : {job_id} | Ref : {job_ref} | Line: {job_line} | Quantity: {job_q} | Picked: {job_p} | Remain: {job_r} | Status: {job_s} | Order: {job_or}")
        selected_job = input("Insert Job ID to update: ")
        job_s = next((job for job in line_jobs if job["id"] == selected_job), None)
        if job_s is None:
            print(f"Job {selected_job} Not Found!!")
            continue
        id = job_s["id"]
        print(job_s["id"])
        while True:
            key = input("Insert Field to update (quantity-job_status-job_order): ")
            print(f"selected Field : {key}")
            value = input(f"Insert New Value for {key}: ")
            if key == "job_order":
                check_job_order(int(value), line_jobs)
                job_s["job_order"] = int(value)
                f = input("Update New Field?? \n1- Yes\n2- No\n")
                if f == "1":
                    continue
                else:
                    Job(**job_s).update()
                    print(f"Job {id} Updated Successfully")
                    key = ""
                    break     
            elif key == "quantity":
                if int(value) < job_s["quantity"] and int(value) < job_s["picked"]:
                    print(f"Picked : {job_s['picked']} GREATER then Quantity : {int(value)}")
                    continue
                job_s["quantity"] = int(value)
                job_s["remain"] = int(value) - job_s["picked"]
                f = input("Update New Field?? \n1- Yes\n2- No\n")
                if f == "1":
                    continue
                else:
                    Job(**job_s).update()
                    print(f"Job {id} Updated Successfully")
                    key = ""
                    break
            elif key == "job_status":
                job_s["job_status"] = value
                if job_s["job_status"] == value:
                    print(f"Job Status is {job_s['job_status']}")
                    break
                elif value == "closed":
                    job_s["job_status"] = "closed"
                    job_s["job_order"] = 0
                elif value == "pending" and job_s["job_status"] != "closed":
                    job_s["job_status"] = "pending"
                elif value == "paused":
                    job_s["job_status"] = "paused"
                    job_s["job_order"] = -1
                else:
                    print("Incorrect Job Status")
                    continue
                f = input("Update New Field?? \n1- Yes\n2- No\n")
                if f == "1":
                    continue
                else:
                    Job(**job_s).update()
                    print(f"Job {id} Updated Successfully")
                    key = ""
                    break
            else:
                print("Incorrect Choice!! Job Not Updated")
                continue
    elif option == "4":
        if line_jobs is None:
            print(f"No Jobs Found on {line_id}")
            continue
        for job in line_jobs:
            job_id = job["id"]
            job_ref = job["reference"]
            job_line = job["line_id"]
            job_q = job["quantity"]
            job_p = job["picked"]
            job_r = job["remain"]
            job_s = job["job_status"]
            job_or = job["job_order"]
            print(f"ID : {job_id} | Ref : {job_ref} | Line: {job_line} | Quantity: {job_q} | Picked: {job_p} | Remain: {job_r} | Status: {job_s} | Order: {job_or}")
        selected_job = input("Insert Job ID to Delete: ")
        job_s = next((job for job in line_jobs if job["id"] == selected_job), None)
        if job_s is None:
            print("Job Not Found")
            continue
        Job(**job_s).delete()
        print(f"Job {selected_job} Deleted!!")
        continue
    else:
        print("Incorrect Selection!!")
        exit(1)