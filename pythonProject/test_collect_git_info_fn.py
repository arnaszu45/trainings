import os
from pathlib import Path
import tempfile
import collect_git_info as cg
import subprocess
import shutil
import pytest


@pytest.fixture()
def temp_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture()
def temp_file():
    with tempfile.TemporaryFile() as temp_file:
        yield temp_file.name


def test_is_git_repo(temp_dir):
    subprocess.run(["git", "init"], cwd=temp_dir, check=True)
    result = cg.is_git_repo(Path(temp_dir))
    assert result


def test_is_git_repo_negative_not_git_repo(temp_dir):
    result = cg.is_git_repo(Path(temp_dir))
    assert not result


def test_is_git_repo_not_directory(temp_file):
    result = cg.is_git_repo(Path(temp_file))
    assert not result


def test_get_commits(temp_dir):
    subprocess.run(["git", "init"], cwd=temp_dir, check=True)
    filename = os.path.join(temp_dir, "filename.txt")
    with open(filename, "w") as f:
        f.write("hello")
    subprocess.run(["git", "add", "filename.txt"], cwd=temp_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Test"], cwd=temp_dir, check=True)
    result = cg.get_commits(Path(temp_dir))
    assert isinstance(result, list)
    assert len(result) == 1


def test_get_commits_empty_repo(temp_dir):
    subprocess.run(["git", "init"], cwd=temp_dir, check=True)
    result = cg.get_commits(Path(temp_dir))
    assert result == []


def test_get_commits_not_git_repo():
    temporary_dir = Path(tempfile.mkdtemp())
    result = cg.get_commits(temporary_dir)
    assert result == []


def test_get_author_and_date_from_git_log():
    string = """
Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>
Date:   2024-03-26 23:21:18 +0200
    """
    author, date = cg.get_author_and_date_from_git_log(string)
    assert author == "arnas.zuklija <arnas.zuklija@qdevtechnologies.com>"
    assert date == "2024-03-26 23:21:18 +0200"


def test_get_author_and_date_from_git_log_empty_author():
    string = """
    commit 0b44f202c497c7efb8599567c92b052ee573afc3
Author: 
Date: 2024-03-26 23:21:18 +0200
    """
    author, date = cg.get_author_and_date_from_git_log(string)
    assert author == ""
    assert date == "2024-03-26 23:21:18 +0200"


def test_get_author_and_date_from_git_log_empty_date():
    string = """
Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>
Date: 
    """
    author, date = cg.get_author_and_date_from_git_log(string)
    assert author == "arnas.zuklija <arnas.zuklija@qdevtechnologies.com>"
    assert date == ""


def test_get_author_and_date_from_git_log_no_author():
    string = """
    commit 0b44f202c497c7efb8599567c92b052ee573afc3
Date:   2024-03-26 23:21:18 +0200
    """
    author, date = cg.get_author_and_date_from_git_log(string)
    assert author == ""
    assert date == ""


def test_get_author_and_date_from_git_log_no_date():
    string = """
    commit 0b44f202c497c7efb8599567c92b052ee573afc3
Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>

    """
    result = cg.get_author_and_date_from_git_log(string)
    assert result == ("", "")


def test_get_insertion_or_deletion_from_git_log():
    string = """
 pythonProject/advent_of_code_2.py | 25 +++++++++++++++++++++++++
  1 file changed, 9 insertions(+), 4 deletions(-)"""
    insertions = cg.get_insertion_or_deletion_from_git_log(string, 'insertion')
    deletions = cg.get_insertion_or_deletion_from_git_log(string, 'deletion')
    expected_insertions = 9
    expected_deletions = 4
    assert insertions == expected_insertions
    assert deletions == expected_deletions


def test_get_insertion_or_deletion_from_git_log_no_deletions():
    string = """
 pythonProject/advent_of_code_2.py | 25 +++++++++++++++++++++++++
 1 file changed, 25 insertions(+)"""
    insertions = cg.get_insertion_or_deletion_from_git_log(string, 'insertion')
    deletions = cg.get_insertion_or_deletion_from_git_log(string, 'deletion')
    expected_insertions = 25
    expected_deletions = 0
    assert insertions == expected_insertions
    assert deletions == expected_deletions


def test_get_insertion_or_deletion_from_git_log_ones():
    string = """
 pythonProject/advent_of_code_2.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
"""
    insertions = cg.get_insertion_or_deletion_from_git_log(string, 'insertion')
    deletions = cg.get_insertion_or_deletion_from_git_log(string, 'deletion')
    expected_insertions = 1
    expected_deletions = 1
    assert insertions == expected_insertions
    assert deletions == expected_deletions


def test_get_insertion_or_deletion_from_git_log_no_changes():
    string = """
    commit e78c1fe49557fb8c713790f750b710c740bfb626
Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>
Date:   2024-02-19 15:03:24 +0200

    Commiting not completely done advent of code part 2
"""
    insertions = cg.get_insertion_or_deletion_from_git_log(string, 'insertion')
    deletions = cg.get_insertion_or_deletion_from_git_log(string, 'deletion')
    expected_insertions = 0
    expected_deletions = 0
    assert insertions == expected_insertions
    assert deletions == expected_deletions


def test_get_changed_and_renamed_files_from_git_log():
    string = """
    commit e78c1fe49557fb8c713790f750b710c740bfb626
Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>
Date:   2021-08-30 13:13:04 +0300

    Merge remote-tracking branch 'origin/develop' into implement_new_tc_24466
    
    # Conflicts:
    #       framework/lib/device/monitor.py

 azure-pipelines.yml                                                                                                                        |    7 +-
 {services/test_cases/core/web => framework/lib/report_engine/validation}/__init__.py                                                       |     0
 framework/unittests/integration/polarion/test_db_20211019_121040_positive.sqlite                                                           |   Bin 0 -> 90112 bytes
 968 files changed, 163570 insertions(+), 86903 deletions(-)
"""
    first_changed_file_line, modified_files, renamed_files = cg.get_changed_and_renamed_files_from_git_log(string)
    print(first_changed_file_line)
    assert first_changed_file_line == "azure-pipelines.yml                                                                                                                        |    7 +-"
    assert modified_files == ["azure-pipelines.yml", "framework/unittests/integration/polarion/test_db_20211019_121040_positive.sqlite"]
    assert renamed_files == {"new_file_name": "framework/lib/report_engine/validation/__init__.py",
                             "old_file_name": "services/test_cases/core/web/__init__.py"}

def test_get_changed_and_renamed_files_from_git_log_no_renamed():
    string = """
 azure-pipelines.yml                                                                                                                        |    7 +-
 framework/unittests/integration/polarion/test_db_20211019_121040_positive.sqlite                                                           |   Bin 0 -> 90112 bytes
 968 files changed, 163570 insertions(+), 86903 deletions(-)
"""
    first_changed_file_line, modified_files, renamed_files = cg.get_changed_and_renamed_files_from_git_log(string)
    assert first_changed_file_line == "azure-pipelines.yml                                                                                                                        |    7 +-"
    assert modified_files == ["azure-pipelines.yml", "framework/unittests/integration/polarion/test_db_20211019_121040_positive.sqlite"]
    assert renamed_files == {}


def test_get_changed_and_renamed_files_from_git_log_no_files():
    string = """
    Date:   Fri Nov 25 13:12:29 2022 +0200

        Merge remote-tracking branch 'origin/develop' into update_testscript_38280

        # Conflicts:
        #       test_cases/EBM/HeparinPump/test_T1_test_heparin_pump.py
"""
    first_changed_file_line, modified_files, renamed_files = cg.get_changed_and_renamed_files_from_git_log(string)
    assert first_changed_file_line == ""
    assert modified_files == []
    assert renamed_files == {}


def test_get_changed_and_renamed_files_from_git_log_variety():
    string = """
 services/{test_cases => project_service_tmt}/requirements.txt                                                                      |     0
 services/{test_cases => project_service_tmt}/run.py                                                                                |     34 +-
 services/{test_cases => project_service_tmt}/unittests/test_case_fields.py                                                         |    13 +-
"""
    first_changed_file_line, modified_files, renamed_files = cg.get_changed_and_renamed_files_from_git_log(string)
    assert first_changed_file_line == "services/{test_cases => project_service_tmt}/requirements.txt                                                                      |     0"
    assert modified_files == ["services/project_service_tmt/run.py",
                              "services/project_service_tmt/unittests/test_case_fields.py"]
    assert renamed_files == {"new_file_name": "services/project_service_tmt/requirements.txt",
                             "old_file_name": "services/test_cases/requirements.txt"}


def test_get_changed_and_renamed_files_from_git_log_variety_renamed_files():
    string = """
 {services/test_cases/command.py => project_service_tmt/run.py}                                                         |     0
 {services/test_cases/core/web => framework/unittests/conductivity_calculation}/__init__.py                             |     0
 test_cases/EBM/BloodPump/{test_E0401_bp_door_sensor_state_monitoring.py => test_bp_door_sensor_state_monitoring.py}    |     0
 services/{test_cases => project_service_tmt}/run.py                                                                    |     0
"""
    first_changed_file_line, modified_files, renamed_files = cg.get_changed_and_renamed_files_from_git_log(string)
    assert first_changed_file_line == "{services/test_cases/command.py => project_service_tmt/run.py}                                                         |     0"
    assert modified_files == []
    assert renamed_files == {"new_file_name": "services/project_service_tmt/requirements.txt",
                             "old_file_name": "services/test_cases/requirements.txt",
                             "new_file_name": "framework/unittests/conductivity_calculation/__init__.py",
                             "old_file_name": "services/test_cases/core/web/__init__.py",
                             "new_file_name": "test_cases/EBM/BloodPump/test_bp_door_sensor_state_monitoring.py",
                             "old_file_name": "test_cases/EBM/BloodPump/test_E0401_bp_door_sensor_state_monitoring.py",
                             "new_file_name": "services/project_service_tmt/run.py",
                             "old_file_name": "services/test_cases/run.py"
                             }


def test_get_message_from_git_log():
    string = """
    commit 0b44f202c497c7efb8599567c92b052ee573afc3
Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>
Date:   2024-03-26 23:21:18 +0200

        # Conflicts:
        #       test_cases/EBM/HeparinPump/test_T1_test_heparin_pump.py

 services/{test_cases => project_service_tmt}/requirements.txt                                          |     0
"""
    _, date = cg.get_author_and_date_from_git_log(string)
    first_file, _, _ = cg.get_changed_and_renamed_files_from_git_log(string)
    message = cg.get_message_from_git_log(string, date, first_file)
    expected_result = """# Conflicts:
        #       test_cases/EBM/HeparinPump/test_T1_test_heparin_pump.py"""
    assert message == expected_result


def test_get_message_from_git_log_no_file():
    string = """
    commit 0b44f202c497c7efb8599567c92b052ee573afc3
Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>
Date:   2024-03-26 23:21:18 +0200

        # Conflicts:
        #       test_cases/EBM/HeparinPump/test_T1_test_heparin_pump.py

"""
    _, date = cg.get_author_and_date_from_git_log(string)
    first_file, _, _ = cg.get_changed_and_renamed_files_from_git_log(string)
    message = cg.get_message_from_git_log(string, date, first_file)
    expected_result = """# Conflicts:
        #       test_cases/EBM/HeparinPump/test_T1_test_heparin_pump.py"""
    assert message == expected_result


def test_get_message_from_git_log_no_date():
    string = """
    commit 0b44f202c497c7efb8599567c92b052ee573afc3
    Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>

        # Conflicts:
        #       test_cases/EBM/HeparinPump/test_T1_test_heparin_pump.py
        
 services/{test_cases => project_service_tmt}/requirements.txt                                        |     0
"""
    _, date = cg.get_author_and_date_from_git_log(string)
    first_file, _, _ = cg.get_changed_and_renamed_files_from_git_log(string)
    message = cg.get_message_from_git_log(string, date, first_file)
    expected_result = ""
    assert message == expected_result


def test_get_message_from_git_log_no_message():
    string = """
    commit 0b44f202c497c7efb8599567c92b052ee573afc3
    Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>
    Date:   2024-03-26 23:21:18 +0200
"""
    _, date = cg.get_author_and_date_from_git_log(string)
    first_file, _, _ = cg.get_changed_and_renamed_files_from_git_log(string)
    message = cg.get_message_from_git_log(string, date, first_file)
    expected_result = ""
    assert message == expected_result


if __name__ == "__main__":
    logger = cg.configure_logger("tester_log.log")
