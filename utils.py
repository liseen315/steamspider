import logging
import traceback
import datetime
import platform


def log(msg, level=logging.DEBUG):
    logging.log(level, msg)
    print('%s [level:%s] msg:%s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), level, msg))

    if level == logging.WARNING or level == logging.ERROR:
        for line in traceback.format_stack():
            print(line.strip())

        for line in traceback.format_stack():
            logging.log(level, line.strip())


def get_platform():
    plat = platform.platform()
    if plat.find('Darwin') != -1:
        return 'mac'
    elif plat.find('Linux') != -1:
        return 'linux'
    else:
        return 'mac'
