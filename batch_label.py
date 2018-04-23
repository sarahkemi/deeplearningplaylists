import spotipy
from spotipy import util
from config import config
import json

from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials(client_id=config['spotify_id'], client_secret=config['spotify_secret'])
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

playlists = {}
playlists_info = {}
playlists_data = {}

with open('batch_playlists') as f:
    playlists = f.read().splitlines()

for playlist_uri in playlists:
    username = playlist_uri.split(':')[2]
    playlist_id = playlist_uri.split(':')[4]

    pl_info = sp.user_playlist(username, playlist_id)

    playlists_info[playlist_id] = [pl_info['name'], pl_info['owner']['display_name'], pl_info['description']]

    all_results = []
    current_results = sp.user_playlist_tracks(username, playlist_id)
    all_results.extend(current_results['items'])
    while current_results['next']:
        current_results = sp.next(current_results)
        all_results.extend(current_results['items'])

    playlists_data[playlist_id] = all_results

prev_labelled = json.load(open('labelled'))
pl_ids = set(prev_labelled.keys())

for playlist in playlists_info:
    initial_songs = [[result['track']['name'], result['track']['artists'][0]['name'], result['track']['id']] for result in playlists_data[playlist]]
    songs = []
    for song in initial_songs:
        if song[2] not in pl_ids:
            songs.append(song)

    playlists_data[playlist] = songs

labelled_data = {}
moods = {'1': 'chill', '2': 'hype', '3':'happy', '4':'sad'}
counter = 0

songs_exist = any(playlists_data.values())
playlists_list = list(playlists_data.keys())
if songs_exist:
    while counter < len(playlists_data):
        current_playlist = playlists_list[counter]
        print("---------------------------------")
        print("playlist {} of {}".format(counter+1,len(playlists_data)))
        print("\n{} by {}".format(playlists_info[current_playlist][0],playlists_info[current_playlist][1]))
        if playlists_info[current_playlist][2]:
            print("Description: {}".format(playlists_info[current_playlist][2]))
        print("\npress 'a' to go back a list, and 's' to go forward/skip a list\n'z' to halt and save what is labelled\n\nlabel mood by selecting two #s:")
        print("[1. chill, 2. hype] [3. happy, 4. sad]\n")
        if counter == 0:
            print("**for example, input '13' for a chill & happy playlist\n")
        label_input = input("enter:")
        if label_input:
            if (label_input[0] in moods.keys() and label_input[1] in moods.keys()) or label_input in ('a','s','z'):
                if label_input[0] in moods.keys() and label_input[1] in moods.keys():
                    songs = playlists_data[current_playlist]
                    for song in songs:
                        labelled_data[song[2]] = {"mood": [moods[label_input[0]],moods[label_input[1]]], "name": song[0]}
                    counter += 1
                if label_input in ('a','s'):
                    counter = counter + 1 if label_input == 's' else counter - 1
                if label_input == 'z':
                    break
            else:
                print(label_input)
                print("invalid input, try again!")
else:
    print("everything in playlists file already labelled!")

if songs_exist:
    labelled_data.update(prev_labelled)
    with open('labelled', 'w') as outfile:
        json.dump(labelled_data, outfile)
        print('labelled data saved to file called "labelled"')
