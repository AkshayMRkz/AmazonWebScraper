"""Takes product reviews from Amazon website, stores them in an Excel sheet, display a pie chart,
 and show emoji based on rating
Usage:
    ./amazonwebscrapper.py

Author:
    Akshay Moorthy - 15th April 2022
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as img
import time


productReviewList = []          #List storing product reviews

"""
 Process product reviews from web data fetched from the web page of given url
 Returns the complete list of product reviews
"""


def fetch_data_from_webpage(url, page_number=1):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/41.0.2228.0 Safari/537.36'}

    if page_number > 1:         #reconstructing url for taking next page
        url += "&pageNumber=" + str(page_number)
    webData = requests.post(url, headers=headers)       #Getting data from web page

    try:
        webData.raise_for_status()      #Checking the status of the request result
        parsedWebData = BeautifulSoup(webData.content, 'html.parser')       #parsing data
        productReviews = parsedWebData.findAll("div", {"class": "a-section review aok-relative"})   #Product reviews
        resultData = fetch_product_reviews(productReviews)  #Obtaing product reviews from the page
        productReviewList.extend(resultData)  #adding it product review list
        if check_for_next_page(parsedWebData):      #Checking if next page exist
            fetch_data_from_webpage(url, page_number + 1)  #Calling same function to process next set data

        return productReviewList
    except Exception as exc:
        print('Error : %s' % exc)


"""
Checks whether there is next page
Returns True if exists
"""


def check_for_next_page(webdata):
    nextButton = webdata.find("li", {"class": "a-disabled a-last"})  #Checking next button is disabled
    if nextButton is None:
        nextButton = webdata.find("li", {"class": "a-last"})      #Checking if enabled next button is there
        if nextButton is not None:
            return True
        else:
            return False
    return False


"""
Converting html data of one page to list of product reviews
Returns the list of product reviews of given page
"""


def fetch_product_reviews(product_reviews):
    productReviewOfEachPage = []
    for review in product_reviews:      #taking each product reviews
        try:
            eachProductReview = BeautifulSoup(review.decode_contents(), 'html.parser')
            customerName = eachProductReview.find("span", {"class": "a-profile-name"}).getText()
            productRatingValue = eachProductReview.find("span", {"class": "a-icon-alt"}).getText()
            productRating = productRatingValue.split("out")  #Taking just teh rating number
            productReview = eachProductReview.find("span", {"class": "a-size-base review-text review-text-content"}
                                                   ).getText()
            singleReviewData = {
                "Name": customerName,
                "Rating": productRating[0].strip(),
                "Message": productReview.strip()
            }

            print("processing data..")
            productReviewOfEachPage.append(singleReviewData)

        except Exception as exc:
            print('An issue occurred during processing: %s' % exc)
    return productReviewOfEachPage


"""
Display an image based on average of the total product rating by the customer
"""


def overall_review(average_review):
    image = ''
    # Checking teh average rating to display the image corresponding to it
    if average_review == 5:
        image = img.imread('images/smiley_smile.jpg')
    elif average_review == 4:
        image = img.imread('images/slight_smile.jpg')
    elif average_review == 3:
        image = img.imread('images/neutral_smiley.jpg')
    else:
        image = img.imread('images/sad_smiley.jpg')

    plt.imshow(image)
    plt.show()  # Displays image


"""
    Plotting a graph based on the ratings given by the customer.
    Pie chart will be displayed
"""


def display_pie_chart_of_reviews(rating_star_list):
    # Dictionary having count of each star ratings of the product and the label to be displayed
    ratingCountData = {'5 Star': rating_star_list.count(5),
                       '4 Star': rating_star_list.count(4),
                       '3 Star': rating_star_list.count(3),
                       '2 Star': rating_star_list.count(2),
                       '1 Star': rating_star_list.count(1)}
    # Taking only non-zero values that other part will be hidden
    labelsForPieChart = [label for label, ratingCount in ratingCountData.items() if ratingCount != 0]
    listOfRatingCount = [ratingCount for ratingCount in ratingCountData.values() if ratingCount != 0]

    # plotting the pie chart
    plt.pie(listOfRatingCount, labels=labelsForPieChart)
    plt.legend(title="Ratings:")
    plt.show()


def main():
    url = username = input("Paste url of all review page of the product:") #getting the url
    fetch_data_from_webpage(url)
    # Creating a dataframe and saving data to an Excel sheet
    dataframeOfReviews = pd.DataFrame(productReviewList)
    # taking rating as float value in a separate column to take average and plotting graph
    dataframeOfReviews['n_rating'] = dataframeOfReviews['Rating'].astype(float)
    dataframeOfReviews.to_excel("productReviewSheet.xlsx") #creates Excel sheet and stores data

    # displaying pie chart
    display_pie_chart_of_reviews(list(dataframeOfReviews['n_rating']))

    # Delaying the display image call to show image after 5 seconds
    print("An image will be displayed based on customer satisfaction")
    time.sleep(5)
    # Displaying image based on total average
    overall_review(dataframeOfReviews['n_rating'].mean())


if __name__ == "__main__":
    main()
