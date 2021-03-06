#!/usr/bin/env python3

import time
import datetime
import re
import os
import argparse
import json
from typing import List, Dict, Tuple

import wget
import requests
from pathlib import Path
from bs4 import BeautifulSoup
    

class Anime():
    def __init__(self, title: str, genre: str, year: int, link_id: str, aid:int = 0):
        self.title = title
        self.genre = genre
        self.year = year
        self.link = link_id
        self.id = aid
    def __str__(self) -> str:
        return f"[{self.id}] - {self.title}"


def handle_input(message: str) -> None:
    try:
        return input(message)
    except KeyboardInterrupt:
        print_log("chiusura del programma in corso...", '\n')
        exit(1)
        return

def print_log(m: str, key: str = "") -> None:
    print("{}[{}] animeworld-downloader: {}".format(key, str(datetime.date.today().strftime("%d/%m/%Y")), m))
    return 

def create_directory(anime_name: str) -> str:
    
    def check_anime_folder():
        # check if anime folder exists
        # Just make the download path in the same directory...
        # nobody likes stuff in the home path tbh
        if not os.path.isdir("Anime"):
            try:
                os.mkdir("Anime")
            except OSError:
                print_log("[X] Error: impossibile creare la cartella che conterrà anime.")
                exit(1)

    check_anime_folder()

    video_directory = "Anime"
    path = "{}/{}".format(video_directory, anime_name)

    if os.path.isdir(path):
        return path
    # create anime directory
    try:
        os.mkdir(path)
        return path
    except OSError:
        print_log("[X] Error: impossibile creare la cartella che conterrà gli episodi dell'anime.")
        exit(1)
    
    return None

def get_episodses(server: str) -> List:

    episodes_id = list()
    for link in server.find_all('a'):
        if 'data-id' in link.attrs:
            episodes_id.append({
                'id': link.attrs['data-id'],
                'number': int(link.attrs['data-base'])
            })
    return episodes_id

def download_anime_by_link(url_anime_raw: str, range_episodes: list) -> None:

    if len(range_episodes) == 0:
        return None
    try:
        html_page = requests.get(url_anime_raw).text
        soup = BeautifulSoup(html_page, "html.parser")

        h1 = soup.findAll("h1", {"class": "title"})
        title = h1[0].text
    except:
        print("Errore Nell'Url!")
        return None
    
    print_log("contatto il sever di animeworld.tv per scaricare' %s'..." % title)

    # here you could use a different query, maybe a by finding the server id Es: 8,9,10
    server_active = soup.find('div', 'server active')

    episodes = get_episodses(server_active)
    #change of api endpoint
    url_request = 'https://www.animeworld.tv/api/episode/info'
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'sec-fetch-mode': 'cors',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }    

    links_episode = list()
    i = 0

    for anime in episodes:
        
        anime_id = anime['id']
        anime_num = anime['number']
        if len(range_episodes) >= 1 and range_episodes[0] != 'all' or range_episodes[0] == 0:
            # Bb..bakaa
            if not anime_num in range_episodes:
                continue    
            
    
        print_log("richiesta al server per l'episodio [{}/{}]...".format(anime_id, anime_num))
        
        query = {'ts': int(time.time()), 'id': anime_id}        
        r = requests.get(url_request, params=query, headers=headers)
        data = r.json()

        print_log(f"risposta per l'episodio [{anime_id}/{anime_num}] ricevuta correttamente dal server 28!")

        link_episode = data['grabber']
        links_episode.append(link_episode)

        i += 1

        # print_log("trovati attualmente %d episodio/i..." % i)
    
    # Re:Zero :C
    path = create_directory(title.replace(":",""))
    print_log("creata directory al seguente indirizzo: '%s'" % path)
    print_log("in download %d episodi dell'anime '%s':" % (len(links_episode), title))

    i = 0

    for link in links_episode:

        #regex = re.search("([a-zA-Z0-9\s_\\.\-\(\):])+(.mp4)$", link)
        # bruh keep it simple
        filename = link.split("/")[-1]
        print_log("Downloading '%s' [%d/%d]" % (filename, i, len(links_episode)))
        episode_path = "{}/{}".format(path, filename)

        if os.path.isfile(episode_path):
            print_log("questo episodio è già stato scaricato!")
            i += 1 
            continue

        try:
            print(link)
            wget.download(link, episode_path)
            print("\n")
        except KeyboardInterrupt:
            print_log("\n[!] Warning: download dell'anime annullato come richiesto dall'utente...")
            delete_anime_files(path)
            print_log("chiusura del programma in corso...")
            exit(1)
        pass

    print_log("I download sono stati completati, i video si trovano nella seguente directory:\n%s" % path)

    return None

