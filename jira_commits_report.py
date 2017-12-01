#!/usr/bin/env python3
"""Generate a report with issue information between two Git repo commits."""

from __future__ import print_function

import argparse
import re
import requests
import sys
from subprocess import Popen, PIPE
from requests.auth import HTTPBasicAuth


__version__ = "1.0"

API_HEADERS = {'Accept': 'application/json'}


def get_issue_regex(project):
    """Get project issue regex."""
    return '^.*(?P<issue_key>({project})-[0-9]+).*$'.format(project=project)


def get_issue_url(jira_url, issue_key):
    """Get issue key URL."""
    return '{url}/browse/{issue}'.format(url=jira_url,
                                         issue=issue_key)


def get_api_url(jira_url):
    """Get Jira API url."""
    return '{url}/rest/api/2'.format(url=jira_url)


def get_issue_data(issue_key, url, user=None, password=None):
    """Get data from an issue."""
    session = requests.Session()

    if user is not None:
        if password is None:
            password = ''
        session.auth = HTTPBasicAuth(user, password)

    rest_url = '{api_url}/issue/{key}'.format(api_url=get_api_url(url),
                                              key=issue_key)
    response = session.get(rest_url, headers=API_HEADERS)
    response.raise_for_status()

    return response.json()


def get_commits_issues(project, commit_list):
    """Get all unrepeated issues from a commit list."""
    issues = set()

    for commit in commit_list:
        issue_match = re.match(get_issue_regex(project),
                               commit['comment'])
        if issue_match:
            issues.add(issue_match.group('issue_key'))

    return list(issues)


def write(text, file=None):
    """Write text to specified output."""
    if file is None:
        print(text)
    else:
        with open(file, 'a') as f:
            print(text, file=f)


def __call_git_log(args, repo_path):
    args.extend(['--pretty=oneline'])
    command_args = ['git', 'log']
    command_args.extend(args)
    p = Popen(command_args, stdout=PIPE, stderr=PIPE, cwd=repo_path)
    raw_out, raw_err = p.communicate()
    out = raw_out.decode()
    if p.returncode:
        raise RuntimeError(
            ('Cmd(\'git\') failed due to: exit code({code})\n'
             '  cmdline: {cmd}\n  stderr: {out}').format(
                code=p.returncode,
                cmd=' '.join(command_args),
                out=raw_err.decode()[:-1]))

    log_lines = out.splitlines()
    log_line_regex = '^(?P<commit>[^ ]+) (?P<comment>.*)$'
    commits = [re.match(log_line_regex, line).groupdict()
               for line in log_lines]

    return commits


def get_commits_between_dates(from_date=None, to_date=None, repo_path='.'):
    """Get all repo commits between two dates."""
    args = []
    if from_date is not None:
        args.append('--since=\'{from_date}\''.format(from_date=from_date))
    if to_date is not None:
        args.append('--until=\'{to_date}\''.format(to_date=to_date))

    commits = __call_git_log(args, repo_path)

    return commits


def get_commits_between_refs(from_ref=None, to_ref=None, repo_path='.'):
    """Get all repo commits between two refs."""
    if to_ref is None:
        to_ref = 'HEAD'

    args = []
    diff_args = []
    if from_ref is not None:
        diff_args.append(from_ref)
        diff_args.append('..')
    diff_args.append(to_ref)
    args.append(''.join(diff_args))

    commits = __call_git_log(args, repo_path)

    return commits


def sanitize(text):
    """Sanitize a text to insert into a CSV."""
    return text.replace('"', '""')


def main():
    """Execute module function."""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Get issues from git repository commit history')

    parser.add_argument('-s', '--jira-server', type=str, required=True,
                        help='Jira server URL')
    parser.add_argument('-P', '--project', type=str, required=True,
                        help='Jira project id')
    parser.add_argument('-u', '--jira-user', type=str, required=True,
                        help='Jira user')
    parser.add_argument('-p', '--jira-password', type=str,
                        required=True, help='Jira password')
    parser.add_argument('-r', '--repo-path', type=str, default='.',
                        help='Repository path')
    parser.add_argument('-f', '--file', type=str,
                        default=None, help='Output file')
    parser.add_argument('-t', '--type', type=str, choices=['date', 'ref'],
                        default='ref', help='Search type, default \'ref\'')
    parser.add_argument('--from', dest='from_value', type=str,
                        help='From value')
    parser.add_argument('--to', dest='to_value', type=str, help='To value')
    args = parser.parse_args()

    # Get commits and write results
    try:
        if args.type == 'date':
            commits = get_commits_between_dates(args.from_value, args.to_value,
                                                repo_path=args.repo_path)
        else:
            commits = get_commits_between_refs(args.from_value, args.to_value,
                                               repo_path=args.repo_path)
    except Exception as e:
        print(e, file=sys.stderr)
        return 1

    issues = get_commits_issues(args.project, commits)

    for issue_key in issues:
        issue_data = get_issue_data(issue_key,
                                    url=args.jira_server,
                                    user=args.jira_user,
                                    password=args.jira_password)

        if 'errorMessages' in issue_data:
            error_message = issue_data['errorMessages'][0].rstrip('.')

            write('"{key}","{error_text}","Error"'.format(
                key=sanitize(issue_key),
                error_text=sanitize(error_message)),
                file=args.file)
        else:
            write('"{key}","{issue_type}","{summary}","{status}","{url}"'.
                  format(
                      key=sanitize(issue_data['key']),
                      issue_type=sanitize(
                          issue_data['fields']['issuetype']['name']),
                      summary=sanitize(issue_data['fields']['summary']),
                      status=sanitize(issue_data['fields']['status']['name']),
                      url=get_issue_url(args.jira_server, issue_data['key'])),
                  file=args.file)

    return 0


if __name__ == "__main__":
    sys.exit(main())
