import logging
import re

# 根据url获取id跟类型
def get_id(url):
    app_type = ''
    if '/sub/' in url:
        # 礼包
        pattern = re.compile('/sub/(\d+)/',re.S)
        app_type = 'subs'
    elif '/app/' in url:
        # app
        pattern = re.compile('/app/(\d+)/', re.S)
        app_type = 'app'
    elif '/bundle/' in url:
        # 捆绑包
        pattern = re.compile('/bundle/(\d+)/', re.S)
        app_type = 'bundle'
    else:
        pattern = re.compile('/(\d+)/', re.S)
        app_type = 'other'
        logging.log('WARNING','get_id other url:%s' % url)

    id = re.search(pattern, url)
    if id:
        id = id.group(1)
        return id, app_type
    logging.log('WARNING', 'get_id error url:%s' % url)
    return 0, 'error'