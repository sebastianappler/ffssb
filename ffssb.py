#!/usr/bin/env python3

import argparse
import configparser
import os
import re
import requests
import shutil
from urllib.parse import urlparse
from PIL import Image

cfg = {
    'ffbaseprofile': 'Profile0',
    'ffssb_prefix': 'ffssb.'
}

def set_linux():
    linux_cfg = {
        'ffssbcache_dir': os.path.expanduser('~') + '/.cache/ffssb/',
        'os_applications_dir': os.path.expanduser('~') + '/.local/share/applications/',
        'os_icons_dir': os.path.expanduser('~') + '/.local/share/icons/hicolor/scalable/apps/',
        'ffsettings_dir': os.path.expanduser('~') + '/.mozilla/firefox/'
    }
    cfg.update(linux_cfg)

def set_windows():
    windows_cfg = {
        'ffssbcache_dir': os.path.expanduser('~') + '\\AppData\\Local\\ffssb\\cache\\',
        'os_applications_dir': os.path.expanduser('~') + '\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs',
        'os_icons_dir': os.path.expanduser('~') + '\\AppData\\Local\\ffssb\\icons\\',
        'ffsettings_dir': os.path.expanduser('~') + '\\AppData\\Roaming\\Mozilla\\Firefox'
    }
    cfg.update(windows_cfg)

def get_base_profile_path():
    config = configparser.ConfigParser()
    config.optionxform = lambda optionstr : optionstr
    config.read(cfg['ffsettings_dir'] + 'profiles.ini')

    for profile in config.sections():
        if profile == cfg['ffbaseprofile']:
            return cfg['ffsettings_dir'] + config[profile]['Path']
    return ''

def get_desktop_entry_path(name):
    return r'' + cfg['os_applications_dir'] + cfg['ffssb_prefix'] + name + '.desktop'

def add_profile_to_ini(name, profile_path):
    config_path = cfg['ffsettings_dir'] + 'profiles.ini'
    config_path_tmp = cfg['ffsettings_dir'] + 'profiles.ini.tmp'

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

def remove_profile_from_ini(name):
    config_path = cfg['ffsettings_dir'] + 'profiles.ini'
    config_path_tmp = cfg['ffsettings_dir'] + 'profiles.ini.tmp'
    config = configparser.ConfigParser()
    config.optionxform = lambda optionstr : optionstr
    config.read(config_path)

    # remove profile
    profile_to_remove = 0
    profile_nums = []
    for profile in config.sections():
        if profile.startswith('Profile'):
            profile_num = int(profile.replace('Profile', ''))
            profile_nums.append(profile_num)

            if config[profile]['Name'] == name:
                profile_to_remove = profile_num
    config.remove_section('Profile' + str(profile_to_remove))

    # rename profiles to be incremental
    profile_nums.sort()
    for num in profile_nums:
        next_profile = 'Profile' + str(num + 1)
        next_next_profile = 'Profile' + str(num + 2)

        if config.has_section(next_profile):
            continue
        if config.has_section(next_next_profile):
            config[next_profile] = config[next_next_profile]
            config.remove_section(next_next_profile)

    # create new config ordered
    new_config_dict = {}
    new_profile_nums = [i for i in range(len(profile_nums)-1)]
    new_profile_nums.sort(reverse=True)
    for num in new_profile_nums:
        profile = 'Profile' + str(num)
        new_config_dict[profile] = config[profile]

    for section in config.sections():
        if not section.startswith('Profile'):
            new_config_dict[section] = config[section]

    new_config = configparser.ConfigParser()
    new_config.optionxform = lambda optionstr : optionstr
    new_config.read_dict(new_config_dict)

    with open(config_path_tmp, 'w') as configfile:
        new_config.write(configfile, space_around_delimiters=False)
    os.remove(config_path)
    shutil.move(config_path_tmp, config_path)

def add_win_shortcut(url, profile):
    ff_exec = '\"C:\\Program Files\\Mozilla Firefox\\firefox.exe\" --new-window {0} --no-remote -P {1}'.format(url, profile)
    ps_cmd = '$s=(New-Object -COM WScript.Shell).CreateShortcut(\'{0}\');$s.TargetPath=\'{1}\';$s.Save()'.format(cfg['os_applications_dir'] + 'test-shortcut.lnk', ff_exec)
