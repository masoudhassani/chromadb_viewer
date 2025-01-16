A simple web-based viewer frontend for chromadb

# Setup
1- Copy ```template_environment_configs.yml``` and name it ```environment_configs.yml```. Then edit the file to add proper information. 

2- If this is the first time setting up the repo, create a virtual environment and install the requirements
```
python3 -m venv ~/.chroma
```
Then activate the environment
```
source ~/.chroma/bin/activate
```
Then install all requirements
```
pip install -r requirements.txt
```

# Launch
After ensuring the configuration files are ready, and requirements are installed, run the following to start the viewer server. You have to feed an argument ```environment```
```
python server.py --environment=<local or cloud>
```

Then open ```index.html```
