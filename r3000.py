import argparse
import yaml
import os
import subprocess

from status import GitStructureUnknown, LingeringReleaseBranch, NoGitRepositoryStatus, ReleaseCouldBeInteresting, ReleaseProbablyNotInteresting, ReleaseBranchReady


def get_project_status(project):

    project_location = project.get('location')

    if not os.path.exists(os.path.join(project_location, '.git')):
        return NoGitRepositoryStatus(project_location)

    if not find_git_branches_starting_with_name(project_location, 'develop'):
        return GitStructureUnknown()

    release_branches = find_git_branches_starting_with_name(
        project_location, 'release/')

    if not release_branches:
        output = subprocess.check_output(
            ['git', 'rev-list', '--count', 'master..develop'], cwd=project_location)
        commit_count = int(output.decode().strip())
        if commit_count > 2:
            return ReleaseCouldBeInteresting(commit_count)
        else:
            return ReleaseProbablyNotInteresting(commit_count)

    latest_release_branch = release_branches[-1].strip()
    output = subprocess.check_output(
        ['git', 'rev-list', '--count', f'master..{latest_release_branch}'], cwd=project_location)
    commit_count = int(output.decode().strip())

    if commit_count == 0:
        return LingeringReleaseBranch(project_location, latest_release_branch)

    return ReleaseBranchReady(project.get("technical-name"), latest_release_branch)


def find_git_branches_starting_with_name(repository_location, starts_with):
    output = subprocess.check_output(
        ['git', 'branch'], cwd=repository_location)
    branches = [branch.strip('*').strip()
                for branch in output.decode().split('\n') if branch.strip()]
    return [branch for branch in branches if branch.startswith(starts_with)]


def sync_git(location, quiet):
    command_parts = ['git', 'fetch']

    if quiet:
        command_parts.append('--quiet')

    subprocess.call(command_parts, cwd=location)


def prepare_workspace(project):
    location = project.get('location')
    print(f'Syncing git status of {location}')
    sync_git(location, False)


def list_status(project):
    name = project.get('name')

    status = get_project_status(project)

    print(f"{status.icon()} {name} - {status.display_information()}")

    next_actions = status.possible_next_actions()
    if next_actions:
        for action in next_actions:
            print(f"  - {action}")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='CLI tools to automate the boring stuff of releases')
    parser.add_argument('--config', type=str, default='~/.r3000/config.yaml', help='path to config file')

    subparsers = parser.add_subparsers(dest='action', required=True)
    list_parser = subparsers.add_parser('list', help='Lists the status of all projects')
    update_parser = subparsers.add_parser('update', help='Brings your branches up to date with the remote')

    args = parser.parse_args()

    config_path = os.path.expanduser(args.config)

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    if args.action == 'update':
        for project in config['projects']:
            prepare_workspace(project)

    if args.action == 'list':
        for project in config['projects']:
            list_status(project)
