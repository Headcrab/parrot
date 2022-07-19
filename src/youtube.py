import re
from pytube import YouTube
import requests
import os
import uuid

YOUTUBE_API_KEY = "AIzaSyBqnxoxriNrSJhV9e-Jenz8LMA7b6S9OOw"

# get YouTube channelId by channel name
def getChannelId(channelName):
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={channelName}&type=id&key={YOUTUBE_API_KEY}'
    response = requests.get(url)
    channelId = response.json()['items'][0]['snippet']['channelId']
    return channelId
    
# get list of videos (name, link, previewLink) by channelId
def getVideoList(channelName): 
    channelId = getChannelId(channelName)  
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channelId}&maxResults=50&order=date&type=video&key={YOUTUBE_API_KEY}'
    response = requests.get(url)
    videos = response.json()['items']
    videoList = []
    for video in videos:
        videoList.append({
            'channel_name': channelName,
            'name': video['snippet']['title'],
            'link': f'https://www.youtube.com/watch?v={video["id"]["videoId"]}',
            'previewLink': f'https://img.youtube.com/vi/{video["id"]["videoId"]}/0.jpg'
        })
    return videoList

# downloads YouTube video by link
def downloadVideo(link,outpath):
    videoId = link.split('v=')[1]
    url = f'https://www.youtube.com/watch?v={videoId}'
    yt = YouTube(url)
    yt.streams.filter(file_extension="mp4").get_by_resolution("360p").download(outpath)
  
# save preview images to disk
def savePreviewImages(videoList):
    for video in videoList:
        dirName = createCorrectFileName(video['channel_name'])
        os.makedirs(dirName, exist_ok=True)
        fname = f'{dirName}/{createCorrectFileName(video["name"])}.jpg'
        if os.path.exists(fname):
            continue
        try:
            response = requests.get(video['previewLink'])
            with open(fname, 'wb') as f:
                f.write(response.content)
        except:
            pass

# create correct file name from string
def createCorrectFileName(name):
    return re.sub(r'[^\w\s]', '', name).replace(' ', '_')
    
# print videoList with pretty print
def printVideoList(videoList):
    for video in videoList:
        print(f'{video["name"]} - {video["link"]}')

# function generates unique file name with given extension in directoy
def generateUniqueFileName(directory, extension = 'jpg'):
    fileName = f'{uuid.uuid4()}.{extension}'
    while os.path.exists(os.path.join(directory, fileName)):
        fileName = f'{uuid.uuid4()}.{extension}'
    return fileName


class app_yt:
    def run(self):
        while True:
            print('YouTube app')
            print('1. Get list of videos')
            print('2. Download video')
            print('3. Save preview images')
            print('4. Exit')
            try:
                choice = int(input('Enter your choice: '))
                if choice == 1:
                    channelName = input('Enter channel name: ')
                    videoList = getVideoList(channelName)
                    printVideoList(videoList)
                elif choice == 2:
                    link = input('Enter video link: ')
                    outpath = input('Enter output path: ')
                    downloadVideo(link, outpath)
                elif choice == 3:
                    videoList = getVideoList(input('Enter channel name: '))
                    savePreviewImages(videoList)
                elif choice == 4:
                    break
                else:
                    print('Invalid choice')
            except:
                print('Invalid choice')
