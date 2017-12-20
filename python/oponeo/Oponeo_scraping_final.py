import pandas as pd
import numpy as np
from time import sleep
import re
import datetime
import os
import platform
import shutil
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains


hostname = platform.node()
chromePath = shutil.which('chromedriver')
options = webdriver.ChromeOptions()
if hostname == 'user-Vostro-260':
    options.add_argument('headless')
    options.add_argument('window-size=1200x600')
driver = webdriver.Chrome(chromePath, chrome_options=options)

def err(gdzie, dla_czego=''):
    print('BLAD', sys.exc_info(), 'W DZIALANIU', gdzie,
          ('DLA', dla_czego) if dla_czego != '' else '')

SIdict = {'M': 'T'
          ,'J': 'T'
          ,'K': 'T'
          ,'L': 'T'
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
          ,'ZR': 'Y'
          ,'Z': 'Z'
          ,'': '_n/a'
          ,'_n/a': '_n/a'
         }



def widthProfileSeatFromSize(rozmiar: str):
    ''' return a list with width, profile and size when given size '''
    rozmiar = rozmiar.replace(' ','')
    szer = re.search('([0-9][\.]?[0-9][0-9]?)[/Xx]?.*?[Rr][0-9]', rozmiar).group(1)
    profil = re.search('[0-9]{2}[0-9]?[/Xx]?(.*)[Rr][0-9]', rozmiar).group(1)
    if profil == '' or profil == '82':
        profil = '80'
    osadzenie = re.search('.*[Rr]([0-9]{2})', rozmiar).group(1)
    return szer, profil, osadzenie


def zapisz(df, sciezka):
    try:
        if os.path.exists(sciezka):
            df.to_csv(sciezka,mode='a',header=False,sep=';',decimal=',')
        else:
            df.to_csv(sciezka,sep=';',decimal=',')
    except:
        print('nie udalo sie zapisac w', sciezka)


