#!/usr/bin/env python3

import time
import datetime
import re
import os
import argparse
from typing import List

import wget
import requests
from pathlib import Path
from bs4 import BeautifulSoup


def print_log(m: str, key: str = "none") -> None:
    emojies = {
        'cat': 'ㅇㅅㅇ',
        'confused': '（・∩・）',
        'angry': '(¬､¬)',
        'happy': '（＞ｙ＜）',
        'none': ''
    }
    print("[{}] ene-chan: {} {}".format(str(datetime.date.today().strftime("%d/%m/%Y - %H:%M:%S")), m, emojies[key]))
    return 

def create_directory(anime_name: str) -> str:
    
    video_directory = "{}/Videos".format(str(Path.home()))
    path = "{}/{}".format(video_directory, anime_name)

    if os.path.isdir(path):
        return path

    try:
        os.mkdir(path)
        return path
    except OSError:
        print_log("[X] Error: impossibile creare la cartella che conterrà gli episodi dell'anime.")
        exit(1)
    
    return None

def get_episode_ids(server: str) -> List:

    episodes_id = list()
    for link in server.find_all('a'):
        if 'data-id' in link.attrs:
            episodes_id.append(link.attrs['data-id'])
    return episodes_id


def download_anime(url_anime_raw: str) -> None:

    html_page = requests.get(url_anime_raw).text
    soup = BeautifulSoup(html_page, "html.parser")

    h1 = soup.findAll("h1", {"class": "title"})
    title = h1[0].text

    print_log("Contatto il sever di animeworld.tv per scaricare' %s'..." % title)

    server_28 = soup.find('div', attrs={
        'data-id': 28,
        'class': 'server'
    })

    episodes_id = get_episode_ids(server_28)
    url_request = 'https://www.animeworld.tv/ajax/episode/info'
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'sec-fetch-mode': 'cors',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }    

    links_episode = list()
    i = 0

    for anime_id in episodes_id:
        query = {'ts': int(time.time()), 'server': 28, 'id': anime_id, '_': 674}
        print_log("Richiesta al server 28 per l'episodio %s..." % anime_id)
        r = requests.get(url_request, params=query, headers=headers)
        data = r.json()
        print_log("Risposta per l'episodio %s ricevuta correttamente dal server 28!" % anime_id)
        link_episode = data['grabber']
        links_episode.append(link_episode)
        i += 1
        print_log("Trovati attualmente %d episodio/i..." % i)
    
    path = create_directory(title)
    print_log("Creata directory al seguente indirizzo: '%s'" % path)
    print_log("In download %d episodi dell'anime '%s':" % (len(links_episode), title))

    i = 0

    for link in links_episode:

        regex = re.search("([a-zA-Z0-9\s_\\.\-\(\):])+(.mp4)$", link)
        print_log("Downloading '%s' [%d/%d]" % (regex[0], i, len(links_episode)))
        episode_path = "{}/{}".format(path, regex[0])

        if os.path.isfile(episode_path):
            print_log("Questo episodio è già stato scaricato!")
            i += 1 
            continue

        try:
            wget.download(link, episode_path)
            print("\n")
        except KeyboardInterrupt:
            print_log("\n[X] Error: download dell'anime annullato come richiesto dall'utente...")
            print_log("I file creati verranno eliminati dal sistema...")
            print_log("Chiusura del programma...")
            exit(1)
        pass

    print_log("I download sono stati completati, i video si trovano nella seguente directory:\n%s" % path)

    return None

def main():

    parser = argparse.ArgumentParser(description="Inserisci il link dell'anime che vuoi scaricare.")
    parser.add_argument('link', metavar='l', type=str, help="link dell'anime da scaricare")

    args = parser.parse_args()

    if args.link is None:
        print_log("[X] Error: inserisci il link dell'anime che vuoi scaricare", "angry")
        exit(1)

    download_anime(args.link)

    return


main()