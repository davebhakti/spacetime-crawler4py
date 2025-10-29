import re
from urllib.parse import urlparse
import json
from bs4 import BeautifulSoup
from pathlib import Path
from collections import Counter

import ast # So this like is used to parase file containing tokens words from urls
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)
scraped_ones = set([])
def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

stop_words = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 
    'aren', 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 
    'but', 'by', 'can', 'cannot', 'could', 'couldn', 'did', 'didn', 'do', 'does', 'doesn', 
    'doing', 'don', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn', 
    'has', 'hasn', 'have', 'haven', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 
    'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'isn', 'it', 'its', 'itself', 
    'just', 'll', 'm', 'ma', 'me', 'might', 'more', 'most', 'mustn', 'my', 'myself', 
    'needn', 'no', 'nor', 'not', 'now', 'o', 'of', 'off', 'on', 'once', 'only', 'or', 
    'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 're', 's', 'same', 'shan', 
    'she', 'should', 'shouldn', 'so', 'some', 'such', 't', 'than', 'that', 'the', 'their', 
    'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 
    'through', 'to', 'too', 'under', 'until', 'up', 've', 'very', 'was', 'wasn', 'we', 
    'were', 'weren', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 
    'will', 'with', 'won', 'wouldn', 'y', 'you', 'your', 'yours', 'yourself', 'yourselves'
}

def extract_next_links(url, resp):
    with open(data_dir/"url.txt", 'a') as file:
        file.write(resp.url + "\n")
    if "https://grape.ics.uci.edu/wiki/public/wiki/cs122b-20" in url:
        return []
    links = set()
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
        with open(data_dir/"tokens_per_url.txt", 'a') as file:
            json_object = {"url": resp.url, "tokens": tokensList}
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
        if len(url) > 300:
            return False
        if not re.match(r"(.*.?ics.uci.edu)|(.*.?cs.uci.edu)|(.*.?informatics.uci.edu)|(.*.?stat.uci.edu)|(today.uci.edu)", parsed.netloc):
            return False
        if re.match(r"today.uci.edu", parsed.netloc) and not re.match(r"\/department\/information_computer_sciences\/?.*", parsed.path):
            return False
        if re.search(r"(calendar|events|date|week|year|month|day)", parsed.path.lower()):
            return False #Searching all the traps
        if url.lower().count('/') > 20:
            return False
        if re.search(r"sessionid=|sid=", url.lower()):
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

def defragment_url(url):
    for i in range(len(url)-1, -1, -1):
        if url[i] == "#":
            url = url[:i-1]
            break
        if url[i] == "/":
            break
    return url

def most_common_words(word_list, words):
    for wd in word_list:
        if wd.lower() in stop_words or len(wd) < 2:
            continue
        else:
            if wd in words:
                words[wd] += 1
            else:
                words[wd] = 1
    return words

def find_sub_domain(url):
    url = url.strip()
    parsed = urlparse(url)
    subdom = parsed.hostname or ""
    if subdom.startswith("www."):
        subdom = subdom[4:]
    return subdom

def verify_word_list(word_list):
    filtered_tokens = []
    for token in word_list:
        t = token.strip()
        if len(t) <= 1:
            continue
        if t.lower() in stop_words:
            continue
        if not any(char.isalnum() for char in t):
            continue
        filtered_tokens.append(t)

    return filtered_tokens

def print_results(num_urls, longest_page, max_wd_cnt, words, unique_sub):
    print(f"The nunber of unique URLS is {num_urls}")
    print(f"The longest page is {longest_page}")
    print(f"The longest url page word length is {max_wd_cnt}")

    print("Top Fifty Words")
    top_words = sorted(words.items(), key=lambda item: item[1], reverse=True)[:50]

    for word, freq in top_words:
        print(f"{word}: {freq}")
        
    print("All of the Unique Subdomains")
    for subdom, freq in sorted(unique_sub.items()):
        print(f"{subdom}, {freq}")

def traverse_url_list(path):
    unique_urls = set([])
    max_word_count = 0
    longest_page_url = ""
    unique_sub = {}
    words = {}
    with open(path, 'r', encoding='utf-8') as content:
        for line in content:
            try:
                line = line.strip()
                if not line:
                    continue
                URL_CONTENT = ast.literal_eval(line)
                url = URL_CONTENT.get("url")
                url_word_list = URL_CONTENT.get("tokens")
            except Exception as e:
                continue
            
            url = defragment_url(url)
            if url not in unique_urls:
               unique_urls.add(url)

            url_word_list = verify_word_list(url_word_list)
            
            url_word_len = len(url_word_list)
            if longest_page_url == "" or max_word_count <= url_word_len:
                max_word_count = url_word_len
                longest_page_url = url

            words = most_common_words(url_word_list, words)
            sub_domain = find_sub_domain(url)

            if sub_domain not in unique_sub:
                unique_sub[sub_domain] = 1
            else:
                unique_sub[sub_domain] += 1
            
    #print_results(len(unique_urls), longest_page_url, max_word_count, words, unique_sub)
    return [unique_urls, longest_page_url, max_word_count, words, unique_sub]



if __name__ == "__main__":

    
    aa = traverse_url_list("data/tokens_per_url_aa.txt")
    bb = traverse_url_list("data/tokens_per_url_ab.txt")
    cc = traverse_url_list("data/tokens_per_url_ac.txt")

    unique_urls = aa[0].union(bb[0], cc[0])

    if aa[2] >= bb[2] and aa[2] >= cc[2]:
        max_word_count = aa[2]
        longest_page_url = aa[1]
    if bb[2] >= aa[2] and bb[2] >= cc[2]:
        max_word_count = bb[2]
        longest_page_url = bb[1]
    if cc[2] >= aa[2] and cc[2] >= bb[2]:
        max_word_count = cc[2]
        longest_page_url = cc[1]

    words = Counter(aa[3]) + Counter(bb[3]) + Counter(cc[3])
    words = dict(words)

    unique_sub = Counter(aa[4]) + Counter(bb[4]) + Counter(cc[4])
    unique_sub = dict(unique_sub)
        
    
    print_results(len(unique_urls), longest_page_url, max_word_count, words, unique_sub)
