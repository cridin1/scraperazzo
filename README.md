# scraperazzo 
Scraper for extracting only specific FILE_TYPE from github, without cloning the entire repos. Install the requirements with pip. To execute the scraperazzo, you need a Github developer token.

```
python scraper.py -h
usage: scraper.py [-h] [-v [VERBOSE]] OUTPUT_DIR [TOKEN_PATH] [QUERY] [FILE_TYPE]

Scraperazzo for github repos

positional arguments:
  OUTPUT_DIR            Output directory for files found
  TOKEN_PATH            Github dev. token
  QUERY                 Query for the github search
  FILE_TYPE             File type to search

options:
  -h, --help            show this help message and exit
  -v [VERBOSE], --verbose [VERBOSE]
                        Verbose

```
