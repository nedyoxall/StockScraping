from bs4 import BeautifulSoup
import urllib
import pandas as pd
import os

 
class ScrapeIII():
    
    def __init__(self, stock_ticker):

        if os.path.exists('Data/III/' + stock_ticker + '.pkl'):
            print "Data for this stock already exists, now checking for updates."
            self.df = self.update_scrape(stock_ticker, 5) #[TODO] edit no of pages
        else:
            print "Creating new dataframe for this stock."
            self.df = self.initial_scrape(stock_ticker, 2)
            print self.df.head()            
    
    def scrape_iii_discussion(self, stock_ticker, page_number):
        url = "http://www.iii.co.uk/investment/detail/?display=discussion&code=cotn%3A"+\
              stock_ticker+\
              "&threshold=0&pageno="+\
              page_number+"&it=le"
        
        r = urllib.urlopen(url).read()
        self.soup = BeautifulSoup(r, "html.parser")
        return self.soup
    
    def get_raw_iii_comments(self):
        ''' Blah blah'''
        return self.soup.find_all("div", style="overflow: auto; width: 612px;")
    
    def get_raw_iii_dates(self):
        return self.soup.find_all("th", class_="date")
    
    def get_raw_iii_authors(self):
        return self.soup.find_all("td", class_="author")
    
    def get_raw_iii_subjects(self):
        return self.soup.find_all("td", class_="subject")
    
    def get_raw_iii_votes(self):
        return self.soup.find_all("td", class_="votes")
    
    def get_iii_subjects(self):
        subjects = self.get_raw_iii_subjects()
        subjects_list = []
        for subject in subjects:
            # Subject text is actually a link so need to use 'a' (for links)
            subjects_list.append(subject.a.get_text())
        return subjects_list
    
    def get_iii_tags(self):
        subjects = self.get_raw_iii_subjects()
        tags_list = [] # tag is within the subjects BS object
        for subject in subjects:
            try:
                tags_list.append(subject.span["title"]) #throws an error if there is no span marker
            except:
                tags_list.append("NO TAG")
        return tags_list
    
    def get_iii_votes(self):
        votes = self.get_raw_iii_votes()
        votes_list = []
        for vote in votes:
            no_of_votes = vote.span.get_text()
            if no_of_votes == u"": # case where there are no votes
                votes_list.append(0)
            else:
                votes_list.append(int(no_of_votes)) #case where there are votes
        return votes_list
    
    def get_iii_comments(self):
        comments = self.get_raw_iii_comments()    
        comments_list = []
        for comment in comments:
            comments_list.append(comment.get_text())
        return comments_list
    
    def get_iii_authors(self):
        authors = self.get_raw_iii_authors()    
        authors_list = []
        for author in authors:
            authors_list.append(author.a.get_text()) 
            # .encode('utf-8') prevents encoding error (after get_text())
        return authors_list
    
    def get_iii_dates(self):
        dates = self.get_raw_iii_dates()
    
        from dateutil.parser import parse
        from datetime import datetime, timedelta
    
        dates_list = []
        for date in dates:
            d = parse(date.get_text(), dayfirst = True)
            if (d - datetime.now()).days >= 0: # for some reason, parser goes to future date
                d = d - timedelta(days=7)
                dates_list.append(d)
            else:
                dates_list.append(d)
            
        return dates_list
    
    
    def initial_scrape(self, stock_ticker, max_pages):
        i = 1
        subjects, dates, comments, votes, tags, authors = [], [], [], [], [], []
        while i <= max_pages:
            soup = self.scrape_iii_discussion(stock_ticker,str(i))
            if len(self.get_iii_subjects()) == 0:
                print "There are only " + str(i-1) + " pages with data."
                break    
            else:	
                subjects.extend(self.get_iii_subjects())    
                dates.extend(self.get_iii_dates())
                comments.extend(self.get_iii_comments())
                votes.extend(self.get_iii_votes())
                tags.extend(self.get_iii_tags())
                authors.extend(self.get_iii_authors())
                print "Got page " + str(i)
                i+=1
                
        dict_for_pd = {'date' : dates,
                       'tag' : tags,
                       'subject' : subjects,
                       'votes' : votes,
                       'author' : authors,
                       'comment' : comments}
        
        iii_df = pd.DataFrame(dict_for_pd)
        
        iii_df.to_pickle("Data/III/" + stock_ticker + ".pkl")
        	
        return iii_df
    
    
    def update_scrape(self, stock_ticker, max_new_pages):
        	#[TODO] add in exception if no file exists
        iii_df_old = pd.read_pickle("Data/III/" + stock_ticker + ".pkl")
        	
        subjects, dates, comments, votes, tags, authors = [], [], [], [], [], []
        
        i = 1 # counter for the pages (probably won't go high)
        j = 0 # counter for the beautiful soup lists
        found_match = False
        while i <= max_new_pages:
            soup = self.scrape_iii_discussion(stock_ticker, str(i))
            
            subjects.extend(self.get_iii_subjects())    
            dates.extend(self.get_iii_dates())
            comments.extend(self.get_iii_comments())
            votes.extend(self.get_iii_votes())
            tags.extend(self.get_iii_tags())
            authors.extend(self.get_iii_authors())
        
            while j  < len(subjects): #[TODO] looking at all subjects, not just specific page
                if subjects[j] == iii_df_old['subject'].iloc[0] \
                and authors[j] == iii_df_old['author'].iloc[0] \
                and dates[j].date() == iii_df_old['date'].iloc[0].date():
                    found_match = True
                    break
                else:
                    j+=1
        
            if found_match == True:
                break
            else:
                print "Not found match on page " + str(i) + ", moving to page " + str(i+1)
                i+=1
        
        
        if j != 0: # if j is 0, then the first match was the first entry i.e. nothing has changed
        
            print "Found a match to old data in the " + str(j) + "th entry on the " + str(i) + "th page." 
            dict_to_concat = {'date' : dates[:j],
                              'tag' : tags[:j],
                              'subject' : subjects[:j],
                              'votes' : votes[:j],
                              'author' : authors[:j],
                              'comment' : comments[:j]}
                             
            iii_df_new = pd.concat((pd.DataFrame(dict_to_concat), iii_df_old))
            iii_df_new.reset_index(drop = True, inplace = True)
            iii_df_new.to_pickle("Data/III/" + stock_ticker + ".pkl")
            return iii_df_new
        
        elif j == 0:
        
            print "No changes need to be made"
            return iii_df_old
    
    	
    def delete_rows_from_df(self, stock_ticker, rows_to_delete):
        ''' This is a testing function. '''
        df = pd.read_pickle("Data/III/" + stock_ticker + ".pkl")
        df2 = df.ix[rows_to_delete:]
        df2.to_pickle("Data/III/" + stock_ticker + ".pkl")
        return df2
    
    
    
    #[TODO] - add print outs so you know where the function is... i.e. initialising
    
x = ScrapeIII("GOOG")
    
    #print soup.prettify()
    
