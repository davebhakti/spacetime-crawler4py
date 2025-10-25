import re
from urllib.parse import urlparse
import json
from bs4 import BeautifulSoup
from pathlib import Path
from collections import Counter

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
scraped_ones = set([])
def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    with open(DATA_DIR/"url.txt", 'a') as file:
        file.write(resp.url + "\n")
    links = set()
    if resp.status != 200:
        return links
    if 600 <= resp.status <= 606:
        return links
    if not resp.raw_response or not resp.raw_response.content:
        return links
    if resp.status == 200:
        raw_content = BeautifulSoup(resp.raw_response.content, features="html.parser")
        tags = raw_content.find_all("a")
        for a in tags:
            link = a.get('href')

            if is_valid(link):
                parsed = urlparse(link)
                fragment = parsed.fragment     

                if len(fragment) > 0:                   # remove fragment part (#...) from url
                    link = link.replace(fragment, "") 

                if link not in scraped_ones:
                    scraped_ones.add(link)
                    links.add(link)
        content = raw_content.get_text()
        tokensList = content.split()
        with open(DATA_DIR/"tokens_per_url.txt", 'a') as file:
            json_object = {"url": resp.url,
                           "tokens": tokensList}
            json.dump(json_object, file)
            file.write("\n")

    links = list(links)
    return links
    
    # Implementation required.
    # url: the URL that was used to get the page

    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
