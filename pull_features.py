#grabbing all the features for labelled songs
#TODO script breaks if data exists in features

import spotipy
from spotipy import util
from config import config
import json

from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials(client_id=config['spotify_id'], client_secret=config['spotify_secret'])
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


prev_pulled = json.load(open('features'))
prev_ids = set([x['id'] for x in prev_pulled] if prev_pulled else [])

labelled = json.load(open('labelled'))
l_ids = set(labelled.keys())

ids = list(l_ids - prev_ids)


features = []

if ids:
    batch = 0
    while len(features) < len(ids):
        start = batch * 50
        end = len(ids) if ((batch + 1) * 50 > len(ids)) else ((batch + 1) * 50)
        features.extend(sp.audio_features(ids[start:end]))
        print("batch: ", batch)
        batch += 1

    data = features.extend(prev_pulled) if prev_pulled else features
    with open('features', 'w') as outfile:
        json.dump(data, outfile)
        print('done!')
else:
    print('no update!')
