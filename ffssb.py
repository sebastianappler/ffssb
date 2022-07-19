#!/usr/bin/env python3

import argparse
import configparser
import os
import shutil

applicationsDir = os.path.expanduser('~') + '/.local/share/applications/'
ffSettingsDir = os.path.expanduser('~') + '/.mozilla/firefox/'
ffBaseProfile = 'Profile0'

def get_base_profile_path():
    config = configparser.ConfigParser()
    config.optionxform = lambda optionstr : optionstr
    config.read(ffSettingsDir + 'profiles.ini')

    for profile in config.sections():
        if profile == ffBaseProfile:
            return ffSettingsDir + config[profile]['Path']
    return ''

def get_profile_path(profileName):
    return 'ffssb.' + profileName

def add_profile_to_ini(name, profilePath):
    configPath = ffSettingsDir + 'profiles.ini'
    configTmpPath = ffSettingsDir + 'profiles.ini.tmp'

    config = configparser.ConfigParser()
    config.optionxform = lambda optionstr : optionstr
    config.read(configPath)

    profileMaxNum = 0;
    for profile in config.sections():
        if profile.startswith('Profile'):
            profileNum = int(profile.replace('Profile', ''))
            if profileNum > profileMaxNum:
                profileMaxNum = profileNum


    profileMax = 'Profile' + str(profileMaxNum)
    # Profile already exists
    if config[profileMax]['Name'] == name and config[profileMax]['Path'] == profilePath:
        return

    profileNext = 'Profile' + str(profileMaxNum + 1)
    configNew = configparser.RawConfigParser()
    configNew.optionxform = lambda optionstr : optionstr
    configNew.add_section(profileNext)
    configNew.set(profileNext, 'Name', name)
    configNew.set(profileNext, 'Path', profilePath)
    configNew.set(profileNext, 'IsRelative', '1')
    configNew.read_dict(config)

    with open(configTmpPath, 'w') as configfile:
        configNew.write(configfile, space_around_delimiters=False)

    os.remove(configPath)
    shutil.move(configTmpPath, configPath)

def add_desktop_entry(displayName, url, profileName, name, icon):
    desktop_entry_template = '''[Desktop Entry]
Version=1.0
Terminal=false
Type=Application
Name={0}
Exec=firefox --new-window {1} --no-remote -P {2} --name {3} --class {3}
Icon={4}
StartupNotify=true
StartupWMClass={3}'''

    desktop_entry_content = desktop_entry_template.format(displayName, url, profileName, name, icon);
    file_path = r'' + applicationsDir + name + '.desktop'

    with open(file_path, 'w') as fp:
        fp.write(desktop_entry_content)

def create(args):
    baseProfilePath = get_base_profile_path()
    newProfilePath = ffSettingsDir + get_profile_path(args.name)

    shutil.rmtree(newProfilePath, ignore_errors=True)
    shutil.copytree(baseProfilePath, newProfilePath, symlinks=True, dirs_exist_ok=True)
    add_desktop_entry(args.name, args.url, args.name, args.name, 'emacs')
    add_profile_to_ini(args.name, get_profile_path(args.name))

def main():
    parser = argparse.ArgumentParser(prog='ffssb')
    subparsers = parser.add_subparsers()

    # create
    parser_create = subparsers.add_parser('create', help = 'create a new site specific browser application.')
    parser_create.add_argument('name', help='name of the application')
    parser_create.add_argument('url', help='url the application will use')
    parser_create.add_argument('--skip-user-chrome', action='store_true', help='do not add userChrome.css to profile')
    parser_create.set_defaults(func=create)

    # remove
    parser_remove = subparsers.add_parser('remove', help = 'remove site specific browser application.')
    parser_remove.add_argument('name', help='name of the application')

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
