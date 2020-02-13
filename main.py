import json
import itertools
from requests_html import HTMLSession

flatten = itertools.chain.from_iterable
def scrape_links(link):
    # .listmain is the class containing all of the links.
    list_class = '.listmain'
    temp_session = session.get(link)
    list_main = temp_session.html.find(list_class)[0]
    return list(list_main.absolute_links)

def dump_info_pages(filename):
    session = HTMLSession()
    website = 'https://geographic.org/streetview/malta/'
    r = session.get(website)

    # there are 3 layers of pages until information is encountered.
    # not really worth making this recrusive.
    first_layer = scrape_links(website)
    second_layer = flatten([scrape_links(link) for link in first_layer])
    # this is the final layer, this is where the information can be found.
    third_layer = flatten([scrape_links(link) for link in second_layer])
    with open(filename,"w") as file:
        for page in third_layer:
            file.write(page + "\n")

def extract_info_from_dump(filename):
    print("running")
    session = HTMLSession()
    cleaned_data = dict()
    with open(filename, "r") as file:
        # remove the \n from each line
        lines = [line[:len(line)-1] for line in file.readlines()]
        total_lines = len(lines)
        for (line_num, line) in enumerate(lines):
            print("{}%".format(int((line_num/total_lines)*100)))
            temp_session = session.get(line)
            info_list = temp_session.html.find(".listmain")
            split_info = info_list[0].text.split("\n")
            for i in split_info:
                (street, long_lat, post_code) = i.split("\xa0 \xa0")
                (longitude, latitude) = [float(x) for x in long_lat.split(",")]
                resultant_dict = {
                    "street": street,
                    "longitude" :longitude,
                    "latitude":latitude
                }
                cleaned_data[post_code] = resultant_dict

    with open("output.json","w") as file:
        file.write(json.dumps(cleaned_data, indent = 4, sort_keys = True))
    print("done")

extract_info_from_dump("dump.txt")
