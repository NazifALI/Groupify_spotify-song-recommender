__author__ = 'Jared'

import random,math,operator,json

def read_in_songs(file_name):
    comma_separated_list = ""
    song_file = open(file_name)
    for line in song_file:
        comma_separated_list = comma_separated_list +  line + ','
    #Remove the last char
    comma_separated_list = comma_separated_list[:-1]
    return comma_separated_list.replace(" ","")

def read_in_top_tracks(top_tracks):
    f = open("testsongs.txt")
    j = json.loads(f.read())
    relevant_info = ["danceability","energy","key","loudness","mode","speechiness","acousticness","instrumentalness","liveness","valence","tempo"]
    songs = {}
    for song in j['audio_features']:
        dict = {}
        for info in relevant_info:
            dict[info] = song[info]
        songs[song['id']] = dict
    return songs



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
    #{center1:{("danceability":value(0-1)),("energy":value(0-1))("key":value(0-11)),("loudness":value),("mode":value),("speechiness":value),("acousticness":value),("instrumentalness":value),("liveness":value),("valence":value),("tempo":value)}...}
    initial_centers = random.sample(songs, k)
    old_clusters = cluster_songs(initial_centers,songs)
    new_clusters = {}
    while not clusters_equivalent(old_clusters,new_clusters):
        centers = calculate_centers(old_clusters,songs)
        new_clusters = cluster_songs(centers,songs)

    return new_clusters




def main():

    songs = read_in_top_tracks("testsongs.txt")
    clusters = calculate_clusters(3,songs)
    print clusters

    #print read_in_songs("t8esttoptracks.txt")
    #calculate_clusters(5,songs)


if __name__ == '__main__':
  main()