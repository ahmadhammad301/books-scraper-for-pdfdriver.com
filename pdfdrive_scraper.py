from logging import exception
from time import sleep
import os
from bs4 import BeautifulSoup
import pandas as pd
import requests
import wget
import concurrent.futures
from new_identity import renew_connection


search_url='https://www.pdfdrive.com/search?q={}&pagecount=&pubyear=&searchin=en&em='
base_url='https://www.pdfdrive.com'

proxies = {'http': 'socks5://127.0.0.1:9050'
            ,'https': 'socks5://127.0.0.1:9050'}

def get_urls(url,all_pages=False):
    # input:
    # url: string --> in this format:'https://www.pdfdrive.com/search?q=data+science&pagecount=&pubyear=&searchin=&em='
    # all_pages: bool --> true: get all pages ,False--> get only first 3
    # output: list--> all urls in the search pages
    
    request= requests.get(url+"1")
    soup = BeautifulSoup(request.content,'lxml')
    
    if all_pages:   
        max_page=int(soup.select_one('div.Zebra_Pagination').find_all('a')[-2].text)
        print(max_page)
    else:
        max_page=3
    
    print("getting links from page:  1")
    links=[]
    #scrape the first searct page and gather book links
    for ul in soup.find_all('ul')[1].find_all('li'):
        links.append(base_url+ul.find('a').attrs['href'])
        
    # scrape each other page    
    for page_num in range(2,max_page+1):
        
        request= requests.get(url+str(page_num))
        soup = BeautifulSoup(request.content,'lxml')
        
        print("getting links from page: ",page_num)
        for ul in soup.find_all('ul')[1].find_all('li'):
            links.append(base_url+ul.find('a').attrs['href'])
    print('number of book_urls',len(links))
    return links



def get_books_Details(book_url_list):
    booksFinalUrls=[]
    for idx,url in enumerate(book_url_list):
        try:
            request= requests.get(url) 
        except Exception as e:
            print(f' ConnectionResetError{str(e)}')
            #renew_connection()
            session = requests.session()
            session.proxies = proxies
            request= session.get(url)    

        book_soup=BeautifulSoup(request.content,'lxml') # make the soup from selenium driver

        # print("exception occured",e)
        title_ = book_soup.find('h1').text.strip()
        try:
            l=book_soup.find(class_='ebook-buttons').find('button').attrs['data-preview']
            download_url=base_url+'/download.pdf?'+l.split('session=')[0].split('?')[1]+'h='+l.split('session=')[1]+'&u=cache&ext=pdf'
        except Exception:
            download_url='not found'
        
        book_details=dict(
                title = title_,
                book_page_url = url,
                download_url = download_url
            )
        print("book url in pdf:  ",download_url)
        
        booksFinalUrls.append(book_details)
    
    return booksFinalUrls

def download_book(download_Details):
    book_name = download_Details[0].replace(':',u'\uff1a')
    full_path = "savedBooks"+"/"+book_name+".pdf"
    path= "savedBooks"
    if download_Details[1] == 'not found ':
        print('book has no download url')
    else:
        full_path
        if not os.path.exists(path):
            os.makedirs(path)

        if  os.path.exists(full_path):
            print('book exists')
        else:
            wget.download(download_Details[1], "{}".format(full_path))
        print(full_path)

def Main():
    skill = input("Enter the skill: ")
    skill = skill.replace(" ","%20")
    url = search_url.format(skill)
    all_book_urls=[]
    all_book_urls = get_urls(url)
    
    books=[]

    books=get_books_Details(all_book_urls)
    
    #saving in an excel file 
    file=pd.DataFrame(books) 
    file.drop_duplicates(inplace=True)
    
    skill=skill.replace("%20",' ')+' books'
    file.to_excel('{}.xlsx'.format(skill),index=False,encoding='utf-8-sig')
    print('excel file saved')
    
    # downloading books
    #resource https://docs.python.org/3/library/concurrent.futures.html
    book_index =[i for i in range(len(file))]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results =concurrent.futures.wait([executor.submit(download_book, [file['title'][index],file['download_url'][index]]) for index in book_index])
    print('books downloaded')



if __name__=="__main__":

    Main()