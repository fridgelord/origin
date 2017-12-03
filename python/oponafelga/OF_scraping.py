# coding: utf-8
# sciaganie danych z oponafelga.pl

############ TODO ###########
## sprawdzic wszystko
## SI wyrzucic nawiasy, LI do LI, ZR(Y) i ZRY -> Y, male litery na duze
## dlaczego nie ma sezonu calorocznych?
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
import sys

from bs4 import BeautifulSoup
from selenium import webdriver
# from selenium.webdriver.support.ui import Select

def isLISI(string):
    string = string.strip()
    return re.search('\d\d\d?/?\d?\d?\d?\D', string).group(0) == string

def err(gdzie, dla_czego=''):
    print('BLAD', sys.exc_info(), 'W DZIALANIU', gdzie,
          ('DLA', dla_czego) if dla_czego != '' else '')

SIdict = {'M': 'T'
          ,'N': 'T'
          ,'O': 'T'
          ,'P': 'T'
          ,'Q': 'T'
          ,'R': 'T'
          ,'S': 'T'
          ,'T': 'T'
          ,'U': 'H'
          ,'H': 'H'
          ,'V': 'V'
          ,'W': 'W'
          ,'Y': 'Y'
          ,'Z': 'Z'
         }


hostname = platform.node()
chromePath = shutil.which('chromedriver')
options = webdriver.ChromeOptions()
# check if running on headless machine at work
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
                brand = brand.upper()
                pattern = re.search('\"productName\">(.+?)<span>(.+?)</span>',
                                    str(prod).replace("\n", "")).group(2)
                title = sizeEU + ' ' + brand + pattern
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
                if dB == '-':
                    dB = '_n/a'
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
                    link, #0
                    title, #1
                    price, #2
                    delivery, #3
                    dzis #4
                    , klasa #5
                    , sizeEU #6
                    , brand #7
                    , pattern #8
                    , RR #9
                    , WG #10
                    , dB #11 
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

kolumnyDoPozniejszegoUzycia = [5,6,7,8,9,10,11]
lista_Opon = pd.DataFrame(
    listaOpon, columns=[
        'link', 
        'title', 
        'price', 
        'delivery', 
        'dateRetrieved',
    ] + kolumnyDoPozniejszegoUzycia]
    
lista_Opon.drop(lista_Opon.columns[kolumnyDoPozniejszegoUzycia], axis=1, inplace=True)
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
# driver.quit() # dev



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
        producent = tempList[0][0].upper()
        bieznik = tempList[0][1]
        sezon = tempList[0][2].lower()
        przeznaczenie = tempList[0][3]
        rozmiar = tempList[1][0].replace('C','')
        XLtemp = tempList[1][3].upper()
        rantTemp = tempList[2][0].upper()
        homol = tempList[2][1]
        dodInfo = tempList[2][2].upper()
        prod_kod = tempList[2][3]
        LItemp = tempList[1][1].upper()
        SItemp = tempList[1][2].upper()
        
        XL = False
        runflat = False
        rant = False

        if sezon == 'letnie':
            sezon = 'summer'
        elif sezon == 'zimowe':
            sezon = 'winter'
        elif sezon == 'caloroczne ':
            sezon = 'allseason'
        else:
            print('Sprawdz nowy rodzaj sezonu dla', adres)
            sezon = '_n/a'
        if LItemp == '':
            LI = '_n/a'
        elif LI == 'XL':
            XL = True
            LI = '_n/a'
        else:
            try:
                LI = re.search('^\(?0?(\d+)\D', LItemp ).group(1)
            except:
                print('sprawdz brak LI dla', adres)
                LI = '_n/a'
        try:
            SI = re.search('(.+?) \(do', tempList[1][2]).group(1)
        except:
            try:
                SI = re.search('\d\d([a-zA-Z])', SItemp).group(1)
            except:
                try:
                    SI = re.search('\d\d([a-zA-Z])', LItemp).group(1)
                except:
                    print('sprawdz brak SI dla', adres)
                    SI = '_n/a'
        if XLtemp in ['XL', 'RF']:
            XL = True
        elif XLtemp == '':
            XL = False
        elif XLtemp in ['OSOBOWE', 'SUV', 'VAN/DOSTAWCZE']:
            przeznaczenie = XL
            XL = False
        elif XLtemp in ['C', 'C 8PR', 'DOT']:
            XL = False
        elif isLISI(XLtemp):
            LI = XLtemp[:-2]
            SI = XLtemp[-1]
        else:
            print('sprawdz nowy XL dla', adres)
            XL = False
        if przeznaczenie == 'osobowy':
            przeznaczenie = 'CAR'
        elif przeznaczenie == 'dostawczy':
            przeznaczenie = 'LTR'
        elif przeznaczenie == '4x4':
            przeznaczenie = 'SUV/4x4'
        elif przeznaczenie == 'runflat':
            runflat = True
            przeznaczenie = '_n/a'
        else:
            print('Sprawdz nowy rodzaj przeznaczenia dla', adres)
            przeznaczenie = '_n/a'
        if rantTemp in ['TAK', 'RANT OCHRONNY']:
            rant = True
        elif rantTemp in ['-', '2016', 'C', 'FR']:
            pass
        elif rantTemp in ['XL', 'XL/RF']:
            XL = True
        elif rantTemp in ['ROF', 'RF']:
            runflat = True
        else:
            print('Sprawdz nowy rodzaj rantu dla', adres)


        szer = re.search('[0-9]{2}[0-9]?[/Xx]?(.*)[Rr][0-9]', rozmiar).group(1) 
        profil = re.search('[0-9]{2}[0-9]?[/Xx]?(.*)[Rr][0-9]', rozmiar).group(1)
        if profil == '' or profil == '82':
            profil = '80'
        osadzenie = re.search('.*[Rr]([0-9]{2})', rozmiar).group(1)
        if dodInfo in ['RUNFLAT', 'ZP - runflat', 'SSR']:
            runflat = True
            dodInfo = ''
        zastosowanie = ''
        RR = referencja[9]
        WG = referencja[10]
        dB = referencja[11]
        noise = ''
        EAN = ''
        indeks = ''
        DOT = ''
        klasa = referencja[5]



        daneOpon.append([
            odnosnik, szer, profil, osadzenie, LI, SI, sezon, bieznik,
            zastosowanie, przeznaczenie, RR, WG, dB, noise, producent,
            prod_kod, EAN, indeks, rant, runflat, dodInfo, XL, DOT, klasa, dzis
            , LItemp, SItemp, rantTemp, referencja[6]
        ])

driver.quit()

dane_opon = pd.DataFrame(
    daneOpon,
    columns=[
        'link', 'width', 'profile', 'seat', 'LI', 'SI', 'season', 'pattern',
        'application', 'tireType', 'RR', 'WG', 'dB', 'noise', 'producer',
        'manuf_code', 'EAN', 'ICindex', 'RBP', 'ROF', 'addFeature', 'XL',
        'DOT', 'tier', 'dateRetrieved'
        , 'LItemp', 'SItemp', 'rantTemp', 'sizeEU'
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
