import spotipy
from spotipy import util
from config import config
import json
import vlc

from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials(client_id=config['spotify_id'], client_secret=config['spotify_secret'])
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

all_results = []
playlists = []

with open('playlists') as f:
    playlists = f.read().splitlines()

for playlist_uri in playlists:
    username = playlist_uri.split(':')[2]
    playlist_id = playlist_uri.split(':')[4]

    current_results = sp.user_playlist_tracks(username, playlist_id)
    all_results.extend(current_results['items'])
    while current_results['next']:
        current_results = sp.next(current_results)
        all_results.extend(current_results['items'])

# TODO: read playlist file and only label songs that aren't labelled

songs = [[result['track']['name'],result['track']['artists'][0]['name'],result['track']['id']] for result in all_results]
labelled_data = {}
moods = {'1': 'chill', '2': 'hype', '3':'happy', '4':'sad'}
counter = 0
sample_playing = False
mp3 = None

def stop_sample(mp3):
    if mp3:
        mp3.stop()
        mp3 = None
        sample_playing = False

while counter < len(songs):
    print("---------------------------------")
    print("song {} of {}".format(counter+1,len(songs)))
    print("\n{} by {}".format(songs[counter][0],songs[counter][1]))
    print("\npress 'q' to hear sample of song,\n'a' to go back a song, and 's' to go forward/skip a song\n'z' to halt and save what is labelled\n\nlabel mood by selecting two #s:")
    print("[1. chill, 2. hype] [3. happy, 4. sad]\n")
    if counter == 0:
        print("**for example, input '13' for a chill & happy song\n")
    label_input = input("enter:")
    if label_input:
        if label_input == 'q':
            if sample_playing and mp3:
                stop_sample()
            else:
                song = sp.track(songs[counter][2])
                if song['preview_url']:
                    mp3 = vlc.MediaPlayer(song['preview_url'])
                    mp3.play()
                    sample_playing = True
                else:
                    print("No preview track to play, sorry :(")

        if (label_input[0] in moods.keys() and label_input[1] in moods.keys()) or label_input in ('a','s','z'):
            if sample_playing and mp3:
                stop_sample(mp3)
            if label_input[0] in moods.keys() and label_input[1] in moods.keys():
                labelled_data[songs[counter][2]] = {"mood": [moods[label_input[0]],moods[label_input[1]]], "name": songs[counter][0]}
                counter += 1
            if label_input in ('a','s'):
                counter = counter + 1 if label_input == 's' else -1
            if label_input == 'z':
                break
        else:
            print(label_input)
            print("invalid input, try again!")


with open('labelled', 'w') as outfile:
    json.dump(labelled_data, outfile)
    print('labelled data saved to file called "labelled"')

