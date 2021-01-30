# animeworld-downloader [ Works 31/01/2021 ]
A simple python3 script to download animeworld.tv animes.

### Prerequisites
Install the packages down below with pip3:
```
pip3 install --user wget bs4
```

### Installation
To install the script open a terminal and digit:
```
mv path/to/script/animeworld.py /usr/local/bin/animeworld-downloader
```
Be sure the path is included in the environment variable $PATH of your system.

### Usage
The program usage il very simple, type `animeworld` in the command line interface and the magic will happen.
The script will downloads, synchronously, the entire anime inside the folder `/home/$USER/Anime/{anime_name}/` (make sure to have the folder `Anime` inside your home)

If you want a guide you have just to type in the command line:
```
animeworld --help
```


### Support and Credits
Remember to support AnimeWorld team visiting their website: https://www.animeworld.tv/

Created by [@gabryon99](https://github.com/gabryon99)

Currently Maintained by [@AlexZorzi](https://github.com/AlexZorzi)