def getproductsFromPage(pricesOpList,dzis,tireDataOpList):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(2)
    pageSource = driver.page_source

    soup = BeautifulSoup(pageSource, 'html.parser')
    products = soup.findAll(True, {'class': 'product'})
    for prod in products:
        if('class="productName"' in str(prod)):
            try:
                title = re.search('(?<=\" title=\")(.*?)(?=\">)', str(prod).replace("\n", "")).group(0)
            except:
                title = '_n/a'
            try:
                stock = int(re.search('\d+',re.search('(?<=class=\"stockLevel\">)(.*?)(?=w mag)', str(prod).replace("\n", "")).group(0)).group(0))
            except:
                stock=0
            runFlat=False
            if str(prod).find('Run Flat') != -1:
                runFlat=True
            try:
                LI = re.search('(?<=Indeks nośności )(.*?)(?= – maksymalne)', str(prod).replace("\n", "")).group(0)
            except:
                LI = '_n/a'
            try:
                LIeu = re.search('^(\d?\d\d)/?\d?', LI).group(1)
            except:
                LIeu = ''
            try:
                SI = re.search('(?<=Indeks prędkości )(.*?)(?= – maksymalna)', str(prod).replace("\n", "")).group(0)
            except:
                SI = '_n/a'
            try:
                SIeu = SIdict[SI]
            except:
                SIeu = ''
            if str(prod).find('<span class="tooltip">Opona letnia z homologacją zimową.</span>') != -1:
                season="allseason"
            elif str(prod).find('<span class="tooltip">Opona na sezon letni.</span>') != -1:
                season="summer"
            elif str(prod).find('<span class="tooltip">Opona na sezon zimowy.</span>') != -1:
                season="winter"
            elif str(prod).find('<span class="tooltip">Opona całoroczna.</span>') != -1:
                season="allseason"
            else:
                season="nieznany"
                print("sprawdz nowy rodzaj sezonu", title)
            if str(prod).find('<strong>24h</strong>') != -1:
                delivery='24h'
            elif str(prod).find('<strong>już jutro!</strong>') != -1:
                delivery='24h'
            elif str(prod).find('Zapytaj o termin dostawy') != -1:
                delivery='ask'
            elif str(prod).find('Doręczymy') != -1:
                delivery=re.search('(?<=Doręczymy  <strong>).*?(?=<\/strong>)', str(prod).replace("\n", "")).group(0)
            elif str(prod).find('dzień roboczy') != -1:
                delivery=re.search('(?<=<strong>).*? dzień roboczy(?=.*?<\/strong>)', str(prod).replace("\n", "")).group(0)
            elif str(prod).find('dni robocz') != -1:
                try:
                    delivery=re.search('(?<=<strong class=\"\">).*? dni robocz(?=.*?<\/strong>)', str(prod).replace("\n", "")).group(0)
                except:
                    delivery=re.search('(?<=<strong>).*? dni robocz(?=.*?<\/strong>)', str(prod).replace("\n", "")).group(0)
            elif str(prod).find('<strong class=" futureSupply">') != -1:
                delivery=re.search('(?<=<strong class=\" futureSupply\">).*?(?=<\/strong>)', str(prod).replace("\n", "")).group(0)
            else:
                delivery="nieznany"
                print("sprawdz nowy rodzaj dostawy", title)
            try:
                price = re.search('(?<=<span class=\"price size-[0-9]\">)(.*?)(?=</span>)', str(prod).replace("\n", "")).group(0)
                price = price.replace(chr(160),'')
                price = int(price)
            except:
                price = np.nan
                print("sprawdz brak ceny", title)
            try:
                link = re.search('(?<=<a href=\")(.*?)(?=\" title)', str(prod).replace("\n", "")).group(0)
            except:
                link = '_n/a'
                print("sprawdz brak linka", title)
            try:
                producer = re.search('(?<=<span class=\"producer\">)(.*?)(?=</span>)', str(prod).replace("\n", "")).group(0)
            except:
                producer = '_n/a'
                print("sprawdz brak producenta", title)
            try:
                model = re.search('(?<=<span class=\"model\">)(.*?)(?=</span>)', str(prod).replace("\n", "")).group(0)
            except:
                model = '_n/a'
                print("sprawdz brak modelu", title)
            try:
                size = re.search('(?<=<span class=\"size\">)(.*?)(?=</span>)', str(prod).replace("\n", "")).group(0)
            except:
                size = '_n/a'
                print("sprawdz brak rozmiaru", title)
            width, profile, seat = widthProfileSeatFromSize(size)
            if str(prod).find('div class=\"dot\"') == -1:
                DOT = ''
            else:
                try:
                    DOT = re.search('div class=\"dot\">\s*?Produkcja\s(\d+?/?\d*?)\s*?<', str(prod).replace('\n', '')).group(1)
                except:
                    try:
                        DOT = re.search('div class=\"dot\">(.*?)<', str(prod).replace('\n', '')).group(1)
                        if DOT.strip() != '':
                            print('sprawdz inny format dotu:', DOT, link)
                            raise
                    except:
                        pass
                DOT = ''
            try:
                country = re.search('span class=\"country\">(.*?)</span>', str(prod).replace('\n', '')).group(1)
            except:
                country = ''
            try:
                RR = re.search('span class=\"icon-fuel\">'+
                               '\s*</span>\s*<em>\s*(\w)\s*<span>',
                               str(prod)).group(1)
            except:
                # print('brak RR', link)
                RR = '_n/a'
            try:
                WG = re.search('span class=\"icon-rain\">'+
                               '\s*</span>\s*<em>\s*(\w)\s*<span>',
                               str(prod)).group(1)
            except:
                # print('brak WG', link)
                WG = '_n/a'
            try:
                dB = re.search('<span class=\"icon-noise\">'+
                               '\s*</span>\s*<em>\s*(\d\d)dB\s*?</em>',
                               str(prod)).group(1)
            except:
                # print('brak dB', link)
                dB = '_n/a'
            if str(prod).find('<em>XL</em>') != -1:
                XL = True
            else:
                XL = False
            application = '_n/a'
            tireType = '_n/a'
            manuf_code = '_n/a'
            EAN = '_n/a'
            ICindex = '_n/a'
            RBP = '_n/a'
            addFeature = '_n/a'
            tier = '_n/a'
            noise = '_n/a'

            try:
                pricesOpList.append([link,
                                title,
                                price,
                                delivery,
                                stock,
                                dzis
                                ])
                tireDataOpList.append([
                                link,
                                width,
                                profile,
                                seat,
                                LI,
                                LIeu,
                                SI,
                                SIeu,
                                season,
                                model,
                                application,
                                tireType,
                                RR,
                                WG,
                                dB,
                                noise,
                                producer,
                                manuf_code,
                                EAN,
                                ICindex,
                                RBP,
                                runFlat,
                                addFeature,
                                XL,
                                DOT,
                                tier,
                                country,
                                dzis
                ])
            except:
                err('dodawanie do listy', link)
    try:
        try:
            close = driver.find_elements_by_xpath("//*[contains(text(), 'Zamknij i nie pokazuj')]")[0]
            close.click()
        except:
            pass
        element = driver.find_element_by_id("_ctPgrp_pgtnni")
        driver.execute_script("arguments[0].scrollIntoView();", element)
        driver.execute_script("window.scrollBy(0,-250)", "")
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        sleep(0.5)
        element.click()
        sleep(4)
    except:
        return True
    else:
        getproductsFromPage(pricesOpList,dzis,tireDataOpList)


