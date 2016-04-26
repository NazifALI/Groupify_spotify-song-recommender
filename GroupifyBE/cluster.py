__author__ = 'Jared'

import random,math,operator,json,requests



##REQUESTS##

def get_user_top_tracks(api_key):
	headers = {"Authorization": "Bearer " + api_key}
	endpoint = "https://api.spotify.com/v1/me/top/tracks?limit=50&offset=0"
	r = requests.get(endpoint,headers=headers)
	if r.status_code != 200:
		print "Status Code: " + str(r.status_code) + ". Error accessing user profile"
	return json.loads(r.text)

def get_tracks_audio_features(tracks,api_key):
	headers = {"Authorization": "Bearer " + api_key}
	endpoint = "https://api.spotify.com/v1/audio-features?ids=" + tracks
	r = requests.get(endpoint,headers=headers)
	if r.status_code != 200:
		print "Status Code: " + str(r.status_code) + ". Error getting audio features"
	return json.loads(r.text)

def get_recommended_songs(tracks,api_key):
	headers = {"Authorization": "Bearer " + api_key}
	endpoint = "https://api.spotify.com/v1/recommendations?seed_tracks=" + tracks + "&limit=20"
	r = requests.get(endpoint,headers=headers)
	if r.status_code != 200:
		print "Status Code: " + str(r.status_code) + ". Error recoomended songs"
	return json.loads(r.text,'string')

##REQUESTS##

def get_top_track_features(api_key):
    top_tracks_json = get_user_top_tracks(api_key)
    song_ids = []
    for item in top_tracks_json['items']:
        song_ids.append(item['id'])
    #Convert list to CSL
    song_ids = ','.join(song_ids)
    return get_tracks_audio_features(song_ids,api_key)


def read_in_top_tracks(api_key):
    #f = open("testsongs.txt")
    #j = json.loads(f.read())
    j = get_top_track_features(api_key)
    relevant_info = ["danceability","energy","key","loudness","mode","speechiness","acousticness","instrumentalness","liveness","valence","tempo"]
    songs = {}
    for song in j['audio_features']:
        dict = {}
        for info in relevant_info:
            dict[info] = song[info]
        songs[song['id']] = dict
    return songs

#changes the score to a 0-1 range
def normalize_scores(songs):
    #Read in the features and their ranges
    f = open("audio_features.txt")
    features_dict = {}
    for line in f:
        feature = line.split(',')
        features_dict[feature[0]] = (feature[1],feature[2])

    #Normailize the scores
    for song in songs:
        for feature in songs[song]:
            score = songs[song][feature]
            l_boundry = int(features_dict[feature][0])
            u_boundry = int(features_dict[feature][1])
            normalized_score = (score-l_boundry)/(u_boundry-l_boundry)
            songs[song][feature] = normalized_score


#Chooses the five songs closest to the center
def five_best_songs(centers,clusters,songs):
    combined_cluster_scores = {}
    for center in centers:
        if len(clusters[center]) > 5:
            single_cluster_scores = {}
            for song in clusters[center]:
                single_cluster_scores[song] = get_cosine_score(centers[center],songs[song])
            #insert top five selecting here
            single_cluster_top_five_scores = dict(sorted(single_cluster_scores.iteritems(), key=operator.itemgetter(1), reverse=True)[:5])
            combined_cluster_scores[center] = single_cluster_top_five_scores.keys()
        else:
            combined_cluster_scores[center] = clusters[center]

    return combined_cluster_scores



#Used from previous submitted code
def get_cosine_score(center,song):
    c_dot_s = 0
    for feature in center:
        c_dot_s += center[feature] * song[feature]

    c_magnitude = 0
    for feature in center:
        c_magnitude += pow(center[feature],2)
    c_magnitude = math.sqrt(c_magnitude)

    s_magnitude = 0
    for feature in song:
        s_magnitude += pow(song[feature],2)
    s_magnitude = math.sqrt(s_magnitude)

    denominator = c_magnitude * s_magnitude
    if denominator == 0:
        return 0

    cosine_score = c_dot_s/denominator

    return cosine_score


