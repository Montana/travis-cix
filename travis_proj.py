from travis_job import TravisJob

class TravisProject:

    def __init__(self, project_org, project_name):
        self.__project_org = project_org
        self.__project_name = project_name
        self.__jobs = None
        print("{} initialized.".format(self.project_folder))

    @property
    def project_folder(self):
        return self.__project_org + "@" + self.__project_name

    @property
    def project_org(self):
        return self.__project_org

    @property
    def project_name(self):
        return self.__project_name

    @property
    def job_list(self):
        return self.__jobs

    def assign_jobs(self, job_list):
        self.__jobs = job_list

    def get_as_csv(self, with_header=True):
        project_csv_entries = []
        project = self.__project_org + '/' + self.__project_name

        if with_header:
            project_csv_entries.append(TravisProject.get_csv_header())

        for job_entry in self.__jobs:
            project_csv_entries.append('"{}",{}\n'.format(project, job_entry.get_as_csv()))

        return project_csv_entries

    @staticmethod
    def get_csv_header():
        return "{},{}".format("project", TravisJob.get_csv_header())
