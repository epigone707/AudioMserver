# AudioMserver

AudioMserver is a simple command line server that stores audio files and corresponding metadata. Users can upload a file, download a file, get the metadata of a file, and filter all audio files using query parameter.
## Server setup

```
$ python3 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
$ python3 app.py
```

## Usage


1. POST audio file and store it in the server. 

Upload a file using `--data-binary` option. The content type will be set to `application/x-www-form-urlencoded` and the server can't know the filename. The server will rename the file using metadata.
```
curl -X POST --data-binary @Hello.wav "http://localhost:5000/post"
```


Upload a file with `-F` option. The content type will be set to `multipart/form-data`. The original filename is known to the server.
```
curl -X POST -F file=@innocence.mp3 "http://localhost:5000/post"
curl -X POST -F file=@Avril-Lavigne-Girlfriend.mp3 "http://localhost:5000/post"
```

2. GET a list of stored files. The GET endpoint(s) should accept a query parameter that allows the user to filter results. Results should be returned as JSON. 
```
curl "http://localhost:5000/list?maxduration=300"
curl "http://localhost:5000/list?maxduration=240"

curl "http://localhost:5000/list?artist=Avril+Lavigne"
curl "http://localhost:5000/list?artist=Avril%20Lavigne"

curl "http://localhost:5000/list?album=The+Best+Damn+Thing+(Deluxe+Edition)"
```


3. GET the content of stored files
```
curl "http://localhost:5000/download?name=innocence.mp3" --output downloaded.mp3
```

4. GET metadata of stored files, such as the duration of the audio. 
```
curl "http://localhost:5000/info?name=innocence.mp3"
curl "http://localhost:5000/info?name=Hello.wav"
```

gyfnb!!