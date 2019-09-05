#!/usr/bin/env python3

import time
import datetime
import re
import os
import argparse
import json
from typing import List, Dict

import wget
import requests
from pathlib import Path
from bs4 import BeautifulSoup

from enum import Enum
    

class Anime():
    def __init__(self, title: str, genre: str, year: int, link_id: str, aid:int = 0):
        self.title = title
        self.genre = genre
        self.year = year
        self.link = link_id
        self.id = aid

    def __str__(self):
        return f"[{self.id}] - {self.title}"


def print_log(m: str, key: str = "none") -> None:
    emojies = {
        'cat': 'ㅇㅅㅇ',
        'confused': '（・∩・）',
        'angry': '(¬､¬)',
        'happy': '（＞ｙ＜）',
        'none': ''
    }
    print("[{}] ene-chan: {} {}".format(str(datetime.date.today().strftime("%d/%m/%Y - %h")), m, emojies[key]))
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

def search_by_keyword(keyword: str) -> Dict[int, Anime]:

    """
    Search anime in animeworld.tv search engine. The search engine
    return from a get call a json object with only a element.
    The element key is 'html' which contains the anime found
    with the keyword inserted by user.
    """
    def make_request(key: str) -> str:
        request = requests.get('https://www.animeworld.tv/ajax/film/search', params={'keyword': key })
        answer = request.content.decode('utf8').replace("'", '"')
        data = json.loads(answer)
        return data['html']

    # create an html parse to elaborate searches
    soup = BeautifulSoup(make_request(keyword), 'html.parser')

    # get anime links and titles, and assign an id
    a_id = 1
    anime_list = dict()

    for e in soup.find_all('a'):

        # get title
        title = e.get('data-jtitle')
        # if title is null then there isn't any anime in that a element
        if title != None:
            link = "{}/{}".format("https://www.animeworld.tv", e.get('href'))
            anime_list[a_id] = Anime(title, 'None', 2019, link, a_id)
            a_id += 1
            
    return anime_list

def search_anime():
    
    anime_name = input("Digita il nome di un anime che vuoi cercare: ")
    if anime_name is None:
        print("[X] Il nome inserito non e' valido!")
        return
    
    anime = search_by_keyword(anime_name)

    if len(anime.values()) > 0:
        
        print(f"Sono stati trovati {len(anime.values())} anime. Digita il numero dell'anime inserito.")
        print("Altrimenti inserisci '0' per uscire dalla ricerca.")
        for a in anime.values():
            print(a)

        choiced = -1

        while choiced < 0 or choiced >= len(anime.values()) + 1:
            user_input = input(f"Digita un numero tra [1-{len(anime.values())}]: ")
            try:
                choiced = int(user_input)
            except ValueError:
                print("[X] Input errato! Inserisci un numero, altrimenti, inserisci '0' per uscire dalla ricerca!")

        if choiced == 0:
            return
        anime_choiced = anime[choiced]
        print(f"Preparazione del download dell'anime: '{anime_choiced.title}'")
        download_anime(anime_choiced.link)

    else:
        print("Non e' stato trovato nessun anime col nome inserito.")

def main():

    def setup_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="Inserisci il link dell'anime che vuoi scaricare.")
        parser.add_argument('--link', default='', type=str, help="link dell'anime da scaricare (default: nessuno)")
        return parser

    def print_menu() -> None:
        print("Digita una delle seguenti operazioni: ")
        print("1 - Cerca un anime da scaricare;")
        print("2 - Inserisci il link di un anime che vuoi scaricare;")
        print("3 - Esci dal programma")

    parser = setup_parser()
    user_choice = 0
    menu = [
        search_anime

    ]

    while user_choice != 3:
        print_menu()
        try:
            user_choice = input('> ')
        except KeyboardInterrupt:
            print("Chiusura del programma in corso...")
        if user_choice == 3:
            continue
        menu[int(user_choice) - 1]()
        print("")


    return


main()