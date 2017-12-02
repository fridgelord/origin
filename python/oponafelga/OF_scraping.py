# coding: utf-8
# sciaganie danych z oponafelga.pl

############ TODO ###########
## pelny profil
## rozmiar terenowe ??X(?)?.??R??
## rozmiar terenowe ??/(?)?.??R??
## LI wyrzucic nawiasy, 0 na pocz (np. 099/097), XL do XL, SI do SI, wyrzucic puste
## SI wyrzucic nawiasy, LI do LI, ZR(Y) i ZRY -> Y, male litery na duze
## dlaczego nie ma sezonu calorocznych?
## tireType runflat???
## producer duze litery tylko
## RBP wyrzucic -, 2016, C, FR
## RBP TAK, Tak, Rant ochronny -> True
## RPB XL, XL/RF -> XL
## RPB ROF, RF -> runflat
## addFeature RF, RUNFLAT, SSR, ZP - runflat, tak RUNFLAT -> runflat
## XL LISI -> LI + SI
## XL C, C 8PR, DOT out
## XL Osobowe, SUV, Van/Dostawcze > type
## XL RF -> XL
############################

import pandas as pd
import numpy as np
from time import sleep
import re
import datetime
import os
import shutil
# import getpass
import platform

from bs4 import BeautifulSoup
from selenium import webdriver
# from selenium.webdriver.support.ui import Select

def isLISI(string):
    string = string.strip()
    return re.search('\d\d\d?/?\d?\d?\d?\D', string).group(0) == string


hostname = platform.node()
chromePath = shutil.which('chromedriver')
options = webdriver.ChromeOptions()
if hostname == 'user-Vostro-260':
    options.add_argument('headless')
driver = webdriver.Chrome(chromePath, chrome_options=options)


def getproductsFromPage(listaOpon, dzis):

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(2)
    pageSource = driver.page_source

    soup = BeautifulSoup(pageSource, 'html.parser')
    products = soup.findAll(True, {'class': 'boxRight'})
    for prod in products:
        if (1 == 1):
            # prod = str(prod).replace('\n', '')
            try:
                link = re.search('href=\".*(/opona.+?)\"><span class=\"productClass',
                                 str(prod).replace("\n", "")).group(1)
            except:
                print('sprawdz brak linka')
                link = '_n/a'
            try:
                sizeEU = re.search('\"productParams\">(.+?)</span>',
                                   str(prod).replace("\n", "")).group(1)
                brand = re.search('\"productName\">(.+?)<span>',
                                  str(prod).replace("\n", "")).group(1)
                pattern = re.search('\"productName\">(.+?)<span>(.+?)</span>',
                                    str(prod).replace("\n", "")).group(2)
                title = sizeEU+' '+brand+pattern
            except:
                title = '_n/a'
                print('sprawdz brak tytulu')


            try:
                price = re.search('class=\"value\">(.+?) zł<',
                                  str(prod).replace("\n", "")).group(1)
                price = price.replace(chr(160), '')
                price = price.replace(chr(32), '')
                price = price.replace(',', '.')
                price = float(price)
            except:
                price = np.nan
                print("sprawdz brak ceny", link)
            if str(prod).find('Towar dostępny od ręki') != -1:
                delivery='24h'
            else:
                try:
                    delivery = re.search('Czas dostawy (.+?)</span>', str(prod).replace("\n", "")).group(1)
                except:
                    delivery="nieznany"
                    print("sprawdz nowy rodzaj dostawy", link)
            try:
                listaOpon.append([
                    link,
                    title,
                    price,
                    delivery,
                    dzis
                ])
            except:
                print("cos nie tek z dodawaniem do listy", title)
    try:
        try:
            chatElement = driver.find_element_by_name('close')
            if chatElement.get_attribute('title') == 'Zakończyć chat':
                chatElement.click()
        except:
            pass
        element = driver.find_element_by_link_text('następna strona')
        driver.execute_script("arguments[0].scrollIntoView();", element)
        driver.execute_script("window.scrollBy(0,-250)", "")
        # actions = ActionChains(driver)
        # actions.move_to_element(element).perform()
        try:
            nast = element.get_attribute('href')
        except:
            print('no href attr')
        sleep(0.5)
        # element.click()
        # driver.get('https://oponafelga.pl/szukaj/' + nast)
        driver.get(nast)
        sleep(4)
    except:
        return True
    else:
        getproductsFromPage(listaOpon, dzis)



listaOpon = []
now = datetime.datetime.now()
dzis = now.isoformat()[:10]
adresPocz = 'https://oponafelga.pl/szukaj/?marka=&rozmiar=&sezon='
adresKonc = '&pojazd=#results'
sezony = ['zimowe', 'letnie', 'caloroczne']
# sezony = ['caloroczne'] # dev
for i in sezony:
    adres = adresPocz+i+adresKonc
    try:
        driver.get(adres)
    except:
        print("Nie udało się otworzyć adresu", adres)
    sleep(3)
    getproductsFromPage(listaOpon, dzis)

lista_Opon = pd.DataFrame(
    listaOpon, columns=['link', 'title', 'price', 'delivery', 'dateRetrieved'])
sciezka = 'datasets/pricesOF.csv'
if os.path.exists(sciezka):
    lista_Opon.to_csv(sciezka, sep=';', decimal=',', mode='a', header=False)
else:
    lista_Opon.to_csv(sciezka, sep=';', decimal=',')
try:
    sciezka2 = '/mnt/scraping/pricesOF.csv'
    if os.path.exists(sciezka2):
        lista_Opon.to_csv(
            sciezka2, sep=';', decimal=',', mode='a', header=False)
    else:
        lista_Opon.to_csv(sciezka2, sep=';', decimal=',')
except:
    print("Nie udało się zapisac na dysku sieciowym")
driver.quit()
