import bs4 as bs
import urllib.request
import os
import requests
from pathlib import Path
import logging

logging.basicConfig(filename= "logfile-udviddet.log", filemode='w', level=logging.ERROR)


def get_member_links(soup, member_links):
    for url in soup.find_all('a', {"class":"search-result-link"}):
        #print(url["href"])
        member_links.append(url["href"])
    return member_links

def profile_scraper(links):
    for link in links:
        try:
            sauce = urllib.request.urlopen(link).read()
        except Exception as e:
            print("Error opening page: {} \n".format(link), e)
            logging.error("Error opening page {}".format(link))
            continue
        soup = bs.BeautifulSoup(sauce, "lxml")
        try:
            party_name = soup.find("meta", {"name":"Parti"})["content"]
            person_name = soup.find("meta", {"name":"Navn"})["content"]
            photo = soup.find("div", {"class":"person__container"})
            photo_source = (photo.img["src"])
        except Exception as e:
            print("Error parsing page: {}".format(link), e)
            logging.error("Error parsing page of {} in party {}".format(person_name, party_name))
            continue
        if (photo_source == "") or (photo_source == "https://www.ft.dk/-/media/cv/foto/foto-mangler_500x500.ashx"): #Checking if an image is available
            logging.error("Error with downloading image of {} in party {}. No photo available".format(person_name, party_name))
            print("No photo available of {}, moving on to next person").format(person_name)
            continue
        #print(photo_source)
        img_url = os.path.splitext(photo_source)[0] + ".jpg"
        #print(img_url)
        save_location = os.path.join(os.getcwd(), "ft_images", party_name.replace(" ", "_").lower(), person_name.replace(" ", "_").lower() + ".jpg")
        #print(save_location)
        try:        
            Path(os.path.join(os.getcwd(), "ft_images", party_name.replace(" ", "_").lower())).mkdir(parents=True, exist_ok=True)
            f = open(save_location, "wb")
            f.write(requests.get(img_url).content)
            f.close
            print("Downloaded image of {} from party {}".format(person_name, party_name))
        except Exception as e:
            print("Error with downloading image of {} in party {}".format(person_name, party_name), e)
            #Writing missing images to log for manual download
            logging.error("Error with downloading image of {} in party {}".format(person_name, party_name))


def main():
    master_member_page = "https://www.ft.dk/da/search?q=&sf=mf&msf=mf&as=1&Funktion=&pageSize=600&pageNr=1"
    sauce = urllib.request.urlopen(master_member_page).read()
    soup = bs.BeautifulSoup(sauce, "lxml")
    member_links = []
    get_member_links(soup, member_links)
    #print(member_links)
    print("Found {} pages.".format(len(member_links)))
    profile_scraper(member_links)



if __name__ == '__main__':
    main()
