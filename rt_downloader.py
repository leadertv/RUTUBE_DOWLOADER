import os.path
import shutil

import requests

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/98.0.4758.132 YaBrowser/22.3.1.892 Yowser/2.5 Safari/537.36',
    'accept': '*/*'
}


def get_m3u8_list(url):
    req = requests.get(url=url, headers=headers)
    video_data = req.json()
    video_author = video_data['author']['name']
    video_title = video_data['title']
    dict_repl = ["/", "\\", "[", "]", "?", "'", '"', ":", "."]
    for repl in dict_repl:
        if repl in video_title:
            video_title = video_title.replace(repl, "")
        if repl in video_author:
            video_author = video_author.replace(repl, "")
    video_title = video_title.replace(" ", "_")
    video_author = video_author.replace(" ", "_")

    video_m3u8 = video_data['video_balancer']['m3u8']
    return video_author, video_title, video_m3u8


def get_link_from_m3u8(url_m3u8):
    if not os.path.isdir('seg'):
        os.mkdir('seg')
    req = requests.get(url=url_m3u8, headers=headers)
    data_m3u8_dict = []
    with open('seg\\pl_list.txt', 'w', encoding='utf-8') as file:
        file.write(req.text)
    with open('seg\\pl_list.txt', 'r', encoding='utf-8') as file:
        src = file.readlines()

    for item in src:
        data_m3u8_dict.append(item)

    url_playlist = data_m3u8_dict[-1]
    return url_playlist


def get_segment_count(m3u8_link):
    req = requests.get(url=m3u8_link, headers=headers)
    data_seg_dict = []
    for seg in req:
        data_seg_dict.append(seg)
    seg_count = str(data_seg_dict[-2]).split("/")[-1].split("-")[1]
    return seg_count


def get_download_link(m3u8_link):
    link = f'{m3u8_link.split(".m3u8")[0]}/'
    return link


def get_download_segment(link, count):
    if not os.path.isdir('seg'):
        os.mkdir('seg')
    for item in range(1, count+1):
        print(f'[+] - Загружаю сегмент {item}/{count}')
        req = requests.get(f'{link}segment-{item}-v1-a1.ts')
        with open(f'seg\\segment-{item}-v1-a1.ts', 'wb') as file:
            file.write(req.content)
    print('[INFO] - Все сегменты загружены')


def merge_ts(author, title, count):
    if not os.path.isdir(author):
        os.mkdir(author)
    with open(f'seg\\{title}.ts', 'wb') as merged:
        for ts in range(1, count+1):
            with open(f'seg\\segment-{ts}-v1-a1.ts', 'rb') as mergefile:
                shutil.copyfileobj(mergefile, merged)
    os.system(f"ffmpeg -i seg\\{title}.ts {author}\\{title}.mp4")
    print('[+] - Конвертирование завершено')

    file_dir = os.listdir('seg')
    for file in file_dir:
        os.remove(f'seg\\{file}')
    os.removedirs('seg')


def main():
    url = input('[+] - Вставь ссылку на видео для загрузки >>> ').split("/")[-2]
    m3u8_url = get_m3u8_list(f'https://rutube.ru/api/play/options/{url}/?no_404=true&referer=https%3A%2F%2Frutube.ru')
    m3u8_link = get_link_from_m3u8(m3u8_url[2])
    seg_count = int(get_segment_count(m3u8_link))
    dwnl_link = get_download_link(m3u8_link)
    get_download_segment(dwnl_link, seg_count)
    merge_ts(m3u8_url[0], m3u8_url[1], seg_count)


if __name__ == "__main__":
    main()
