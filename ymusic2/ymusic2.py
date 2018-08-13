# -*- coding:utf-8 -*-
import pymongo
import random
import time
from math import ceil
from selenium import webdriver
from selenium.webdriver.common.by import By

"""
使用 Selenium 爬取网易云音乐歌曲的所有评论数据，
并存储到 MongoDB 中
"""
MONGO_HOST = '127.0.0.1'
MONGO_PROT = 27017
MONGO_DB = 'ymusic'
MONGO_COLLECTION = 'comments'

client = pymongo.MongoClient(MONGO_HOST, MONGO_PROT)
db_manager = client[MONGO_DB]


def start_spider(url):
    """ 启动 Chrome 浏览器访问页面 """
    """
    # 从 Chrome 59 版本开始，支持 Headless 模式（无界面模式），即不会弹出浏览器
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    brower = webdriver.Chrome(chrome_options)
    """
    brower = webdriver.Chrome()
    brower.get(url)
    # 等待 5s，让评论数据加载完成
    print('评论数据正在加载，等待 5s')
    time.sleep(5)
    # 页面被嵌套一层 iframe，必须切换到 iframe，才能定位到 iframe 里面的元素
    iframe = brower.find_element_by_class_name('g-iframe')
    brower.switch_to.frame(iframe)
    # 增加一层防护，拉动滚动条到底部
    js = "var q=document.documentElement.scrollTop=20000"
    brower.execute_script(js)

    # 获取 comments(最新评论) 总数
    new_comments = brower.find_elements(By.XPATH, "//h3[@class='u-hd4']")[1]

    max_page = get_max_page(new_comments.text)

    current = 1
    is_first = True
    while current <= max_page:
        print('正在爬取第 ', current, ' 页的评论数据')
        if current == 1:
            is_first = True
        else:
            is_first = False
        data_list = get_comments(is_first, brower)
        # 将第 1 页评论数据存储到 MongoDB 中
        save_data_to_mongo(data_list)
        # 模拟点击下一页
        time.sleep(1)
        go_nextpage(brower)
        # 模拟人为浏览
        sim = random.randint(8, 12)
        print('模拟人为浏览点击【下一页】的时间为 {}s'.format(sim))
        time.sleep(sim)
        current += 1


def get_max_page(new_comments):
    """ 根据评论总数计算出总的页数 """
    print('-' * 20 + new_comments + '-' * 20)
    max_page = new_comments.split('(')[1].split(')')[0]
    # 每页显示 20 条最新评论
    offset = 20
    max_page = ceil(int(max_page) / offset)
    print('---------最新评论总共', max_page, '页---------')
    return max_page


def get_comments(is_first, borwer):
    """ 获取评论数据 """
    items = borwer.find_elements(By.XPATH, "//div[@class='cmmts j-flag']/div[@class='itm']")
    # 首页的评论数据中包含 15 条精彩评论，20 条最新评论，只保留最新评论
    if is_first:
        items = items[15: len(items)]

    data_list = []
    data = {}
    for each in items:
        # 用户 ID
        userId = each.find_elements_by_xpath("./div[@class='head']/a")[0]
        userId = userId.get_attribute('href').split('=')[1]
        # 用户昵称
        nickname = each.find_elements_by_xpath("./div[@class='cntwrap']/div[1]/div[1]/a")[0]
        nickname = nickname.text
        # 评论内容
        content = each.find_elements_by_xpath("./div[@class='cntwrap']/div[1]/div[1]")[0]
        content = content.text.split('：')[1]
        # 点赞数
        like = each.find_elements_by_xpath("./div[@class='cntwrap']/div[@class='rp']/a[1]")[0]
        like = like.text
        if like:
            like = like.strip().split('(')[1].split(')')[0]
        else:
            like = '0'
        # 头像地址
        avatar = each.find_elements_by_xpath("./div[@class='head']/a/img")[0]
        avatar = avatar.get_attribute('src')

        data['userId'] = userId
        data['nickname'] = nickname
        data['content'] = content
        data['like'] = like
        data['avatar'] = avatar
        print(data)
        data_list.append(data)
        data = {}
    return data_list


# 写入 MongoDB
def save_data_to_mongo(data_list):
    """
    一次性插入 20 条评论。插入效率高，降低数据丢失风险。
    """
    collection = db_manager[MONGO_COLLECTION]
    try:
        if collection.insert_many(data_list):
            print('成功插入 ', len(data_list), ' 条数据')
    except Exception:
        print('插入数据出现异常！')


# 点击下一页
def go_nextpage(brower):
    """
    模拟人为操作，点击【下一页】
    """
    next_button = brower.find_elements(By.XPATH, "//div[@class='m-cmmt']/div[3]/div[1]/a")[-1]
    if next_button.text == '下一页':
        next_button.click()


if __name__ == '__main__':
    # 正在爬取第  47  页的评论数据
    url = 'https://music.163.com/#/song?id=31445772'  # 理想三旬
    start_spider(url)
