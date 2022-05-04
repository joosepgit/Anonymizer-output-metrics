import time
import configparser
import os
import logging


def populateConfigFromFile(file_name_path=None):
    """ Loob konfiguratsiooni objekti """
    start = time.time()
    config = configparser.ConfigParser(
        converters={'list': lambda x: [i.strip() for i in x.split(',')]})

    config.read(os.path.join('inp', 'conf.txt'), encoding='UTF-8')
    
    if not config.has_section("Main") or not config.has_section("ARX"):
        section = "Main" if not config.has_section("Main") else "ARX"
        raise Exception(f'Konfiguratsioonifailis ei leitud sektsiooni {section}.')

    spent = time.time()-start
    logging.info('Populated configuration from file in %s seconds', spent)
    return config

def getSepNaive(path):
    """ Leiab ja tagastab andmefaili veergude separaatori """
    potential_separators = ['\t', ';', ',']
    with open(path, 'r') as f:
        fst_line = f.readline().strip()
        for s in potential_separators:
            if len(fst_line.split(s)) > 1:
                return s
    raise RuntimeError('Could not detect a separator for csv file at {0}'.format(path))