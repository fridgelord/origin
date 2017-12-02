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

def err(gdzie, dla_czego=''):
    print('BLAD', sys.exc_info(), 'W DZIALANIU', gdzie,
          ('DLA', dla_czego) if dla_czego != '' else '')


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
                prodClass = re.search('\"productClass\">(.+?)</span>',
                                  str(prod).replace("\n", "")).group(1)
                klasy = {
                    'Klasa ekonomiczna': 'budget', 
                    'Klasa średnia': 'medium', 
                    'Klasa premium': 'premium',
                    'Klasa ': '_n/a'
                }
                klasa = klasy[prodClass]
            except:
                print('sprawdz brak klasy', link)
                print(sys.exc_info())
                klasa = '_n/a'
            etykiety = prod.findAll(True, {'class': 'lineInfo'})
            etykiety = str(etykiety).replace('\n', '')
            try:
                RR = re.search('1s\.png" style=\"height:18px;\"/>(.+?)<',
                               etykiety).group(1).strip()
            except:
                print('blad wyszukania RR dla', link, sys.exc_info())
                RR = '_n/a'
            try:
                WG = re.search('2s\.png" style=\"height:18px;\"/>(.+?)<', 
                               etykiety).group(1).strip()
            except:
                print('blad wyszukania WG dla', link, sys.exc_info())
                WG = '_n/a'
            try:
                dB = re.search('3s\.gif\" style=\"height:18px;\"/>\s*(\d{0,2}|-*)\s.*<',
                               etykiety).group(1).strip()
                dB = '_n/a' if dB == '-'
            except:
                print('blad wyszukania dB dla', link, sys.exc_info())
                dB = '_n/a'


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
# sezony = ['zimowe', 'letnie', 'caloroczne'] 
sezony = ['caloroczne'] # dev
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
driver.quit() # dev



try:
    biezacaBazaOpon = pd.read_csv(
        'datasets/tireDataOF.csv', dtype='str', header=0, sep=';', usecols=[1])
    biezacaBazaOpon = biezacaBazaOpon['link'].values.tolist()
except:
    biezacaBazaOpon = []
    print ('brak bazy opon, tworze nowa')
daneOpon = []
# for referencja in [['/opona/vredestein_quatrac_5_59371.html']]:
for referencja in listaOpon:
    odnosnik = referencja[0]
    if odnosnik not in biezacaBazaOpon:
        try:
            adres = 'https://oponafelga.pl' + odnosnik
            driver.get(adres)
            sleep(2)
        except:
            print("Nie udało się otworzyć strony dla", adres)
            continue
        pageSource = driver.page_source
        soup = BeautifulSoup(pageSource, 'html.parser')
        table = soup.find('table', attrs={'class':'produkt'})
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        tempList = []
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            tempList.append(cols)
        for i in [6, 5, 3, 2, 0]:
            tempList.pop(i)
        producent = tempList[0][0]
        bieznik = tempList[0][1]
        sezon = tempList[0][2].lower()
        if sezon == 'letnie':
            sezon = 'summer'
        elif sezon == 'zimowe':
            sezon = 'winter'
        elif sezon == 'caloroczne':
            sezon = 'allseason'
        else:
            print('Sprawdz nowy rodzaj sezonu dla', adres)
            sezon = '_n/a'
        przeznaczenie = tempList[0][3]
        if przeznaczenie == 'osobowy':
            przeznaczenie = 'CAR'
        elif przeznaczenie == 'dostawczy':
            przeznaczenie = 'LTR'
        elif przeznaczenie == '4x4':
            przeznaczenie = 'SUV/4x4'
        else:
            print('Sprawdz nowy rodzaj przeznaczenia dla', adres)
            przeznaczenie = '_n/a'
        rozmiar = tempList[1][0].replace('C','')
        try:
            LI = re.search('(.+?) \(do', tempList[1][1]).group(1)
        except:
            print('sprawdz brak LI dla', adres)
            LI = ''
        try:
            SI = re.search('(.+?) \(do', tempList[1][2]).group(1)
        except:
            print('sprawdz brak SI dla', adres)
            SI = ''
        XL = tempList[1][3]
        rant = tempList[2][0]
        homol = tempList[2][1]
        cecha = tempList[2][2]
        prod_kod = tempList[2][3]

        szer = rozmiar
        profil = ''
        osadzenie = ''
        zastosowanie = ''
        RR = ''
        WG = ''
        dB = ''
        noise = ''
        EAN = ''
        indeks = ''
        runflat = ''
        DOT = ''
        klasa = ''



        daneOpon.append([
            odnosnik, szer, profil, osadzenie, LI, SI, sezon, bieznik,
            zastosowanie, przeznaczenie, RR, WG, dB, noise, producent,
            prod_kod, EAN, indeks, rant, runflat, cecha, XL, DOT, klasa, dzis
        ])

driver.quit()

dane_opon = pd.DataFrame(
    daneOpon,
    columns=[
        'link', 'width', 'profile', 'seat', 'LI', 'SI', 'season', 'pattern',
        'application', 'tireType', 'RR', 'WG', 'dB', 'noise', 'producer',
        'manuf_code', 'EAN', 'ICindex', 'RBP', 'ROF', 'addFeature', 'XL',
        'DOT', 'tier', 'dateRetrieved'
    ])

def zapiszDfDoCsv(dataFr, sciezka):
    if os.path.exists(sciezka):
        dataFr.to_csv(sciezka, sep=';', decimal=',', mode='a', header=False)
    else:
        dataFr.to_csv(sciezka, sep=';', decimal=',')

sciezka = 'datasets/tireDataOF.csv'
sciezkaNewTires = 'datasets/tireDataOF.csv'
sciezkaRemote = '/mnt/scraping/tireDataOF.csv'
sciezkaRemoteNewTires = '/mnt/scraping/tireDataOF.csv'
listaSciezek = [sciezka, sciezkaNewTires, sciezkaRemote, sciezkaNewTires]
for i in listaSciezek:
    try:
        zapiszDfDoCsv(dane_opon, i)
    except:
        print("Nie udalo sie zapisac w", i)

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
