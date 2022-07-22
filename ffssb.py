#!/usr/bin/env python3

import argparse
import configparser
import logging
import os
import re
import requests
import shutil
from urllib.parse import urlparse
from PIL import Image

ffssbcache_dir = os.path.expanduser('~') + '/.cache/ffssb'
os_applications_dir = os.path.expanduser('~') + '/.local/share/applications/'
os_icons_dir = os.path.expanduser('~') + '/.local/share/icons/hicolor'
ffsettings_dir = os.path.expanduser('~') + '/.mozilla/firefox/'
ffbaseprofile = 'Profile0'

def get_base_profile_path():
    config = configparser.ConfigParser()
    config.optionxform = lambda optionstr : optionstr
    config.read(ffsettings_dir + 'profiles.ini')

    for profile in config.sections():
        if profile == ffbaseprofile:
            return ffsettings_dir + config[profile]['Path']
    return ''

def get_ffssb_prefix():
    return 'ffssb.'

def add_profile_to_ini(name, profile_path):
    config_path = ffsettings_dir + 'profiles.ini'
    config_path_tmp = ffsettings_dir + 'profiles.ini.tmp'

    config = configparser.ConfigParser()
    config.optionxform = lambda optionstr : optionstr
    config.read(config_path)

    profile_max_num = 0;
    for profile in config.sections():
        if profile.startswith('Profile'):
            profile_num = int(profile.replace('Profile', ''))
            if profile_num > profile_max_num:
                profile_max_num = profile_num

    profile_max = 'Profile' + str(profile_max_num)
    # Profile already exists
    if config[profile_max]['Name'] == name and config[profile_max]['Path'] == profile_path:
        return

    profile_next = 'Profile' + str(profile_max_num + 1)
    config_new = configparser.RawConfigParser()
    config_new.optionxform = lambda optionstr : optionstr
    config_new.add_section(profile_next)
    config_new.set(profile_next, 'Name', name)
    config_new.set(profile_next, 'Path', profile_path)
    config_new.set(profile_next, 'IsRelative', '1')
    config_new.read_dict(config)

    with open(config_path_tmp, 'w') as configfile:
        config_new.write(configfile, space_around_delimiters=False)
    os.remove(config_path)
    shutil.move(config_path_tmp, config_path)

def add_desktop_entry(display_name, url, profile_name, name, icon):
    desktop_entry_template = '''[Desktop Entry]
Version=1.0
Terminal=false
Type=Application
Name={0}
Exec=firefox --new-window {1} --no-remote -P {2} --name {3} --class {3}
Icon={4}
StartupNotify=true
StartupWMClass={3}'''

    desktop_entry_content = desktop_entry_template.format(display_name, url, profile_name, name, icon);
    filePath = r'' + os_applications_dir + get_ffssb_prefix() + name + '.desktop'
    with open(filePath, 'w') as fp:
        fp.write(desktop_entry_content)

def add_desktop_entry_icon(name, url):
    if not os.path.exists(ffssbcache_dir):
        os.mkdir(ffssbcache_dir)

    icon_path = ffssbcache_dir + '/' + name + '.ico'
    if not os.path.exists(icon_path):
        domain = str(urlparse(url).hostname)
        ico_url = 'https://icons.duckduckgo.com/ip2/' + domain + '.ico'
        ico_file = requests.get(ico_url)
        open(icon_path, 'wb').write(ico_file.content)

    img = Image.open(icon_path)
    img_path = os_icons_dir + '/48x48/apps/' + name + '.png'
    img.save(img_path, format = 'PNG', sizes=[(48,48)])

    return img_path

def add_user_chrome(profile_path):
    chrome_css = '''@namespace url("http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul");
@namespace url("http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul");

#TabsToolbar .customization-target, /* tabs */
#PersonalToolbar, /* bookmarks toolbar */
#page-action-buttons
{
    visibility: collapse;
}
#nav-bar {
    margin-top: -10px;
    margin-right: 75px;
    max-height: 40px;
}
#nav-bar-customization-target {
    margin-top: 5px;
}
#urlbar-background {
    visibility: hidden;
}
#urlbar-container {
    margin-right: 70vh;
    max-width: 35vh;
}
.urlbarView {
    display: none !important;
}
#PanelUI-button,
#nav-bar-overflow-button {
    margin-top: 5px !important;
}
#TabsToolbar {
    background: #444;
}
#titlebar {
    margin-bottom: -30px;
}
'''
    chrome_dir = ffsettings_dir + profile_path + '/chrome'
    if not os.path.exists(chrome_dir):
        os.mkdir(chrome_dir)
    with open(chrome_dir + '/userChrome.css', 'w') as fp:
        fp.write(chrome_css)

def set_userchrome_true(profile_path):
    userchrome_true = 'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);'

    user_js_file = ffsettings_dir + profile_path + '/user.js'
    if os.path.exists(user_js_file):
        filedata = ""
        with open(user_js_file, 'r') as fp:
            filedata = fp.read()
        if not filedata.find(userchrome_true):
            with open(user_js_file, 'a') as fp:
                fp.writelines(userchrome_true)
    else:
        with open(user_js_file, 'w') as fp:
            fp.write(userchrome_true)

def create(args):
    baseprofile_path = get_base_profile_path()
    ffssb_name = get_ffssb_prefix() + args.name
    newprofile_path = ffsettings_dir + ffssb_name
    display_name = args.name
    icon_path = args.name

    if args.display_name != None:
        display_name = args.display_name

    if not os.path.exists(newprofile_path):
        shutil.copytree(baseprofile_path, newprofile_path, symlinks=True, dirs_exist_ok=True)

    try:
        icon_path = add_desktop_entry_icon(args.name, args.url)
    except:
        # We dont care if the icon fails
        # but don't break the program
        logging.info("Failed to add icon")

    add_desktop_entry(display_name, args.url, args.name, args.name, icon_path)
    add_profile_to_ini(args.name, ffssb_name)

    if not args.skip_user_chrome:
        add_user_chrome(ffssb_name)
        set_userchrome_true(ffssb_name)

def list(args):
    applications = os.listdir(os_applications_dir)
    ffssb_application_files = [a for a in applications if get_ffssb_prefix() in a]

    data = []
    for file in ffssb_application_files:
        with open(os_applications_dir + file, 'r') as fp:
            file_text = fp.read()
            name = re.findall(r'^ffssb\.(.+)\.desktop$' ,file)[0]
            url = re.findall(r'(https?://\S+)', file_text)[0]
            data.append([name, url])

    print ("{:<20} {:<20}".format('NAME','URL'))
    for v in data:
        name, url = v
        print ("{:<20} {:<20}".format(name, url))

def remove(args):
    return ''

def main():
    parser = argparse.ArgumentParser(prog='ffssb')
    subparsers = parser.add_subparsers()

    # create
    parser_create = subparsers.add_parser('create', help = 'create a new site specific browser application.')
    parser_create.add_argument('name', help='name of the application')
    parser_create.add_argument('url', help='url the application will use')
    parser_create.add_argument('--display-name', help='set display name of desktop entry')
    parser_create.add_argument('--skip-user-chrome', action='store_true', help='do not add userChrome.css to profile')
    parser_create.set_defaults(func=create)

    # list
    parser_list = subparsers.add_parser('list', help = 'list all site specific browsers created by this tool.')
    parser_list.set_defaults(func=list)

    # remove
    parser_remove = subparsers.add_parser('remove', help = 'remove site specific browser application.')
    parser_remove.add_argument('name', help='name of the application')
    parser_remove.set_defaults(func=remove)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
