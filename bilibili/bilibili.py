import requests
import re
from contextlib import closing


def getVideoName(url):
    html = requests.get(url).text
    title = re.findall('<title data-vue-meta="true">(.*?)_', html)[0]
    video_url = re.findall(r'"backup_url":\["(.*?)"', html)[0]
    return title, video_url


if __name__ == '__main__':
    # 把这里的链接改为你需要下载的视频链接
    url = 'https://www.bilibili.com/video/av21061574?t=145'
    video_name, video_url = getVideoName(url)

    with closing(
            requests.get(video_url, headers={'referer': url}, stream=True, verify=False)) as response:
        if response.status_code == 200:
            print(video_name)
            print(video_url)
            print('下载中...')
            with open(video_name + '.flv', 'wb') as f:
                for data in response.iter_content(chunk_size=1024):
                    f.write(data)
                    f.flush()
                else:
                    print('视频下载完成，保存在 Python 程序目录下！')
