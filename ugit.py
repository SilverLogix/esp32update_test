import os
import urequests  # noqa
import json
import hashlib
import binascii
import machine
import time
import network
# test

# User Variables
ssid = "OpenMuscle"
password = "3141592653"
github_user = 'turfptax'
repository = 'ugit_test'
token = ''
default_branch = 'main'
ignore_files = ['/ugit.py']

github_url = f'https://github.com/{github_user}/{repository}'
trees_url = f'https://api.github.com/repos/{github_user}/{repository}/git/trees/{default_branch}?recursive=1'
raw_url = f'https://raw.githubusercontent.com/{github_user}/{repository}/master/'

BATCH_SIZE = 5  # Number of files to process in a single batch


def pull_file(file_path, raw_url):
    print(f'Pulling {file_path} from GitHub')
    headers = {'User-Agent': 'ugit-turfptax'}
    if token:
        headers['authorization'] = "bearer %s" % token
    response = urequests.get(raw_url, headers=headers)
    try:
        content = response.content.decode('utf-8')
        return content
    except:
        print('Decode failed. Try adding non-code files to .gitignore')


def pull_all(ignore=ignore_files):
    wlan = connect_wifi()
    os.chdir('/')
    tree = get_git_tree()
    internal_tree = build_internal_tree()
    internal_tree = remove_ignored(internal_tree, ignore)
    print('Ignore removed:')
    print(internal_tree)
    log = []

    batch_count = len(tree['tree']) // BATCH_SIZE
    for i in range(batch_count + 1):
        batch_files = tree['tree'][i * BATCH_SIZE:(i + 1) * BATCH_SIZE]
        process_batch(batch_files, ignore, internal_tree, log)

    for file_path in internal_tree:
        os.remove(file_path)
        log.append(f'{file_path} removed from internal memory')

    logfile = open('ugit_log.py', 'w')
    logfile.write(str(log))
    logfile.close()
    time.sleep(10)
    print('Resetting machine in 10 seconds: machine.reset()')
    machine.reset()


def connect_wifi(ssid=ssid, password=password):
    print('Use: ugit.connect_wifi(SSID, Password)')
    print('Otherwise, use SSID and password from the top of ugit.py code')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
    print('WiFi Connected!!')
    print(f'SSID: {ssid}')
    print('Local IP Address, Subnet Mask, Default Gateway, Listening on...')
    print(wlan.ifconfig())
    return wlan


def build_internal_tree():
    internal_tree = []
    os.chdir('/')
    for dir_path, dir_names, file_names in os.walk('.'):
        for file_name in file_names:
            file_path = os.path.join(dir_path, file_name)
            file_hash = get_file_hash(file_path)
            content = os.read_file(file_path)
            internal_tree.append([file_path, file_hash, content])
    return internal_tree


def get_file_hash(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()
    sha1obj = hashlib.sha1(data)
    file_hash = sha1obj.digest()
    return binascii.hexlify(file_hash)


def get_git_tree(tree_url=trees_url):
    headers = {'User-Agent': 'ugit-turfptax'}
    if token:
        headers['authorization'] = "bearer %s" % token
    response = urequests.get(tree_url, headers=headers)
    data = json.loads(response.content.decode('utf-8'))
    if 'tree' not in data:
        print(f'\nDefault branch "{default_branch}" not found. Set "default_branch" variable to your default branch.\n')
        raise Exception(f'Default branch {default_branch} not found.')
    return data


def process_batch(batch_files, ignore, internal_tree, log):
    for item in batch_files:
        if item['type'] == 'tree':
            try:
                os.mkdir(item['path'])
            except:
                print(f'Failed to create directory {item["path"]}. It may already exist.')
        elif item['path'] not in ignore:
            try:
                os.remove(item['path'])
                log.append(f'{item["path"]} file removed from internal memory')
                internal_tree = remove_item(item['path'], internal_tree)
            except:
                log.append(f'{item["path"]} deletion failed from internal memory')
                print('Failed to delete old file')
            try:
                content = pull_file(item['path'], raw_url + item['path'])
                with open(item['path'], 'w') as file:
                    file.write(content)
                log.append(f'{item["path"]} updated')
            except:
                log.append(f'{item["path"]} failed to pull')


def remove_ignored(internal_tree, ignore):
    return [file_path for file_path in internal_tree if file_path[0] not in ignore]


def remove_item(item, tree):
    return [file_path for file_path in tree if item not in file_path]


def update():
    print('Updating ugit.py to the newest version')
    content = pull_file('ugit.py', raw_url + 'ugit.py')
    with open('ugit.py', 'w') as file:
        file.write(content)


def backup():
    internal_tree = build_internal_tree()
    backup_text = "ugit Backup Version 1.0\n\n"
    for file_path, file_hash, content in internal_tree:
        backup_text += f'FN:SHA1{file_path},{file_hash}\n'
        backup_text += '---' + content + '---\n'
    with open('ugit.backup', 'w') as backup:
        backup.write(backup_text)
