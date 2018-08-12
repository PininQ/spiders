# -*- coding:utf-8 -*-
import time
import random
import requests
import json
import csv
import codecs
"""
爬取网易云音乐歌曲的精彩评论
"""


def get_song_id(url):
    """ 从 url 中截取歌曲的 id """
    song_id = url.split('=')[1]
    return song_id


def start_spider(song_id):
    """ 评论数据采用 AJAX 技术获取，下面是获取评论的请求地址 """
    url = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_{}?csrf_token='.format(song_id)

    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.3964.2 Safari/537.36',
        'Origin': 'http://music.163.com',
        'Referer': 'https://music.163.com/song?id={}'.format(song_id),
    }

    formdata = {
        'params': '7j69rOf9B7h7kjawVOQbRd5NiEYw5o7O+jdJs+eCN2jE/Di9NSHkm7Ar0PpciHUb3FE1IR4IwdUlfbdkY2yVlqShtoVEhAomwrhxBb/GSFjKfKZJaDkhSUVgByjMBhBqtfq1I4T307lELiWEbFm+BRBlBoJXtejZce/rf6Gc99ry7EwwNZFGeQ6nOGViekeUomrXMeG0Q3yztn5c16HiC7M40wByj6YBUDt+oz1PCSU=',
        'encSecKey': 'cdd62a540032ad317085f08c010d0e363ab1db5048bb92defaf34a8550f1c7e22950ec0fd45b2d097b685d09a25426456e0269954846ee663fdf2ab4619ca422addae51111274514c309a9d40c6b40af8c5972d38a4c6d52c0383695917ef00a89390a80fa1a96ab329cef9437df98df88b40796b110887598803c1738edbfea'
    }

    # 使用 requests 发起 HTTP 请求
    response = requests.post(url, headers=headers, data=formdata)
    print('\n\n请求 [ ' + url + ' ]，状态码为 ')
    print(response.status_code)
    #
    # get_hot_comments(response.text)
    # 将数据写到 CSV 文件中
    write_to_file(get_hot_comments(response.text))


def get_hot_comments(response):
    """ 
    获取精彩评论
    请求返回结果是 JSON 数据格式，使用 json.loads(response) 将其转化为字典类型，就可以使用 key-value 形式获得值
    """
    data_list = []
    data = {}

    for comment in json.loads(response)['hotComments']:
        data['userID'] = comment['user']['userId']
        data['nickname'] = comment['user']['nickname']
        data['content'] = comment['content']
        data['likedCount'] = comment['likedCount']
        data_list.append(data)
        data = {}
    return data_list


def write_to_file(data_list):
    """
    将数据保存到 CSV 文件中
    """
    print('开始将数据持久化...')
    file_name = '网易云音乐精彩评论.CSV'

    with codecs.open(file_name, 'a+', 'utf_8_sig') as csvfile:
        filenames = ['用户ID', '昵称', '评论内容', '点赞数']
        writer = csv.DictWriter(csvfile, fieldnames=filenames)

        writer.writeheader()
        for data in data_list:
            print(data)
            try:
                writer.writerow({
                    filenames[0]: data['userID'],
                    filenames[1]: data['nickname'],
                    filenames[2]: data['content'],
                    filenames[3]: data['likedCount']
                })
            except UnicodeEncodeError:
                print("编码错误，该数据无法写到文件中，直接忽略该数据")

    print('成功将数据写入到 ' + file_name + ' 中！')


def main():
    songs_url_list = [
        'http://music.163.com/#/song?id=479408220',  # 凉凉
        'http://music.163.com/#/song?id=31445772',  # 理想三旬
        'http://music.163.com/#/song?id=40147554',  # 关键词
        'http://music.163.com/#/song?id=64634',  # 一丝不挂
        'http://music.163.com/#/song?id=64833',  # 沙龙
        'http://music.163.com/#/song?id=34380998',  # 差三岁
        'http://music.163.com/#/song?id=468517654',  # 动物世界
        'http://music.163.com/#/song?id=466122271',  # 高尚
        'http://music.163.com/#/song?id=470759757',  # 不露声色
        'http://music.163.com/#/song?id=208902',  # 红色高跟鞋
    ]

    for each in songs_url_list:
        start_spider(get_song_id(each))
        time.sleep(random.uniform(5, 10))

    print('\n\nURL 列表中的所有歌曲的精彩评论已全部抓取完成！')


if __name__ == '__main__':
    main()