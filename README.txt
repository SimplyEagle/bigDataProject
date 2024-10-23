The Basics
############
The MusicoSet dataset is included in the repo. It is a big dataset including a huge list of artist, songs, and albums.
There are also sets for popularity and song features that aren't utilized in this version.

The dataset is being used as a big dictionary for artist names, album names, and song names. No ML. The input is read
the code compares it to these big dictionaries and calls Last.fm API to find similar songs. That's the part that needs
to phase out. Our model will replace the API call. But it works technically.

Loading Data
##############
.zip files are for the data. They are too big to load into a repo.
Extract them into the project for it to run.

Local vs Online
################
Right now the program is running locally, but I'd like to deploy it onto Streamlit for online use.
However, it loads from a Git repo and the data files are too big to load into a repo (~140MB for one).
So, for now, it runs on http://localhost:8501/, which is fine.

Future
##############
Actual ML that compared songfeatures.csv to determine songs that the user may like.
Voice Recognition for input?
I'd like some to make the streamlit page less boring.
Mood-based browsing?