def cluster_songs(centers,songs):
    clusters = {}
    for center in centers:
        clusters[center] = []
    for song in songs:
        center_scores = {}
        for center in centers:
            center_scores[center] = get_cosine_score(songs[center],songs[song])
        str = max(center_scores.iteritems(), key=operator.itemgetter(1))[0]
        clusters[str].append(song)
    return clusters

def calculate_centers(clusters,songs):
    centers = {}
    for cluster in clusters:
        centers[cluster] = {}
        for song in clusters[cluster]:
            if centers[cluster] == {}:
                centers[cluster] = songs[song]
            else:
                for info in centers[cluster]:
                    centers[cluster][info] += songs[song][info]
        for info in centers[cluster]:
            centers[cluster][info] = centers[cluster][info]/len(clusters[cluster])
    return centers

def clusters_equivalent(old_clusters,new_clusters):
    if new_clusters == {}:
        return False
    clusters_are_equivlent = True
    for cluster in old_clusters:
        if old_clusters[cluster] != new_clusters[cluster]:
            clusters_are_equivlent = False
    return clusters_are_equivlent




#This will take in a k value and an array of json object songs and generate clusters
#songs data format
#{songId:{("danceability":value(0-1)),("energy":value(0-1))("key":value(0-11)),("loudness":value),("mode":value),("speechiness":value),("acousticness":value),("instrumentalness":value),("liveness":value),("valence":value),("tempo":value)}...}
def calculate_clusters(k,songs):
    #Use k random songs for intial centers
    #Center data format:
    #{center1:{("danceability":value(0-1)),("energy":value(0-1))("key":value(0-11)),("loudness":value(-60-0)),("mode":value(0-1)),("speechiness":value(0-1)),("acousticness":value(0-1)),("instrumentalness":value(0-1)),("liveness":value(0-1)),("valence":value(0-1)),("tempo":value(0-200))}...}
    initial_centers = random.sample(songs, k)
    normalize_scores(songs)
    old_clusters = cluster_songs(initial_centers,songs)
    new_clusters = {}
    centers = {}
    first_iteration = True
    while not clusters_equivalent(old_clusters,new_clusters):
        print 'Iteration'
        if first_iteration:
            centers = calculate_centers(old_clusters,songs)
            new_clusters = cluster_songs(centers,songs)
            first_iteration = False
        else:
            centers = calculate_centers(new_clusters,songs)
            new_clusters = cluster_songs(centers,songs)
            old_clusters = new_clusters


    clusters_top_five = five_best_songs(centers,new_clusters,songs)
    return clusters_top_five


def clusters_to_reccomended_songs(clusters,api_key):
    recommended_songs = {}
    for cluster in clusters:
        #Convert list to CSL
        csl_cluster = ','.join(clusters[cluster])
        recommended_songs[cluster] = get_recommended_songs(csl_cluster,api_key)

    #Need to normalize to str from unicode
    for cluster in recommended_songs:
        cluster_dict = {}
        for track in recommended_songs[cluster]['tracks']:
            track_dict = {}
            track_dict['name'] = track['name']
            track_dict['preview_url'] = track['preview_url']
            track_dict['uri'] = track['uri']
            cluster_dict[track['id']] = track_dict
        recommended_songs[cluster] = cluster_dict

    return recommended_songs


def clustering_based_recommendations(api_key):
    songs = read_in_top_tracks(api_key)
    clusters = calculate_clusters(3,songs)
    recommended_songs = clusters_to_reccomended_songs(clusters,api_key)
    return recommended_songs



def main():

    api_key = ""


    recommended_songs = clustering_based_recommendations(api_key)


    for item in recommended_songs:
        print recommended_songs[item]
    print "done"


if __name__ == '__main__':
  main()