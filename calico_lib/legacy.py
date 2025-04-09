import os
import sys
import zipfile
import argparse

# Functions from the old calico lib.
def get_path(is_secret, file_name='', ext=None):
    """
    If file_name is unspecified, makes a path to the root of the sample or
    secret directory depending on is_secret.

    Otherwise, get the path for a file in the sample or secret directory. The
    path is absolute based on the location of this file, not relative to the
    execution path.
    """
    relative_path = ''.join([
        'data/',
        'secret/' if is_secret else 'sample/',
        ('secret_' if is_secret else 'sample_') if file_name else '',
        file_name,
        f'.{ext}' if ext else ''
    ])
    return os.path.join(os.path.dirname(__file__), relative_path)

def delete_old_zips(problem_name, test_set_names):
    """
    Delete old zips if they exist so we can start making with a clean slate.
    """
    print('Deleting old zips', end='...')
    deleted = False
    for test_set_name in test_set_names:
        zip_file_name = get_zip_file_path(problem_name, test_set_name)
        if os.path.exists(zip_file_name):
            os.remove(zip_file_name)
            deleted = True
    print('Done!' if deleted else 'Nothing to delete!')


def make_actual_zips(problem_name, time_limit, test_set_names, \
                     is_data_in_test_set, is_submission_in_test_set):
    """
    Create a zip for each test set. Each test set consists of data, submissions,
    and the DOMjudge metadata file.
    """
    for test_set_name in test_set_names:
        print(f'Creating zip for test set "{test_set_name}"...')

        file_path = get_zip_file_path(problem_name, test_set_name)
        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_path(zip_file, 'data', test_set_name, is_data_in_test_set)
            zip_path(zip_file, 'submissions', test_set_name, is_submission_in_test_set)
            zip_metadata(zip_file, problem_name, test_set_name, time_limit)

        print(f'Done creating zip for test set "{test_set_name}"!')


def get_zip_file_path(problem_name, test_set_name):
    """
    Get the path for a zip file given the name of the test set and the DOMjudge
    metadata name.
    """
    return f'{problem_name}_{test_set_name}.zip'


def zip_path(zip_file, path, test_set_name, is_file_in_test_set):
    """
    Add all files in path. Only files that is_file_in_test_set says
    are to be added to the current test_set_name will be added.
    """
    print(f'Zipping directory "{path}" for test set "{test_set_name}"', end='...')

    # path = os.path.join(os.path.dirname(__file__), relative_path)
    for root, dirs, files in os.walk(path):
        for file in files:
            if is_file_in_test_set(file, test_set_name):
                file_path = os.path.join(root, file)
                zip_path = os.path.relpath(os.path.join(root, file), os.path.join(path, '..'))
                zip_file.write(file_path, zip_path)

    print(f'Done!')


def zip_metadata(zip_file, problem_name, test_set_name, time_limit):
    """
    Add the DOMjudge metadata file to the zip_file with the test_set_name. This
    function creates a temporary file, writes name and timelimit, adds it to
    the zip, then deletes the temporary file.
    """
    print(f'Zipping domjudge-problem.ini for test set "{test_set_name}"', end='...')

    meta_path = os.path.join(os.path.dirname(__file__), 'domjudge-problem.ini')
    with open(meta_path, 'w') as meta_file:
        problem_name = 'draft_' + problem_name
        print(f'name={problem_name}_{test_set_name}', file=meta_file)
        print(f'timelimit={time_limit}', file=meta_file)

    zip_file.write(meta_path, 'domjudge-problem.ini')
    os.remove(meta_path)

    print('Done!')
