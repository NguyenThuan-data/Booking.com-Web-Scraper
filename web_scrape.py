# This app scrape data from booking.com

# import libraries
import requests
### This library's job is to act like a web browser. It sends an HTTP 
### request to a URL and fetches the raw HTML source code of the webpage for you. It's the first step in any web scraping process.
from bs4 import BeautifulSoup ### This lib having function and features that support web scraping
### it get the raw html from 'requests' and turn into something structured and searchable/
import lxml ### act like a high-performance parser for BeautifulSoup
import csv
import time


def web_scraper(web_url, file_name):

    # Greeting and Add delay
    print('Hi welcome to the show!\nStart now!')
    time.sleep(5)

    # add user-browser information, this is the most common browser that users use to access the link
    header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'}

    res = requests.get(web_url, headers=header)


    if res.status_code == 200:### 200 is stadard HTTP status code for 'OK' or 'success'
        print("Connect to the Website successfully")
        html_cont = res.text

        # creating soup
        soup = BeautifulSoup(html_cont, 'lxml')

        # list of all hotels
        hotel_divs=soup.find_all('div', role = "listitem")

        # record scraped information to csv file
        with open(f'{file_name}.csv','w') as file_csv:
            writer = csv.writer(file_csv)

            # adding header
            writer.writerow(['Hotel Name', 'Location', 'Price', 'Rating', 'Score', 'Review','Link'])

            # access each hotel information
            for hotel in hotel_divs:
                hotel_name = hotel.find('div', class_="b87c397a13 a3e0b4ffd1").text.strip()

                hotel_location = hotel.find('span',class_="d823fbbeed f9b3563dd4").text.strip()

                # price
                price = hotel.find('span',class_="b87c397a13 f2f358d1de ab607752a2").text.strip().replace('NZD ','')
                # review
                hotel_review = hotel.find('div',class_="fff1944c52 fb14de7f14 eaa8455879")
                # rating and score
                hotel_rating = hotel.find('div',class_="f63b14ab7a f546354b44 becbee2f63")
                hotel_score = hotel.find('div',class_="f63b14ab7a dff2e52086")
                if hotel_review:
                    # This code only runs if there was review
                    review = hotel_review.text.strip()
                    rating = hotel_rating.text.strip()
                    score = hotel_score.text.strip()
                else:
                    # This code runs if the hotel is new and have no review yet
                    rating = "New to Booking.com" 
                    score = "New to Booking.com"

                # getting the link
                link = hotel.find('a', href = True).get('href')

                # record the information to the file
                writer.writerow([hotel_name, hotel_location, price, rating, score, review, link])
    else:
        print(f"Connection failed!{res.status_code}")
    
# if using this script directly then the code below will be executed
### The code below is allow user to run directly but also allow others to import it as a module into other scripts
### if run directly, Python automatically sets the __name__ variable for that script to the special value __main__.
if __name__=='__main__':## to compare if __name__ = __main__, which mean checking if the scripts is run directly
    # get the url and file name from users

    web_url = input("Please enter URL: ")
    file_name = input("please enter the stored file's name: ")
        
    # calling the function
    web_scraper(web_url, file_name)