def getproductsFromPage1(pricesOpList,rozmiar,dzis,rozmiarySpecjalne,tireDataOpList):
    rozmiar1=rozmiar[1]+'-'+rozmiar[2]+'-r'+rozmiar[3]
    rozmiar1=rozmiar1.replace('.','-')
    if rozmiar1 in rozmiarySpecjalne:
        rozmiar1 = rozmiarySpecjalne[rozmiar1]
    adres='http://www.oponeo.pl/wybierz-opony/r=1/'+rozmiar1
    try:
        driver.get(adres)
    except:
        print("Nie udało się otworzyć strony dla", rozmiar)
    sleep(3)
    try:
        szer=Select(driver.find_element_by_id("_ctTS_ddlDimWidth")).all_selected_options[0].text
    except:
        print("nie udalo sie sprawdzic szer dla", rozmiar)
        raise
    else:
        if szer != rozmiar[1]: 
            print("rozmiar", rozmiar, "niepoprawny")
            raise
    try:
        driver.find_element_by_id("_ctTS_inpPF").clear()
        driver.find_element_by_id("_ctTS_inpPF").send_keys("0" + "\n")
    except:
        print("Nie udało się wpisać min ceny dla", rozmiar)
    sleep(3)
    try:
        driver.find_element_by_id("_ctTS_inpPT").clear()
        driver.find_element_by_id("_ctTS_inpPT").send_keys("100000" + "\n")
    except:
        print("Nie udało się wpisać max ceny dla", rozmiar)
    sleep(3)
    getproductsFromPage(pricesOpList,dzis,tireDataOpList)



pricesOpList = []
tireDataOpList = []
now = datetime.datetime.now()
dzis = now.isoformat()[:10]
rozmiaryOpon = pd.read_csv('datasets/typy_opon.csv',dtype='str')
rozmiarySpecjalne = pd.read_csv('datasets/rozmiary_specjalne.csv',dtype='str',header=None)
rozmiarySpecjalne = dict(rozmiarySpecjalne.values)
rozmiaryOpon1 = rozmiaryOpon.values.tolist()
#rozmiaryOpon1 = [['0','195','55','16'],['1','255','50','18']] #test
# rozmiaryOpon1 = [['1','125','80','12']] #test
# rozmiaryOpon1 = [['1','135','70','15']] #test
# rozmiaryOpon1 = [['0','33','13.50','16']] #test
for i in rozmiaryOpon1:
    if '__OTHER__' not in i:
        try:
            getproductsFromPage1(pricesOpList,i,dzis,rozmiarySpecjalne,tireDataOpList)
        except:
            print("Nie udało się pobrać danych dla", i)


driver.quit()
pricesOp = pd.DataFrame(pricesOpList,
                        columns=['link', 'title', 'price,'
                                 , 'delivery', 'stock', 'dateRetrieved'])
tireDataOp = pd.DataFrame(tireDataOpList
                          , columns=['link', 'width', 'profile'
                                     , 'seat','LI','LIeu','SI','SIeu','season'
                                     , 'model', 'application','tireType'
                                     , 'RR','WG','dB','noise','producer'
                                     ,'manuf_code','EAN','ICindex','RBP'
                                     ,'runFlat','addFeature','XL','DOT'
                                     ,'tier','country','dateRetrieved'])

sciezka='datasets/pricesOp.csv'
sciezka2='/mnt/scraping/pricesOp.csv'
sciezka3='datasets/tireDataOp.csv'
sciezka4='/mnt/scraping/tireDataOp.csv'

zapisz(pricesOp, sciezka)
zapisz(pricesOp, sciezka2)
zapisz(tireDataOp, sciezka3)
zapisz(tireDataOp, sciezka4)
