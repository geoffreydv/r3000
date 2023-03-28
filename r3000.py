import argparse
import yaml
import os
import subprocess
import re
import urllib.parse

from status import GitStructureUnknown, LingeringReleaseBranch, NoGitRepositoryStatus, ReleaseCouldBeInteresting, ReleaseProbablyNotInteresting, ReleaseBranchReady


def get_project_status(project):

    project_location = project.get('location')

    if not os.path.exists(os.path.join(project_location, '.git')):
        return NoGitRepositoryStatus(project_location)

    if not find_git_branches_starting_with_name(project_location, 'develop'):
        return GitStructureUnknown('develop', project_location)
    
    if not find_git_branches_starting_with_name(project_location, 'master'):
        return GitStructureUnknown('master', project_location)

    release_branches = find_git_branches_starting_with_name(project_location, 'release/')

    if not release_branches:
        tickets_between = list_tickets_between(project_location, 'master', 'develop')
        referenced_ticket_count = len(tickets_between)
        
        if referenced_ticket_count > 0:
            return ReleaseCouldBeInteresting(tickets_between)
        else:
            return ReleaseProbablyNotInteresting()

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


def sync_git(repo_path):

    # Define the branches that we want to check
    branch_patterns = ["master", "develop", "release/", "hotfix/"]

    # Get the list of remote branches
    git_ls_remote_cmd = ['git', '-C', repo_path, 'ls-remote', '--heads', 'origin']
    git_ls_remote_output = subprocess.check_output(git_ls_remote_cmd).decode().strip()
    remote_branches = [line.split('\t')[1].split('refs/heads/')[1] for line in git_ls_remote_output.split('\n')]

    # Check out or pull each matching branch
    for branch_pattern in branch_patterns:
        for branch in remote_branches:
            if branch.startswith(branch_pattern):
                try:
                    subprocess.check_output(['git', '-C', repo_path, 'show-ref', '--verify', '--quiet', f"refs/heads/{branch}"])
                    # Branch exists locally, so do a pull
                    subprocess.check_output(['git', '-C', repo_path, 'checkout', branch, '--quiet'])
                    subprocess.check_output(['git', '-C', repo_path, 'pull', 'origin', branch, '--quiet'])
                    print(f'Pulled changes from origin/{branch} into {branch}.')
                except subprocess.CalledProcessError:
                    # Branch doesn't exist locally, so do a checkout
                    subprocess.check_output(['git', '-C', repo_path, 'checkout', '-b', branch, f'origin/{branch}', '--quiet'])
                    print(f'Branch {branch} was not in your local repo yet. Now it is.')


def prepare_workspace(project):
    location = project.get('location')
    print(f'Syncing git status of {location}')
    sync_git(location)


def list_status(project):
    name = project.get('name')

    status = get_project_status(project)

    print(f"{status.icon()} {name} - {status.display_information()}")

    next_actions = status.possible_next_actions()
    if next_actions:
        for action in next_actions:
            print(f"  - {action}")

def list_tickets_between(project_location, reference_branch, branch_to_check):

    log_output = subprocess.check_output(['git', '--no-pager', 'log', '--cherry', '--pretty=oneline', f'{reference_branch}..{branch_to_check}'], cwd=project_location).strip().decode()

    # Extract the ticket numbers from the commit messages
    ticket_numbers = re.findall(r'REN-\d{2,6}', log_output)

    # Return a list of unique ticket numbers
    return list(set(ticket_numbers))

def find_project_with_name(projects, target_name):
    for project in projects:
        if project.get("technical-name") == target_name:
            return project

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='CLI tools to automate the boring stuff of releases')
    parser.add_argument('--config', type=str, default='~/.r3000/config.yaml', help='path to config file')

    subparsers = parser.add_subparsers(dest='action', required=True)

    list_parser = subparsers.add_parser('list', help='Lists the status of all projects')
    update_parser = subparsers.add_parser('prepare-workspace', help='Brings your branches up to date with the remote')
    list_tickets_parser = subparsers.add_parser('list-tickets', help='List JIRA tickets between master and the release branch')    
    list_tickets_parser.add_argument('project_name', type=str, help='The technical name of a project in your config file')

    args = parser.parse_args()

    config_path = os.path.expanduser(args.config)

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    if args.action == 'prepare-workspace':
        for project in config['projects']:
            prepare_workspace(project)

    if args.action == 'list':
        for project in config['projects']:
            list_status(project)

    if args.action == 'list-tickets':
        project = find_project_with_name(config['projects'], args.project_name)
        last_rc_name = find_git_branches_starting_with_name(project.get("location"), 'release/')[0]

        tickets = ','.join(list_tickets_between(project.get("location"), "master", last_rc_name))
        jql = urllib.parse.quote(f'issueKey in ({tickets}) and issuetype not in subTaskIssueTypes()')
        print(f'https://rsautomotive.atlassian.net/issues/?jql={jql}')