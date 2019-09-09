# Animeworld-downloader
Uno script realizzato in Python 3. Permette di scaricare un intero anime dal sito: https://animeworld.tv

## Prerequisiti
Per potere utilizzare correttamente lo script è necessario installare i seguenti pacchetti attraverso `pip`:
```
pip3 install --user wget bs4
```

## Installazione
Per potere installare lo script basta eseguire questi comandi:
```
mv path/to/script/animeworld.py /usr/local/bin/animeworld-downloader
```
Assicurati che il path sia contentuto all'interno della variabile di ambiente `$PATH` del tuo sistema operativo.

## Utilizzo
L'uso del programma è molto semplice, basta digitare: `animeworld link-anime-da-animeworld`.
Ad esempio:
```
animeworld https://www.animeworld.tv/watch/dragon-ball-super.qu9Y82/XLZNN
```
Lo script scaricherà, in modo sincrono, l'intero anime all'interno della cartella `/home/$USER/Anime/{anime_name}/`.

Per visualizzare il manuale basta digitare:
```
animeworld --help
```


## Supporto
Ricordate di supportare il team di AnimeWorld visitando il loro sito web all'indirizzo: http://animeworld.tv.

gabryon @2019
