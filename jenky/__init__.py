import sys
import os
import re
import github3
import git
import jenkins
import json
import pprint
import slack

GH_USER = os.environ.get('GH_USER', 'andyshinn')
GH_TOKEN = os.environ.get('GH_TOKEN')
GH_REPOSITORY = os.environ.get('GH_REPOSITORY', 'monolith')
GH_ORG = os.environ.get('GH_ORG','myorg')
JENKINS_JOB = os.environ.get('PROMOTED_JOB_NAME', 'build/monolith')
JENKINS_URL = os.environ.get('JENKINS_URL', 'http://localhost:8081')
PROMOTION_NAME = 'production'
PROMOTED_GIT_COMMIT = os.environ.get('PROMOTED_GIT_COMMIT')
PROMOTED_NUMBER = os.environ.get('PROMOTED_NUMBER')

class Jenkins(object):
    DEPTH = 2

    def __init__(self, url, user, password):
        super(Jenkins, self).__init__()
        try:
            self.connection = jenkins.Jenkins(url, user, password)
        except Exception as e:
            raise

    def promotions(self, job, depth=DEPTH):
        return self.connection.get_promotions_info(job, depth)

    def promotion(self, job, name, depth=DEPTH):
        return Promotion(self, job, name, depth)

    def build_sha1(self, job, build, depth=DEPTH):
        actions = self.connection.get_build_info(job, build, depth)['actions']
        for action in actions:
            if '_class' in action and action['_class'] == 'hudson.plugins.git.util.BuildData':
                return action['lastBuiltRevision']['SHA1']

    def fname(arg):
        pass

class Promotion(object):
    def __init__(self, connection, job, name, depth):
        self.connection = connection

        promotions = self.connection.promotions(job, depth)

        for promotion in promotions['processes']:
            if promotion['name'] == name:
                for k,v in promotion.items():
                    setattr(self, k, v)

    def previous_build(self):
        for build in self.builds:
            if build['target']['number'] < self.lastBuild['target']['number']:
                return build

class Message(object):
    """docstring for Message."""
    def __init__(self, arg):
        super(Message, self).__init__()
        self.arg = arg

    def message(pull_requests, deployer, repo=GH_REPOSITORY, user=GH_ORG, build_number=PROMOTED_NUMBER, head=PROMOTED_GIT_COMMIT, base='none'):
        for pr in pull_requests:
            field = dict({"text": "• <{0}|#{1}: {2}>".format(pr.html_url, pr.number, pr.title)})
            fields.append(field)

        message = dict({"author_name": deployer, "title": "test"})

        message_text = '''
        {0} has started a <https://github.com/{1}|{2}> <https://jenkins.myorg.com/job/build/job/{2}/{3}/promotion/|promotion for Jenkins build {3}>. There are <https://github.com/myorg/monolith/compare/{4}...{5}|15 commits> over 6 closed pull requests:\n\n{6}
        '''.format(deployer, user, repo, build_number, base, head, "\n".join(pull_requests_lines))

        message = {"unfurl_media":False, "text": message_text.strip()}

        print(json.dumps(message, ensure_ascii=False))



def main():
    pp = pprint.PrettyPrinter(indent=4)
    jenkins = Jenkins(JENKINS_URL, GH_USER, GH_TOKEN)
    promotion = jenkins.promotion(JENKINS_JOB, PROMOTION_NAME, 2)
    previous_build = promotion.previous_build()
    current_sha1 = jenkins.build_sha1(JENKINS_JOB, 262)
    last_sha1 = jenkins.build_sha1(JENKINS_JOB, previous_build['target']['number'])

    pp.pprint(current_sha1)
    pp.pprint(last_sha1)
