The Basics
############
The MusicoSet dataset is included in the repo. It is a big dataset including a huge list of artist, songs, and albums.
There are also sets for popularity and song features that aren't utilized in this version.

Loading Data
##############
.zip files are for the data. They are too big to load into a repo.
Extract them into the project for it to run.
To run, pip install streamlit and any other packages you need and enter streamlit run app.py in your favorite command line interface (while in project directory).

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