def add_desktop_entry(display_name, url, profile, name, icon):
    desktop_entry_template = '''[Desktop Entry]
Version=1.0
Terminal=false
Type=Application
Name={0}
Exec=firefox --new-window "{1}" --no-remote -P "{2}" --name "{3}" --class "{3}"
Icon={4}
StartupNotify=true
StartupWMClass={3}'''

    desktop_entry_content = desktop_entry_template.format(display_name, url, profile, name, icon);
    with open(get_desktop_entry_path(name), 'w') as fp:
        fp.write(desktop_entry_content)

def add_desktop_entry_icon(name, url):
    if not os.path.exists(cfg['ffssbcache_dir']):
        os.mkdir(cfg['ffssbcache_dir'])

    icon_path = cfg['ffssbcache_dir'] + name + '.ico'
    if not os.path.exists(icon_path):
        domain = str(urlparse(url).hostname)
        ico_url = 'https://icons.duckduckgo.com/ip3/{0}.ico'.format(domain)
        ico_file = requests.get(ico_url)
        open(icon_path, 'wb').write(ico_file.content)

    icon_sizes = ['16', '32']
    img_paths = {}
    for size in icon_sizes:
        app_icons_path = cfg['os_icons_dir'] + '{0}x{0}'.format(size) + os.path.sep + 'apps'
        if not os.path.exists(app_icons_path):
            os.makedirs(app_icons_path)

        img_paths[size] = app_icons_path + os.path.sep + name + '.png'
        if not os.path.exists(img_paths[size]):
            img = Image.open(icon_path)
            img.save(img_paths[size], format = 'PNG', sizes=[(size, size)])

    return img_paths['32']

def add_user_chrome(profile_path):
    chrome_css = '''@namespace url("http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul");
/* hide clutter */
#PersonalToolbar,
#page-action-buttons
{
    visibility: collapse;
}
.urlbarView {
    display: none !important;
}
#urlbar-background {
    visibility: hidden;
}
/* hide all tabs but first */
#tabbrowser-arrowscrollbox tab:not(:first-child) {
    display: none;
}

/* structure bars */
#nav-bar {
    margin-top: -6px;
    margin-right: 75px;
    margin-left: 32px;
    max-height: 36px;
    box-shadow: none !important;
}
#urlbar-container {
    margin-right: 70vh;
    max-width: 35vh;
}
#titlebar {
    margin-bottom: -30px;
}
#TabsToolbar {
    background: #444;
    border-radius: 10px 10px 0px 0px;
}

/* adjust button alignments */
toolbarbutton {
    margin-top: -5px !important;
}
.titlebar-buttonbox-container {
    margin-top: 6px;
}

/* favicon */
#TabsToolbar-customization-target {
    margin-left: -40px;
}
#tabbrowser-arrowscrollbox * {
    min-width: 0px !important;
    max-width: 32px !important;
    max-height: 32px !important;
}
.tab-background,
.tab-close-button
{
    display: none;
}
tab {
    padding-top: 2px !important;
}
'''
    chrome_dir = cfg['ffsettings_dir'] + profile_path + os.path.sep + 'chrome'
    if not os.path.exists(chrome_dir):
        os.mkdir(chrome_dir)
    with open(chrome_dir + os.path.sep +'userChrome.css', 'w') as fp:
        fp.write(chrome_css)

def add_to_about_config(profile_path, configLine):
    user_js_file = cfg['ffsettings_dir'] + profile_path + os.path.sep + 'user.js'
    if os.path.exists(user_js_file):
        filedata = ""
        with open(user_js_file, 'r') as fp:
            filedata = fp.read()
        if not filedata.find(configLine):
            with open(user_js_file, 'a') as fp:
                fp.writelines(configLine)
    else:
        with open(user_js_file, 'w') as fp:
            fp.write(configLine)

def set_userchrome_true(profile_path):
    userchrome_true = 'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);'
    add_to_about_config(profile_path, userchrome_true)

