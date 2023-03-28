class Status:

    def icon(self):
        return ""

    def display_information(self):
        pass

    def possible_next_actions(self):
        return []


class ReleaseBranchReady(Status):

    def __init__(self, shortName, releaseBranchName):
        self.shortName = shortName
        self.releaseBranchName = releaseBranchName

    def icon(self):
        return "✅"

    def display_information(self):
        return f"Release branch present: {self.releaseBranchName}"

    def possible_next_actions(self):
        return [
            f"List tickets in release with: python r3000.py list-tickets {self.shortName}"
        ]


class NoGitRepositoryStatus(Status):

    def __init__(self, location):
        self.location = location

    def icon(self):
        return "❌"

    def display_information(self):
        return f"No .git repository found at location {self.location}"


class GitStructureUnknown(Status):

    def __init__(self, missing_branch, project_location):
        self.missing_branch = missing_branch
        self.project_location = project_location

    def icon(self):
        return "😐"

    def display_information(self):
        return f"We only support gitflow right now but no branch named `{self.missing_branch}` found."
    
    def possible_next_actions(self):
        return [
            f"If you think the branch exists, run python r3000.py update-workspace"
        ]


class ReleaseCouldBeInteresting(Status):

    def __init__(self, tickets):
        self.tickets = tickets

    def icon(self):
        return "👀"

    def display_information(self):
        return f"It might be worth releasing this app. {len(self.tickets)} tickets mentioned in dev commits"
    
    def possible_next_actions(self):
        return [
            f"Referenced tickets: {','.join(self.tickets)}"
        ]


class ReleaseProbablyNotInteresting(Status):

    def icon(self):
        return "➖"

    def display_information(self):
        return f"Release is probably not interesting. There are no commits with referenced ticket numbers on dev"


class NoReleaseBranchStatus(Status):

    def icon(self):
        return "❌"

    def display_information(self):
        return "No Release branch"


class LingeringReleaseBranch(Status):

    def __init__(self, project_location, branch_name):
        self.branch_name = branch_name
        self.project_location = project_location

    def icon(self):
        return "❌"

    def display_information(self):
        return f"You still have an old release branch `{self.branch_name}`. Please delete it (local and on the remote)"

    def possible_next_actions(self):
        return [f"Delete branch with: git -C {self.project_location} branch -D {self.branch_name} && git -C {self.project_location} push origin --delete {self.branch_name}"]
