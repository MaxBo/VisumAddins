# -*- coding: utf8 -*-
import os


def get_folders(Visum):
    """
    return folders
    """
    version = Visum.VersionNumber[:2]
    visum_appdata = {'15': os.path.join('PTV Vision', 'PTV Visum 15'),
                     }

    p = os.path.join(
        os.environ['APPDATA'],
        visum_appdata.get(version,
                          os.path.join('PTV Vision',
                                       'PTV Visum {}'.format(version))),
    )
    pfd = os.path.join(p, 'ggr.pfd')
    folders = {}
    try:
        with open(pfd) as f:
            lines = f.readlines()
            for line in lines:
                l = line.strip().split('=')
                if len(l) > 1:
                    folders[l[0]] = l[1]
    except IOError as e:
        print('ggr.pfd not found in {}'.format(p))
        raise e
    try:
        pythonpath = os.path.join(folders['ExecutableFolder'], 'python')
        project_folder = folders['ProjectFolder']
    except KeyError as e:
        print('key not found in {pdf}'.format(pfd))
        raise e
    return pythonpath, project_folder
