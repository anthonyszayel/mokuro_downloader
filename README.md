# mokuro_downloader
Script for downloading volumes from the mokuro.moe/manga repository.

# Why use this?

Sometimes, there are entire volumes/manga folders already in the <a href="https://mokuro.moe/">mokuro repository</a> that are inaccessible through <a href="https://catalog.mokuro.moe/">the catalog</a> (they don't load). Because I was having that problem with a manga I wanted to immerse with, I created this script to download manga directly from the repository along with the volume's respective .mokuro file, so that I could just drag and drop the folder and the file into <a href="https://reader.mokuro.app/">the reader</a> and read without any complications. If you're having a similar problem, this might be useful to you.

# Pre-requisites
- Python 3.13 or newer

# Usage
If you do not have Python 3.13 or newer, install it through their <a href="https://www.python.org/"> official website</a>. Make sure to check the box for adding Python to PATH during installation.

Once Python is installed, run this in CMD:
```
pip3 install requests bs4
```
This will install the modules that make requests to the website and parse html documents, respectively.

Once that is done, download mokuro_downloader.py from this directory and put it in the folder where you would like your manga to be downloaded to and run it. The actual usage of the script is intuitive.


https://github.com/user-attachments/assets/0966b564-eaab-4c2c-97f1-8d28457f5983

# Final comments

I am a beginner information systems student with no real experience in software development. This was my first project, so there are probably various issues I'm not aware of with the code, so I'd be more than happy to hear what you think about it and what I can do to improve in the future. 
