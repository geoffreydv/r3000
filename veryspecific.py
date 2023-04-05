from abc import ABC, abstractmethod
import requests


class ProjectInfo(ABC):

    @abstractmethod
    def get_deployed_commit(self, project, config, environment):
        pass


class RsProjectInfo(ProjectInfo):
    def get_deployed_commit(self, project, config, environment):
        if project.custom_properties:
            workspace = project.custom_properties.get('bitbucket-workspace')
            slug = project.custom_properties.get('bitbucket-repository-slug')
            url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{slug}/environments"
            r = requests.get(url, auth=(
                config.get('bitbucket').get('api-user'),
                config.get('bitbucket').get('api-password')
            ))

            # print(url)
            # print(r.text)
