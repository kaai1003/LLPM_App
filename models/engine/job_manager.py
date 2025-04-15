#!/usr/bin/python3
"""Jobs Manager Functions"""

from models.engine.db_manager import get_connection
from models.engine.db_manager import get_all
from models.engine.db_manager import get_obj
from models.engine.db_manager import set_db_conn
from models.engine.app_tools import get_line_conn
from models.job import Job

def check_job(ref, line_id):
    """Check if a job exists for a given reference and line_id."""
    job = get_obj("production_jobs", "reference", ref)
    if job:
        if job["line_id"] == line_id:
            return True
        else:
            return False
    return False
    
def create_job(ref, line_id, qt, order):
    line_conn = get_line_conn(line_id)
    if line_conn is None:
        print(f"Line {line_id} does not exist.")
        return None
    conn = get_connection(line_conn)
    if conn is None:
        print(f"Connection to line {line_id} failed.")
        return None
    set_db_conn(line_conn)
    if check_job(ref, line_id):
        print(f"Job with reference {ref} already exists for line {line_id}.")
        return None
    new_job = {}
    if get_obj("reference", "ref", ref) is None:
        print(f"Reference {ref} does not exist.")
        return None
    new_job["reference"] = ref
    new_job["line_id"] = line_id
    new_job["superviseur"] = get_obj("lines", "line_id", line_id)["superviseur"]
    new_job["quantity"] = qt
    new_job["remain"] = qt
    new_job["job_order"] = int(order)
    new_job["job_status"] = "pending"
    return Job(**new_job).save()

def update_job(job_id, data):
    """Update job details."""
    job = get_obj("production_jobs", "id", job_id)
    if job is None:
        print(f"Job with ID {job_id} does not exist.")
        return None
    return Job(**data).update()

def delete_job(job_id):
    """Delete a job."""
    job = get_obj("production_jobs", "id", job_id)
    if job is None:
        print(f"Job with ID {job_id} does not exist.")
        return None
    return Job(**job).delete()

def get_job(ref, line_id):
    """Get job details."""
    job = get_obj("production_jobs", "refrence", ref)
    if job is None:
        print(f"Job with Ref {ref} does not exist.")
        return None
    return Job(**job).to_dict()

def get_all_jobs():
    """Get all jobs."""
    jobs = get_all("production_jobs")
    if jobs is None:
        print("No jobs found.")
        return None
    return jobs

def get_job_by_id(job_id):
    """Get job by ID."""
    job = get_obj("production_jobs", "id", job_id)
    if job is None:
        print(f"Job with ID {job_id} does not exist.")
        return None
    return job

def jobs_by_line(line_id):
    """Get jobs by line ID."""
    jobs = get_all("production_jobs")
    if jobs is None:
        print("No jobs found.")
        return None
    line_jobs = [job for job in jobs if job["line_id"] == line_id]
    return sort_jobs_by_order(line_jobs)

def check_job_order(order, jobs):
    sorted_jobs = sort_jobs_by_order(jobs)
    for job in sorted_jobs:
        if job["job_order"] == order:
            min_order = min(sorted_jobs, key=lambda x: x["job_order"])["job_order"]
            max_order = max(sorted_jobs, key=lambda x: x["job_order"])["job_order"]
            if order == int(min_order):
                for j in sorted_jobs:
                    j["job_order"] += 1
                    Job(**j).update()
                return
            elif order == int(max_order):
                job["job_order"] += 1
                Job(**job).update()
                return
            elif order > int(min_order) and order < int(max_order):
                for j in sorted_jobs:
                    if j["job_order"] >= order:
                        job["job_order"] += 1
                        Job(**job).update()
                return
    return

def sort_jobs_by_order(jobs):
    """Sort jobs by order."""
    sorted_jobs = sorted(jobs, key=lambda x: (x["job_order"] == 0, x["job_order"]))
    return sorted_jobs