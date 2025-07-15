#!/usr/bin/python3

from models.engine.job_manager import jobs_by_line
from models.engine.db_manager import get_obj
from models.job import Job

def display_jobs(line_id):
    # load line jobs
    line_jobs = jobs_by_line(line_id)
    if line_jobs is None:
        print("Error Loading Line Jobs")
        return None
    current_job = None
    current = False
    next = False
    paused = False
    closed = False
    for job in line_jobs:
        if job["job_order"] == 1 and job["job_status"] == "pending":
            current_job = job
            if current == False:
                print("--------------Current JOB:------")
            current = True
            print(f"Job ID: {job['id']} || Reference: {job['reference']} || Quantity: {job['picked']} / {job['quantity']}")
        elif job["job_order"] > 1 and job["job_status"] == "pending":
            if next == False:
                print("----------Next Jobs----------")
            next = True
            print(f"Job ID: {job['id']} || Reference: {job['reference']} || Quantity: {job['picked']} / {job['quantity']}")
        elif job["job_order"] == -1 and job["job_status"] == "paused":
            if paused == False:
                print("----------Paused Jobs----------")
            paused = True
            print(f"Job ID: {job['id']} || Reference: {job['reference']} || Quantity: {job['picked']} / {job['quantity']}")
        elif job["job_order"] == 0 and job["job_status"] == "closed":
            if closed == False:
                print("----------Closed Jobs----------")
            closed = True
            print(f"Job ID: {job['id']} || Reference: {job['reference']} || Quantity: {job['picked']} / {job['quantity']}")
    return current_job

def update_orders(line_id):
    # load line jobs
    line_jobs = jobs_by_line(line_id)
    for job in line_jobs:
        if job['job_order'] > 1:
            job['job_order'] -= 1
            Job(**job).update()
    return

def check_fusebox(ref):
    obj_ref = get_obj("reference", "ref", ref)
    if obj_ref["fuse_box"] == "NULL":
        return None
    return obj_ref["fuse_box"]