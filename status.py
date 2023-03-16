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

    def icon(self):
        return "😐"

    def display_information(self):
        return f"GIT structure not supported yet. No branch named `develop` found."


class ReleaseCouldBeInteresting(Status):

    def __init__(self, commitCount):
        self.commitCount = commitCount

    def icon(self):
        return "👀"

    def display_information(self):
        return f"It might be worth releasing this app. There are {self.commitCount} new commits on develop compared to the master branch."


class ReleaseProbablyNotInteresting(Status):

    def __init__(self, commitCount):
        self.commitCount = commitCount

    def icon(self):
        return "➖"

    def display_information(self):
        return f"Release is probably not interesting. There are {self.commitCount} commits on dev"


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
