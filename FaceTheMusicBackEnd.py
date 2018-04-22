import requests
import webbrowser

def calculateSentiment(sentiment_dict):
  happiness = sentiment_dict["happiness"] + sentiment_dict["surprise"]
  neutral = sentiment_dict["neutral"]
  trueSentiment = happiness + .5 * neutral
  return trueSentiment

def findMatchingSong(sentiment_val):
  best_song = ""
  best_delta = 1
  with open("database.txt", "r") as f:
    content = f.readlines()
  content = [x.strip() for x in content]

  for line in content:
    line = line.split("-")
    song_name = line[0]
    song_author = line[1]
    new_delta = abs(sentiment_val - float(line[2]))
    if new_delta < best_delta:
      best_delta = new_delta
      best_song = song_name + "-" + song_author
  
  return best_song

# Sentiment API Section
def createDatabase(filename):
  lyrics_subscription_key = "864224e31ea64158b517554406fd267c"
  assert lyrics_subscription_key
  headers = {"Ocp-Apim-Subscription-Key": lyrics_subscription_key}

  with open("MrBlueSky.txt", "r") as f:
    happy_name = f.readline().strip()
    happy_lyrics = f.read()

  with open("SadSong.txt", "r") as f:
    sad_name = f.readline().strip()
    sad_lyrics = f.read()

  documents = {'documents': [
      {'id': happy_name,
       'language': 'en',
       'text': happy_lyrics},
      {'id': sad_name,
       'language': 'en',
       'text': sad_lyrics}
  ]}

  text_analytics_base_url = "https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/"
  language_api_url = text_analytics_base_url + "languages"
  sentiment_api_url = text_analytics_base_url + "sentiment"
  key_phrase_api_url = text_analytics_base_url + "keyPhrases"

  language_response = requests.post(language_api_url, headers=headers, json=documents)
  sentiment_response = requests.post(sentiment_api_url, headers=headers, json=documents)
  key_phrase_response = requests.post(key_phrase_api_url, headers=headers, json=documents)

  languages = language_response.json()
  sentiments = sentiment_response.json()
  key_phrases = key_phrase_response.json()

  database_list = sentiments["documents"]

  with open(filename, "w") as f:
    for song in database_list:
      f.write(song["id"] + " - " + str(song["score"]) + "\n")


# Face API Section
def returnSong(image_path):
  face_subscription_key = "58ea05bb980e492da0de2f084d435702"
  assert face_subscription_key

  face_api_url = 'https://westus.api.cognitive.microsoft.com/face/v1.0/detect'
  headers = {'Ocp-Apim-Subscription-Key': face_subscription_key,
             'Content-Type': 'application/octet-stream'}
  params = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'true',
    'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
  }

  with open(image_path, "rb") as f:
    img_data = f.read()

  response = requests.post(face_api_url, headers=headers, params=params, data=img_data)
  faces = response.json()
  avg_sentiment = calculateSentiment(faces[0]["faceAttributes"]["emotion"])

  for face in faces:
    fr = face["faceRectangle"]
    fa = face["faceAttributes"]
    avg_sentiment = (avg_sentiment + calculateSentiment(fa["emotion"])) / 2

  matching_song = findMatchingSong(avg_sentiment)
  return matching_song

def openWeb(search_term):
  web_subscription_key = "c451a29781cc414bb7d2da9eee53faf5"
  assert web_subscription_key

  headers = {"Ocp-Apim-Subscription-Key": web_subscription_key}
  params = {"q": search_term, "textDecorations": True, "textFormat": "HTML"}
 
  search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"
  response = requests.get(search_url, headers=headers, params=params)
  response.raise_for_status()
  search_results = response.json()

  webbrowser.open(search_results["videos"]["value"][0]["contentUrl"])

def main():
  database_file = "database.txt"
  createDatabase(database_file)

  image_path = "sad_picture.png"
  song_info = returnSong(image_path)
  openWeb(song_info)

  image_path = "happy_picture.png"
  song_info = returnSong(image_path)
  openWeb(song_info)

  image_path = "surprised_picture.png"
  song_info = returnSong(image_path)
  openWeb(song_info)

if __name__ == "__main__":
  main()

