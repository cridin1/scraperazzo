from github import Github
import logging as lg
import time
import os
import argparse
import requests
from datetime import datetime


def walking_for_files(repo, path, file_type) -> []:
    files = []
    lg.debug(f"{repo.full_name} Searching in {path}")

    for elem in repo.get_contents(path):
        if(elem.type == "dir"):
            files += walking_for_files(repo, elem.path, file_type)
        elif(elem.type == "file" and file_type in elem.name.split(".")[-1]):
            lg.debug(f" Found file in {repo.full_name} : {elem.name}")
            files.append(elem)

    return files

def github_login(token_path) -> Github:
    token = open(token_path,"r").read()
    try:
        g = Github(token)
        lg.info(g.get_user())
    except:
        lg.warn("Error in Github login")

    return g

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Scraperazzo for github repos")
    parser.add_argument("OUTPUT_DIR", help="Output directory for files found")
    parser.add_argument("TOKEN_PATH", help="Github dev. token", nargs='?', default="token.txt")
    parser.add_argument("QUERY", help="Query for the github search",nargs='?', default="commands language:powershell")
    parser.add_argument("FILE_TYPE", help="File type to search", nargs='?',default="ps")
    parser.add_argument("-v","--verbose", help="Verbose", nargs='?', type=int, const=1, default=0)

    args = parser.parse_args()

    TOKEN_PATH = args.TOKEN_PATH 
    OUTPUT_DIR = args.OUTPUT_DIR
    QUERY = args.QUERY
    FILE_TYPE = args.FILE_TYPE
    VERBOSE = args.verbose
    CURRENT_TIME_SET = True

    if(VERBOSE):
        lg.getLogger().setLevel(lg.DEBUG)
        lg.debug(vars(args))
    else:
        lg.getLogger().setLevel(lg.INFO)

    if(not(os.path.exists(OUTPUT_DIR))):
       os.mkdir(OUTPUT_DIR)
    
    if(not(os.path.exists("./logs"))):
       os.mkdir("./logs")
       
    if(not(os.path.exists("current_time.txt"))):
        CURRENT_TIME_SET = False
        #creating file
        fp = open("current_time.txt", "x")
        fp.close()
    else:
        fp = open("current_time.txt", "r")
        end_time_from_file = int(fp.read().strip())
        fp.close()
       
    lg.basicConfig(format='%(asctime)s - %(message)s', 
               datefmt='%d-%b-%y %H:%M:%S',
               level=lg.INFO,
               filename="./logs/log_scraperazzo.txt")
    
    end_time = int(time.time()) if not CURRENT_TIME_SET else end_time_from_file
    
    giorni = 3600*24*15 #every 15 days search for repos
    start_time = end_time - giorni #searching for repos in 10 years (?)
    
    g = github_login(TOKEN_PATH)
    
    for i in range(240):
        try: 
            start_time_str = datetime.utcfromtimestamp(start_time).strftime("%Y-%m-%d")
            end_time_str = datetime.utcfromtimestamp(end_time).strftime("%Y-%m-%d")

            query = f"{QUERY} created:{start_time_str}..{end_time_str}"
            
            lg.info(f"Current end_time {end_time}")
            
            with open("current_time.txt", "w") as fp:
                fp.write(str(end_time))
                fp.close()
            
            start_time -= giorni
            end_time -= giorni
            
            result = g.search_repositories(query)
            
            lg.info(f"In range {start_time_str} -> {end_time_str} found #Repos: {result.totalCount}")
            
            for repo in result:
                
                new_repo_path = os.path.join(OUTPUT_DIR,repo.name)
                
                if(os.path.exists(new_repo_path)):
                    continue
                else:
                    os.mkdir(new_repo_path)
                
                lg.info(f"Searching in  {repo.full_name}")

                founded = walking_for_files(repo,".",FILE_TYPE)
                for elem in founded:
                    try:
                        file_retrieved = requests.get(elem.download_url)
                        with open(os.path.join(new_repo_path, elem.name), 'wb') as f:
                            f.write(file_retrieved.content)
                        f.close()
                        
                    except Exception as e:
                        lg.exception(f"Error in retrieving the file {e} {elem.download_url}")
                        
        
        except Exception as e:
            lg.exception(f"Exception thrown {e}, sleeping for 60 sec...")
            time.sleep(60)
            
        