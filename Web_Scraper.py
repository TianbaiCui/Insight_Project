import time
import numpy as np
import pandas as pd
import unicodecsv as csv
from datetime import datetime, timedelta
# imoport packages for web scraping:
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains


def find_end_date(deal_end, description):
    end_day = ''
    end_month = ''
    if deal_end not in description:
        return None
    else:
        i = 0
        while description[description.find(deal_end)+len(deal_end)+i].isdigit():
            end_month += description[description.find(
                deal_end)+len(deal_end)+i]
            i += 1
        i += 1
        while description[description.find(deal_end)+len(deal_end)+i].isdigit():
            end_day += description[description.find(deal_end)+len(deal_end)+i]
            i += 1
            if description.find(deal_end)+len(deal_end)+i == len(description):
                break
        return end_month, end_day


def crawling(url, brand, page_max=100):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)

    master = [['Brand', 'Title', 'Description', 'Posted_date',
               'End_date', 'Comments_count', 'Bookmarks_count', 'Shares_count']]
    page = 0
    while True:

        check_height = driver.execute_script(
            "return document.body.scrollHeight;")
        while True:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            try:
                WebDriverWait(driver, 3).until(lambda driver: driver.execute_script(
                    "return document.body.scrollHeight;") > check_height)
                check_height = driver.execute_script(
                    "return document.body.scrollHeight;")
            except:
                break

        print('Started')
        elements = driver.find_elements_by_class_name('mlist')

        for element in elements:
            temp = [brand]
            deal_id = element.get_attribute('id')  # first find the deal_id

            # ------ find title of deal
            try:
                title = element.find_element_by_class_name("indextitle").text
            except:
                pass

            temp.append(title)

            # ------ find description of deal
            des = element.find_element_by_tag_name('table').text

            for deal_ends in ['Deal ends on ', 'Deal ends ', 'Deal expires ', 'Coupon expires ']:
                if not find_end_date(deal_ends, des):
                    end_month = None
                    end_day = None
                    continue
                else:
                    end_month, end_day = find_end_date(deal_ends, des)
                    try:
                        end_month = int(end_month)
                        end_day = int(end_day)
                        if end_month > 12 or end_day > 31:
                            end_month = None
                            end_day = None
                    except:
                        pass
                    break

            temp.append(des)

            # ------ find time the deal was posted
            try:
                time = element.find_element_by_class_name('pubtime').text
                time = time[0:-4]  # strip away 'Posted' and 'ago'
                post_date = datetime.today()
                if time[-4:] == 'days':
                    post_date -= timedelta(days=int(time[0:-5]))

            except Exception as e:
                print('===TIME NOT FOUND')
                print('===deal skipped')
                continue

            temp.append(post_date.strftime("%m/%d/%Y"))

            # ------ find time the deal was ended

            if end_month and end_day:
                end_date = datetime(post_date.year, end_month, end_day)
                end_date_saved = end_date.strftime("%m/%d/%Y")
            else:
                end_date_saved = ''

            temp.append(end_date_saved)

            # ------ find number of comments for the deal
            num_comments = 0
            try:
                path = '//*[@id=' + '"' + deal_id + \
                    '"' + ']/div[2]/div[3]/div/t[1]/span'
                num_comments = element.find_element_by_xpath(path).text
                # print(num_comments)
            except Exception as e:
                pass

            temp.append(num_comments)

            # ------ find number of bookmarks for the deal
            num_bookmarks = 0
            try:
                path = '//*[@id=' + '"' + deal_id + \
                    '"' + ']/div[2]/div[3]/div/t[2]/span'
                num_bookmarks = element.find_element_by_xpath(path).text
            except Exception as e:
                pass

            temp.append(num_bookmarks)

            # ------ find number of shares for the deal
            num_shares = 0
            try:
                path = '//*[@id=' + '"' + deal_id + \
                    '"' + ']/div[2]/div[3]/div/t[3]/span'
                num_shares = element.find_element_by_xpath(path).text
            except Exception as e:
                pass

            temp.append(num_shares)

            # ------ append to master list
            master.append(temp)

        try:
            load = driver.find_element_by_class_name("next_link")
            page += 4
            print("Finished {} pages".format(page))

            # See if the last page has been reached
            page_num = driver.find_element_by_class_name(
                'pages').find_element_by_class_name('current').text

            if page_num == str(page_max):
                print('Last page reached')
                break
            else:
                load.click()
        except:
            print("===Can't go to the next page")
            break

    return master


def saveCSV(filename, data):
    with open(filename, 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    return
