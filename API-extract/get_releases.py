#! /usr/bin/python3

from requests import get


def generate_api_url(project_name):
    return "https://pypi.org/pypi/%s/json" % project_name

def get_releases(project):
    api_url = generate_api_url(project)
    response = get(api_url)
    wheel_info = response.json() if response.status_code == 200 else None
    return wheel_info["releases"] if wheel_info else None


def main():
    project = "tensorflow"
    releases = get_releases(project)
    print("Version,Upload time")
    for version in releases:
        print("%s,%s" % (version, releases[version][0]["upload_time"]))

if __name__ == "__main__":
    main()
