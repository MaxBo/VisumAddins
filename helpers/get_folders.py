# -*- coding: utf8 -*-
import os


def get_folders(Visum,
                exe_folder='ExecutableFolder',
                project_folder='ProjectFolder'):
    """
    return folders
    """
    appdata_path = get_appdata_path(Visum)
    pfd = os.path.join(appdata_path, 'ggr.pfd')
    folders = {}
    try:
        with open(pfd) as f:
            lines = f.readlines()
            for line in lines:
                l = line.strip().split('=')
                if len(l) > 1:
                    folders[l[0]] = l[1]
    except IOError as e:
        print('ggr.pfd not found in {}'.format(appdata_path))
        raise e
    try:
        pythonpath = os.path.join(folders[exe_folder], 'python')
        project_folder = folders[project_folder]
    except KeyError as e:
        print('key not found in {pdf}'.format(pfd))
        raise e
    return pythonpath, project_folder

def get_appdata_path(Visum):
    version = Visum.VersionNumber[:2]
    visum_appdata = {'15': os.path.join('PTV Vision', 'PTV Visum 15'),
                     }

    appdata_path = os.path.join(
        os.environ['APPDATA'],
        visum_appdata.get(version,
                          os.path.join('PTV Vision',
                                       'PTV Visum {}'.format(version))),
    )
    return appdata_path
