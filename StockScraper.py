from bs4 import BeautifulSoup
import urllib


stock_ticker = "AMER.L"
page_number = "1"


def scrape_iii_discussion(stock_ticker, page_number):
    url = "http://www.iii.co.uk/investment/detail/?display=discussion&code=cotn%3A"+\
          stock_ticker+\
          "&threshold=0&pageno="+\
          page_number+"&it=le"
    r = urllib.urlopen(url).read()
    soup = BeautifulSoup(r, "html.parser")
    return soup

def get_raw_iii_comments(soup):
    ''' Blah blah'''
    return soup.find_all("div", style="overflow: auto; width: 612px;")

def get_raw_iii_dates(soup):
    return soup.find_all("th", class_="date")

def get_raw_iii_authors(soup):
    return soup.find_all("td", class_="author")

def get_raw_iii_subjects(soup):
    return soup.find_all("td", class_="subject")

def get_raw_iii_votes(soup):
    return soup.find_all("td", class_="votes")

def get_iii_subjects(soup):
    subjects = get_raw_iii_subjects(soup)
    subjects_list = []
    for subject in subjects:
        # Subject text is actually a link so need to use 'a' (for links)
        subjects_list.append(subject.a.get_text())
    return subjects_list

def get_iii_tags(soup):
    subjects = get_raw_iii_subjects(soup)
    tags_list = [] # tag is within the subjects BS object
    for subject in subjects:
        try:
            tags_list.append(subject.span["title"]) #throws an error if there is no span marker
        except:
            tags_list.append("NO TAG")
    return tags_list

def get_iii_votes(soup):
    votes = get_raw_iii_votes(soup)
    votes_list = []
    for vote in votes:
        no_of_votes = vote.span.get_text()
        if no_of_votes == u"": # case where there are no votes
            votes_list.append(0)
        else:
            votes_list.append(int(no_of_votes)) #case where there are votes
    return votes_list

def get_iii_comments(soup):
    comments = get_raw_iii_comments(soup)    
    comments_list = []
    for comment in comments:
        comments_list.append(comment.get_text())
    return comments_list

def get_iii_dates(soup):
    dates = get_raw_iii_dates(soup)

    from dateutil.parser import parse
    from datetime import datetime

    dates_list = []
    for date in dates:
        d = parse(date.get_text())
        if (d - datetime.now()).days >= 0: # for some reason, parser goes to future date
            d = datetime(d.year, d.month, d.day-7, d.hour, d.minute)
            dates_list.append(d)
        else:
            dates_list.append(d)
        
    return dates_list


soup = scrape_iii_discussion("AMER.L","1")
subjects = get_iii_subjects(soup)    
dates = get_iii_dates(soup)
comments = get_iii_comments(soup)
votes = get_iii_votes(soup)
tags = get_iii_tags(soup)

print len(subjects)
print len(dates)
print len(comments)
print len(votes)
print len(tags)






#print soup.prettify()

