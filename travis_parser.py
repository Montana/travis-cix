from concurrent.futures import ProcessPoolExecutor, as_completed
import glob
import os
import time
from shutil import copyfileobj


from travis_project import TravisProject
import travis_job_helper

input_folder = "input/"
output_folder = "output/"

repo_data_file = "repo-data-travis.csv"
build_log_file = "buildlog-data-travis.csv"
extracted_data_file = "extracted.csv"

parallel_enabled = True
parallel_workers = 8


def process_project(project_folder):
    project = create_project(project_folder)

    job_list = process_jobs(project_folder)
    project.assign_jobs(job_list)

    copy_repo_data_file(project_folder)
    copy_build_log_file(project_folder)

    write_to_csv(project)

    return project


def create_project(project_folder):
    project_folder_name = os.path.basename(os.path.basename(project_folder))

    project_info = project_folder_name.split('@')
    project_org = str(project_info[0])
    project_name = str(project_info[1])

    return TravisProject(project_org, project_name)


def process_jobs(project_folder):
    job_list = []

    log_listing = glob.glob(project_folder + os.sep + "*.log")
    for log_file in log_listing:
        job = travis_job_helper.parse_job_log_file(log_file)
        job_list.append(job)

    return job_list


def create_dir_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def copy_repo_data_file(project_folder):
    repo_log_source_file = project_folder + os.sep + repo_data_file
    repo_log_destination_file = output_folder + os.sep + os.path.basename(project_folder) + os.sep + repo_data_file

    create_dir_if_not_exists(os.path.dirname(repo_log_destination_file))

    if os.path.isfile(repo_log_source_file):
        remove_tz_label(repo_log_source_file, repo_log_destination_file)


def copy_build_log_file(project_folder):
    build_log_source_file = project_folder + os.sep + build_log_file
    build_log_destination_file = output_folder + os.sep + os.path.basename(project_folder) + os.sep + build_log_file

    create_dir_if_not_exists(os.path.dirname(build_log_destination_file))

    if os.path.isfile(build_log_source_file):
        
        remove_tz_label(build_log_source_file, build_log_destination_file)


def merge_log_files(folder_list, file_name):

    header_added = False
    with open(output_folder + os.sep + file_name, "wb") as out_file:
        for project_folder in folder_list:
            if os.path.isdir(project_folder):
                with open(output_folder + os.sep + os.path.basename(project_folder) + os.sep + file_name, "rb") as in_file:
                    if header_added:
                        in_file.__next__()
                    else:
                        header_added = True
                    copyfileobj(in_file, out_file)
            else:
                print(project_folder)


def remove_tz_label(source_file, out_file):

    first_line = True

    with open(source_file, "r") as infile:
        with open(out_file, "w") as outfile:
            for line_in in infile:
                if first_line:
                    outfile.write(line_in)
                    first_line = False
                else:
                    outfile.write(line_in.replace(' UTC,', ','))


def write_to_csv(project):
    destination_csv_file = output_folder + project.project_folder + os.sep + "extracted.csv"
    print(project.project_folder, "done. Writing to ", destination_csv_file)
    with open(destination_csv_file, 'w') as csv_file:

        csv_file.writelines(project.get_as_csv(with_header=True))


def main():
    project_list = []

    file_names = [extracted_data_file, build_log_file, repo_data_file]

    start_time = time.time()

    xfolder_list = [item for item in glob.glob(input_folder + os.sep + "*") if os.path.isdir(item)]
    folder_list = ["calabash@calabash-ios",
                   "assaf@vanity",
                   "DSpace@DSpace",
                   "eventmachine@eventmachine",
                   "fluent@fluentd",
                   "garethr@garethr-docker",
                   "GoogleCloudPlatform@DataflowJavaSDK",
                   "grpc@grpc-java",
                   "guard@listen",
                   "Homebrew@homebrew-nginx",
                   "Homebrew@homebrew-science",
                   "inaturalist@inaturalist",
                   "javaslang@javaslang",
                   "manshar@manshar",
                   "minimagick@minimagick",
                   "mockito@mockito",
                   "openSUSE@open-build-service",
                   "rails@rails",
                   "ruboto@ruboto",
                   "ruby@ruby",
                   "rubymotion@BubbleWrap",
                   "SpongePowered@SpongeAPI"]

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if parallel_enabled:
        with ProcessPoolExecutor(max_workers=parallel_workers) as executor:
            future_process_project = \
                {executor.submit(process_project, 'input' + os.sep + folder):
                    folder for folder in folder_list}

            { executor.submit(merge_log_files, project_list, file_name) : file_name for file_name in file_names }
    else:
        for folder in folder_list:
            project = process_project(folder)
            project_list.append(project)

    out_folder_list = [item for item in glob.glob(output_folder + os.sep + "*") if os.path.isdir(item)]

    for file_name in file_names:
        merge_log_files(out_folder_list, file_name)

    print("")

    end_time = time.time()
    print("Extraction done in %s" % (end_time - start_time))

if __name__ == '__main__':
    main()
