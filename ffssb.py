#!/usr/bin/env python3

import argparse
import configparser
import os
import requests
import shutil
from PIL import Image

applications_dir = os.path.expanduser('~') + '/.local/share/applications/'
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

def get_profile_path(profileName):
    return 'ffssb.' + profileName

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
    filePath = r'' + applications_dir + name + '.desktop'
    with open(filePath, 'w') as fp:
        fp.write(desktop_entry_content)

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
#urlbar {
    max-width: 50vh;
}
#urlbar-background {
    visibility: hidden;
}
#urlbar-container {
    margin-right: 70vh;
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
    newprofile_path = ffsettings_dir + get_profile_path(args.name)
    profile_path = get_profile_path(args.name)
    display_name = args.name
    if args.display_name != None:
        display_name = args.display_name

    shutil.rmtree(newprofile_path, ignore_errors=True)
    shutil.copytree(baseprofile_path, newprofile_path, symlinks=True, dirs_exist_ok=True)
    add_desktop_entry(display_name, args.url, args.name, args.name, 'emacs')
    add_profile_to_ini(args.name, profile_path)

    if not args.skip_user_chrome:
        add_user_chrome(profile_path)
        set_userchrome_true(profile_path)

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

    # remove
    parser_remove = subparsers.add_parser('remove', help = 'remove site specific browser application.')
    parser_remove.add_argument('name', help='name of the application')

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
