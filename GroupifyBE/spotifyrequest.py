__author__ = 'Jared Russell'
__UIN__ = '322006115'

#import operator
import httplib, requests, json, os, re, math, random

api_key = ""



def get_user_profile(username):
	endpoint = "https://api.spotify.com/v1/users/" + username
	r = requests.get(endpoint)
	if r.status_code != 200:
		print "Status Code: " + r.status_code + ". Error accessing user profile " + '"' + username + '"'
	return r.text

def get_user_top_tracks(username,number_of_tracks):
	headers = {"Authorization": "Bearer " + api_key}
	endpoint = "https://api.spotify.com/v1/me/top/tracks?limit=50&offset=0"
	r = requests.get(endpoint,headers=headers)
	if r.status_code != 200:
		print "Status Code: " + str(r.status_code) + ". Error accessing user profile " + '"' + username + '"'
	return r.text

def get_tracks_audio_features(tracks):
	headers = {"Authorization": "Bearer " + api_key}
	endpoint = "https://api.spotify.com/v1/audio-features?ids=" + tracks
	r = requests.get(endpoint,headers=headers)
	if r.status_code != 200:
		print "Status Code: " + str(r.status_code) + ". Error getting audio features"
	return r.text

def get_recommended_songs(tracks):
	headers = {"Authorization": "Bearer " + api_key}
	endpoint = "https://api.spotify.com/v1/recommendations?seed_tracks=" + tracks + "&limit=10"
	r = requests.get(endpoint,headers=headers)
	if r.status_code != 200:
		print "Status Code: " + str(r.status_code) + ". Error recoomended songs"
	return r.text



def main():


    #print get_user_top_tracks("jarheadr176",0)
    #print get_user_profile("jarheadr176")

	#tracks = "7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B"
	#print get_tracks_audio_features(tracks)
	#print get_recommended_songs(tracks)
	return 0




if __name__ == '__main__':
  main()