def create(args):
    baseprofile_path = get_base_profile_path()
    ffssb_name = cfg['ffssb_prefix'] + args.name
    newprofile_path = cfg['ffsettings_dir'] + ffssb_name
    display_name = args.name
    icon_path = cfg['os_icons_dir'] + os.path.sep + args.name

    if args.display_name != None:
        display_name = args.display_name

    if not os.path.exists(newprofile_path):
        shutil.copytree(baseprofile_path, newprofile_path, symlinks=True, dirs_exist_ok=True)
        # remove previous sessions
        shutil.rmtree(newprofile_path + os.path.sep + 'sessionstore-backups')
        os.remove(newprofile_path + os.path.sep + 'sessionCheckpoints.json')

    if args.icon != None:
        shutil.copy2(args.icon, icon_path)
    else:
        try:
            icon_path = add_desktop_entry_icon(args.name, args.url)
        except:
            # We dont care if the icon fails
            # but don't break the program
            print("Could not add icon")

    add_desktop_entry(display_name, args.url, args.name, args.name, icon_path)
    add_profile_to_ini(args.name, ffssb_name)

    if not args.skip_user_chrome:
        add_user_chrome(ffssb_name)
        set_userchrome_true(ffssb_name)

def list(args):
    applications = os.listdir(cfg['os_applications_dir'])
    ffssb_application_files = [a for a in applications if cfg['ffssb_prefix'] in a]

    data = []
    for file in ffssb_application_files:
        with open(cfg['os_applications_dir'] + file, 'r') as fp:
            file_text = fp.read()
            name = re.findall(r'^ffssb\.(.+)\.desktop$' ,file)[0]
            url = re.findall(r'(https?://\S+)', file_text)[0]
            data.append([name, url])

    if len(data) == 0:
        return

    print ("{:<20} {:<20}".format('NAME','URL'))
    for v in data:
        name, url = v
        print ("{:<20} {:<20}".format(name, url))

def launch(args):
    desktop_path = get_desktop_entry_path(args.name)
    if os.path.exists(desktop_path):
        with open(desktop_path, 'r') as fp:
            file_text = fp.read()
            exec_cmd = re.findall(r'^(?:Exec=)(.+)$', file_text, re.MULTILINE)[0]
            if len(exec_cmd) == 0:
                return
            os.system(exec_cmd)

def remove(args):
    ffssb_name = cfg['ffssb_prefix'] + args.name
    profile_path = cfg['ffsettings_dir'] + ffssb_name

    if os.path.exists(get_desktop_entry_path(args.name)):
        os.remove(get_desktop_entry_path(args.name))

    if os.path.exists(profile_path):
        shutil.rmtree(profile_path)

    remove_profile_from_ini(args.name)

def main():
    set_linux()

    parser = argparse.ArgumentParser(prog='ffssb')
    subparsers = parser.add_subparsers()

    # create
    parser_create = subparsers.add_parser('create', help = 'create a new site specific browser application.')
    parser_create.add_argument('name', help='name of the application')
    parser_create.add_argument('url', help='url the application will use')
    parser_create.add_argument('--display-name', help='set display name of desktop entry')
    parser_create.add_argument('--icon', help='path to custom icon')
    parser_create.add_argument('--skip-user-chrome', action='store_true', help='do not add userChrome.css to profile')
    parser_create.set_defaults(func=create)

    # list
    parser_list = subparsers.add_parser('list', help = 'list all site specific browsers created by this tool.')
    parser_list.set_defaults(func=list)

    # launch
    parser_launch = subparsers.add_parser('launch', help = 'launch site specific browser application.')
    parser_launch.add_argument('name', help='name of the application')
    parser_launch.set_defaults(func=launch)

    # remove
    parser_remove = subparsers.add_parser('remove', help = 'remove site specific browser application.')
    parser_remove.add_argument('name', help='name of the application')
    parser_remove.set_defaults(func=remove)

    args = parser.parse_args()

    if hasattr(args, 'name'):
        if args.name == 'default' or args.name == 'default-release':
            print("Name is reserved by firefox. Aborting...")
            return

    args.func(args)

if __name__ == '__main__':
    main()
