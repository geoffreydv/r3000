import yaml
import os
import subprocess

from status import GitStructureUnknown, LingeringReleaseBranch, NoGitRepositoryStatus, ReleaseCouldBeInteresting, ReleaseProbablyNotInteresting, TempAllGoodStatus

config_path = os.path.expanduser('~/.r3000/config.yaml')

with open(config_path, 'r') as f:
    config = yaml.safe_load(f)


def find_git_branches_starting_with_name(repository_location, starts_with):
    output = subprocess.check_output(
        ['git', 'branch'], cwd=repository_location)
    branches = [branch.strip('*').strip() for branch in output.decode().split('\n') if branch.strip()]
    return [branch for branch in branches if branch.startswith(starts_with)]

def get_project_status(project_location):

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

    return TempAllGoodStatus()


for project in config['projects']:

    name = project.get('name')
    location = project.get('location')

    status = get_project_status(location)

    print(f"{status.icon()} {name} - {status.display_information()}")

    next_actions = status.possible_next_actions()
    if next_actions:
        for action in next_actions:
            print(f"\t- Hint: {action}")
