class TravisJob:


    def __init__(self, build_number, commit_hash, job_id):
        self.__build_number = build_number
        self.__commit_hash = commit_hash
        self.__job_id = job_id

       
        self.__startup_duration = None
        self.__worker_hostname = None
        self.__worker_version = None
        self.__worker_instance = None
        self.__os_dist_id = None
        self.__os_dist_release = None
        self.__os_description = None
        self.__build_language = None
        self.__using_worker_header = None
        self.__travis_fold_worker_info = False
        self.__travis_fold_system_info = False
        self.__travis_fold_count = 0
        self.__step_first_start = None
        self.__step_last_end = None
        self.__duration_aggregated_timestamp = None
        self.__duration_diff_timestamp = None

    @staticmethod
    def __csv_prep(param=None):
        if param is None:
            return 'NULL'
        elif isinstance(param, str) and len(param) > 0:
            return '"' + param + '"'
        else:
            return param

    @staticmethod
    def __cast_or_none(param, cast_type):
        return_value = param
        if param is not None:
            return_value = cast_type(param)

            if cast_type is str:
                return_value = return_value.strip()

        else:
            return_value = param

        return return_value

    @property
    def build_number(self):
        return self.__build_number

    @property
    def commit_hash(self):
        return self.__commit_hash

    @property
    def job_id(self):
        return self.__job_id

    def assign_properties(self,
                          startup_duration,
                          worker_hostname,
                          worker_version,
                          worker_instance,
                          os_dist_id,
                          os_dist_release,
                          os_description,
                          build_language,
                          using_worker_header,
                          travis_fold_worker_info,
                          travis_fold_system_info,
                          travis_fold_count,
                          step_first_start,
                          step_last_end,
                          duration_aggregated_timestamp,
                          duration_diff_timestamp
                          ):
        self.__startup_duration = TravisJob.__cast_or_none(startup_duration, int)
        self.__worker_hostname = TravisJob.__cast_or_none(worker_hostname, str)
        self.__worker_version = TravisJob.__cast_or_none(worker_version, str)
        self.__worker_instance = TravisJob.__cast_or_none(worker_instance, str)
        self.__os_dist_id = TravisJob.__cast_or_none(os_dist_id, str)
        self.__os_dist_release = TravisJob.__cast_or_none(os_dist_release, str)
        self.__os_description = TravisJob.__cast_or_none(os_description, str)
        self.__build_language = TravisJob.__cast_or_none(build_language, str)
        self.__using_worker_header = bool(using_worker_header)
        self.__travis_fold_worker_info = bool(travis_fold_worker_info)
        self.__travis_fold_system_info = bool(travis_fold_system_info)
        self.__travis_fold_count = TravisJob.__cast_or_none(travis_fold_count, int)
        self.__step_first_start = step_first_start
        self.__step_last_end = step_last_end
        self.__duration_aggregated_timestamp = TravisJob.__cast_or_none(duration_aggregated_timestamp, int)
        self.__duration_diff_timestamp = TravisJob.__cast_or_none(duration_diff_timestamp, str)

    def get_as_csv(self):
        return "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(
            TravisJob.__csv_prep(self.__build_number),
            TravisJob.__csv_prep(self.__commit_hash),
            TravisJob.__csv_prep(self.__job_id),
            TravisJob.__csv_prep(self.__startup_duration),
            TravisJob.__csv_prep(self.__worker_hostname),
            TravisJob.__csv_prep(self.__worker_version),
            TravisJob.__csv_prep(self.__worker_instance),
            TravisJob.__csv_prep(self.__os_dist_id),
            TravisJob.__csv_prep(self.__os_dist_release),
            TravisJob.__csv_prep(self.__os_description),
            TravisJob.__csv_prep(self.__build_language),
            TravisJob.__csv_prep(self.__using_worker_header),
            TravisJob.__csv_prep(self.__travis_fold_worker_info),
            TravisJob.__csv_prep(self.__travis_fold_system_info),
            TravisJob.__csv_prep(self.__travis_fold_count),
            TravisJob.__csv_prep(self.__step_first_start),
            TravisJob.__csv_prep(self.__step_last_end),
            TravisJob.__csv_prep(self.__duration_aggregated_timestamp),
            TravisJob.__csv_prep(self.__duration_diff_timestamp)
        )

    @staticmethod
    def get_csv_header():
        return "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
            "build_number",
            "commit_hash",
            "job_id",
            "startup_duration_seconds",
            "worker_hostname",
            "worker_version",
            "worker_instance",
            "os_dist_id",
            "os_dist_release",
            "os_description",
            "build_language",
            "using_worker_header",
            "travis_fold_worker_info",
            "travis_fold_system_info",
            "travis_fold_count",
            "step_first_start_datetime",
            "step_last_end_datetime",
            "duration_aggregated_milliseconds",
            "duration_diff_seconds"
        )
