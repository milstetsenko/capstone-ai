## Usage
1. Initialize your environment using conda or virtualenv. We prefer virtualenv because of it's easier interface.
```bash 
brew install python
brew install virtualenv
virtualenv -p python3.9 venv
. venv/bin/activate
```
2. Now that our environment is set up, we need to install all required dependencies. To do this execute the command
```bash
pip install -r requirements.txt
```
3. Enter a list of the search queries you want to search for in the file `searchterms.txt`. Every line in this file is a separate query.
4. For each search term we launch a separate thread that has its own headless Chrome instance which is used for image scraping. We support 8 threads at maximum, but this number can be increased depending on the user's machine used for doing this.
5. Run 
```bash
python main.py
```

I took the core logic for the image-scraping and locating 
elements within the search page from [here](https://github.com/ohyicong/Google-Image-Scraper/blob/master/GoogleImageScraper.py)
I have imporoved on it by adding a few neat things like headless mode and concurrency
