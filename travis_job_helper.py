#!/usr/bin/env python

from curses.ascii import isprint
from datetime import timedelta, datetime
import re
import os

from travis_job import TravisJob

sanitize1 = re.compile(r'\x1B\[(([0-9]{1,2})?(;)?([0-9]{1,2})?)?[m,K,H,f,J]')
sanitize2 = re.compile(r'^M\n')
startup_duration_regex = \
    re.compile(r'((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)?)(.\d+)?s')


def __strip_meta_characters(log_string):

    out = log_string
    out = sanitize1.sub('', out)
    out = sanitize2.sub('', out)
    out = "".join(filter(isprint,out))

    return out


def __extract_startup_duration(duration_string):
 

    parts = startup_duration_regex.match(duration_string)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}

    for (name, param) in parts.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params).seconds


def __extract_job_base(log_file):
    
    if '_' in log_file:
        log_file_name = os.path.splitext(os.path.basename(log_file))[0]
        log_file_split = log_file_name.split('_')

        build_number = int(log_file_split[0])
        commit_hash = str(log_file_split[1])
        job_id = int(log_file_split[2])

        return TravisJob(build_number, commit_hash, job_id)
    else:
        raise Exception("File name format error in {}. File name contains different segments."
              .format(log_file))


def __convert_timestamp_to_datetime(timestamp):


    if not timestamp == 0 or timestamp is not None:
       
        ts = int(timestamp)/1000000000
        return datetime.utcfromtimestamp(ts).replace(microsecond=0)
    else:
        return None


def parse_job_log_file(log_file_path):
    if os.path.isfile(log_file_path):

        job_startup_duration = None
        job_worker_hostname = None
        job_worker_version = None
        job_worker_instance = None
        job_os_dist_id = None
        job_os_dist_release = None
        job_os_description = None
        job_build_language = None
        job_using_worker_header = None
        job_travis_fold_worker_info = False
        job_travis_fold_system_info = False
        job_travis_fold_count = 0
        job_step_first_start = None
        job_step_last_end = None
        job_duration_aggregated_timestamp = None
        job_duration_diff_timestamp = None

        job = __extract_job_base(log_file_path)

        first_line = True
        os_details_coming = False
        worker_details_coming = False

        with open(log_file_path, "r") as log:
            for raw_line in log:
                line = __strip_meta_characters(raw_line)

                # Worker Header
                if first_line and line.startswith("Using worker"):
                    job_using_worker_header = True
                    job_worker_hostname = line.split(' ')[2]
                    first_line = False

                # Fold count
                elif line.startswith("travis_fold:start"):
                    job_travis_fold_count += 1

                # System/OS Info
                elif line.startswith("travis_fold:start:system_info"):
                    job_travis_fold_system_info = True
                    os_details_coming = True

                elif line.startswith("travis_fold:end:system_info"):
                    os_details_coming = False

                # Worker Info
                elif line.startswith("travis_fold:start:worker_info"):
                    job_travis_fold_worker_info = True
                    worker_details_coming = True

                elif line.startswith("travis_fold:end:worker_info"):
                    worker_details_coming = False

                # Startup time
                elif line.startswith("startup:"):
                    job_startup_duration = \
                        int(__extract_startup_duration(line.split(' ')[1]))

                elif line.startswith("travis_time:end"):
                    timings = line.split(':')[3]

                    start_timings = timings.split(',')[0]
                    start_value = int(start_timings.split('=')[1])

                    finish_timings = timings.split(',')[1]
                    finish_value = int(finish_timings.split('=')[1])

                    duration_timings = timings.split(',')[2]
                    duration_value = int(duration_timings.split('=')[1])

                    # Milliseconds
                    duration_value_ms = duration_value / 1000000

                    if job_step_first_start is None:
                        job_step_first_start = __convert_timestamp_to_datetime(start_value)

                    job_step_last_end = __convert_timestamp_to_datetime(finish_value)

                    if job_duration_aggregated_timestamp is None:
                        job_duration_aggregated_timestamp = duration_value_ms
                    else:
                        job_duration_aggregated_timestamp += duration_value_ms

                    job_duration_diff_timestamp = (job_step_last_end - job_step_first_start).total_seconds()

                # System/OS Details
                if os_details_coming:
                    if line.startswith("Description:"):
                        job_os_description = line.split(":")[1]
                    elif line.startswith("Distributor ID"):
                        job_os_dist_id = line.split(":")[1]
                    elif line.startswith("Release:"):
                        job_os_dist_release = line.split(":")[1]
                    elif line.startswith("Build language"):
                        job_build_language = line.split(":")[1]

                # Worker Details
                if worker_details_coming:
                    if line.startswith("hostname:"):
                        job_worker_hostname = line.split(' ')[1]

                    if line.startswith("version:"):
                        job_worker_version = " ".join(line.split(' ')[1:])

                    if line.startswith("instance:"):
                        job_worker_instance = line.split(' ')[1]

            job.assign_properties(startup_duration=job_startup_duration,
                                  worker_hostname=job_worker_hostname,
                                  worker_version=job_worker_version,
                                  worker_instance=job_worker_instance,
                                  os_dist_id=job_os_dist_id,
                                  os_dist_release=job_os_dist_release,
                                  os_description=job_os_description,
                                  build_language=job_build_language,
                                  using_worker_header=job_using_worker_header,
                                  travis_fold_worker_info=job_travis_fold_worker_info,
                                  travis_fold_system_info=job_travis_fold_system_info,
                                  travis_fold_count=job_travis_fold_count,
                                  step_first_start=job_step_first_start,
                                  step_last_end=job_step_last_end,
                                  duration_aggregated_timestamp=job_duration_aggregated_timestamp,
                                  duration_diff_timestamp=job_duration_diff_timestamp
                                  )
            return job