def delete_anime_files(path: str) -> None:
    for f in os.listdir(path):
        print_log(f"il file '{f}' verra' rimosso dal sistema...")
        os.remove(f)

def search_by_keyword(keyword: str) -> Dict[int, Anime]:

    """
    Search anime in animeworld.tv search engine. The search engine
    return from a get call a json object with only a element.
    The element key is 'html' which contains the anime found
    with the keyword inserted by user.
    """
    def make_request(key: str) -> str:
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'sec-fetch-mode': 'cors',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }    
        # change of api endpoint
        request = requests.get('https://www.animeworld.tv/api/search', params={'keyword': key }, headers=headers)
        data = request.json()
        return data['html']

    data = make_request(keyword)
    if data == None:
        return {}


    # create an html parse to elaborate searches
    soup = BeautifulSoup(data, 'html.parser')

    # get anime links and titles, and assign an id
    a_id = 1
    anime_list = dict()

    for item_tag in soup.find_all("div","item"):
        # get title

        a_tag = item_tag.find("a","name")
        # if href is null then there isn't any anime in that a element
        if a_tag != None:
            link = "https://www.animeworld.tv/"+a_tag["href"]
            anime_list[a_id] = Anime(a_tag.string, 'None', 2019, link, a_id)
            a_id += 1
            
    return anime_list

def get_anime_range() -> List:
    
    print("Quale/i episodio/i vuoi scaricare?")
    print("\t- digita il numero dell'episodio che vorresti scaricare, ad esempio: 8;")
    print("\t- digita un range da xx:yy, ad esempio: 1:100 scarichera' gli episodi da 1 a 100 incluso;")
    print("\t- digita un intervallo separato da ; se vuoi scaricare episodi diversi, ad esempio: 1;5;32;102;")
    print("\t- altrimenti digta 'all', senza virgolette, per scaricare l'intera serie.")
    print("\t- altrimenti digta '0', senza virgolette, per tornare indietro.")


    is_valid = False

    episodes = []

    while not is_valid:
        user_input = handle_input('> ')
        if user_input.lower() == 'all':
            is_valid = True
            episodes = ['all']
        else:
            if re.search("^[0-9]+(\;|\n)", user_input):
                is_valid = True
                episodes = re.split(';', user_input)
                episodes = list(map(int, episodes))
            elif re.search("^[0-9]+\:[0-9]+", user_input):
                is_valid = True
                temp = re.split(':', user_input)
                for i in range(int(temp[0]), int(temp[1]) + 1):
                    episodes.append(i)
            elif re.search("^[0-9]+", user_input):
                is_valid = True
                episodes = [int(user_input)]
            else:
                print("input digitato non corretto! Controlla le istruzioni di sopra...")
                is_valid = False

    return episodes

def download_anime() -> None:

    anime_link = ''
    anime_link = handle_input("Inserisci il link dell'anime che vuoi scaricare: ")
    episodes = get_anime_range()
    download_anime_by_link(anime_link, episodes)

    return

def search_anime() -> None:
    
    anime_name = handle_input("Digita il nome di un anime che vuoi cercare: ")
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
            user_input = handle_input(f"Digita un numero tra [1-{len(anime.values())}] (0 per uscire): ")
            try:
                choiced = int(user_input)
            except ValueError:
                print("[X] Input errato! Inserisci un numero, altrimenti, inserisci '0' per uscire dalla ricerca!")

        if choiced == 0:
            return
        anime_choiced = anime[choiced]
        print(f"Preparazione del download dell'anime: '{anime_choiced.title}'")
        episodes = get_anime_range()
        print("adesso attendi un istante...")
        download_anime_by_link(anime_choiced.link, episodes)

    else:
        print("Non e' stato trovato nessun anime col nome inserito.")

def main() -> int:

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
    arg_link = parser.parse_args().link

    if arg_link != '':
        download_anime_by_link(arg_link, ['all'])
        return 0

    user_choice = 0
    menu = [search_anime, download_anime]

    while user_choice != len(menu) + 1:
        print_menu()
        while True:     #its ugly to end with an error at the input stage because you didnt enter an integer ^^
            try:
                user_choice = int(handle_input('> '))
                if(user_choice >= 1 and user_choice <= 3):
                    break
                else:
                    print("Input non valido!")
            except:
                print("Input non valido!")
                pass
        if user_choice == 3:
            continue
        menu[user_choice - 1]()
        print("")

    return 0

# execute program
if __name__ == "__main__":
    main()

# Last Edited by Alex Zorzi 01/10/2020
# Happy Coding