import pandas as pd
import numpy as np
from time import sleep
import re
import datetime
import os
import platform
import shutil
# import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
import logging


cur_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(cur_path)

logging.getLogger(__name__)
logging.basicConfig(
                    level=logging.INFO
                    , format='%(name)s|%(levelname)s|%(asctime)s|%(message)s'
                    , datefmt='%Y-%m-%d %H:%M'
                    # , logger = __name__
                   )


logging.info('starting')


hostname = platform.node()
chromePath = shutil.which('chromedriver')
options = webdriver.ChromeOptions()
if hostname == 'user-Vostro-260':
    options.add_argument('headless')
    options.add_argument('window-size=1200x600')
driver = webdriver.Chrome(chromePath, chrome_options=options)


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
        logging.warning('nie udalo sie zapisac w', sciezka)


def getproductsFromPage(pricesOpList,dzis,tireDataOpList,biezacaBazaOpon):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(2)
    pageSource = driver.page_source

    soup = BeautifulSoup(pageSource, 'html.parser')
    products = soup.findAll(True, {'class': 'product'})
    for prod in products:
        prod = str(prod).replace('\n', '')
        if('class="productName"' in prod):
            try:
                title = re.search('(?<=\" title=\")(.*?)(?=\">)', prod).group(0)
            except:
                title = '_n/a'
            try:
                link = re.search('(?<=<a href=\")(.*?)(?=\" title)', prod).group(0)
            except:
                link = '_n/a'
                logging.error('sprawdz brak linka {}'.format(title))
                raise
            try:
                stock = int(re.search('\d+',re.search('(?<=class=\"stockLevel\">)(.*?)(?=w mag)', prod).group(0)).group(0))
            except:
                stock=0
            runFlat = 'Run Flat' in prod
            try:
                LI = re.search('(?<=Indeks nośności )(.*?)(?= – maksymalne)', prod).group(0)
            except:
                LI = '_n/a'
            try:
                LIeu = re.search('^(\d?\d\d)/?\d?', LI).group(1)
            except:
                LIeu = ''
            try:
                SI = re.search('(?<=Indeks prędkości )(.*?)(?= – maksymalna)', prod).group(0)
            except:
                SI = '_n/a'
            try:
                SIeu = SIdict[SI]
            except:
                logging.error('brak {} w slowniku SI dla {}'.format(SI, link))
                SIeu = ''
            if prod.find('<span class="tooltip">Opona letnia z homologacją zimową.</span>') != -1:
                season="allseason"
            elif prod.find('<span class="tooltip">Opona na sezon letni.</span>') != -1:
                season="summer"
            elif prod.find('<span class="tooltip">Opona na sezon zimowy.</span>') != -1:
                season="winter"
            elif prod.find('<span class="tooltip">Opona całoroczna.</span>') != -1:
                season="allseason"
            else:
                season="nieznany"
                logging.warning('sprawdz nowy rodzaj sezonu dla {}'.format(link))
            if prod.find('<strong>24h</strong>') != -1:
                delivery='24h'
            elif prod.find('<strong>już jutro!</strong>') != -1:
                delivery='24h'
            elif prod.find('Zapytaj o termin dostawy') != -1:
                delivery='ask'
            elif prod.find('Doręczymy') != -1:
                delivery=re.search('(?<=Doręczymy  <strong>).*?(?=<\/strong>)', prod).group(0)
            elif prod.find('dzień roboczy') != -1:
                delivery=re.search('(?<=<strong>).*? dzień roboczy(?=.*?<\/strong>)', prod).group(0)
            elif prod.find('dni robocz') != -1:
                try:
                    delivery=re.search('(?<=<strong class=\"\">).*? dni robocz(?=.*?<\/strong>)', prod).group(0)
                except:
                    delivery=re.search('(?<=<strong>).*? dni robocz(?=.*?<\/strong>)', prod).group(0)
            elif prod.find('<strong class=" futureSupply">') != -1:
                delivery=re.search('(?<=<strong class=\" futureSupply\">).*?(?=<\/strong>)', prod).group(0)
            else:
                delivery="nieznany"
                logging.warning('sprawdz nowy rodzaj dostawy dla {}'.format(link))
            try:
                price = re.search('(?<=<span class=\"price size-[0-9]\">)(.*?)(?=</span>)', prod).group(0)
                price = price.replace(chr(160),'')
                price = int(price)
            except:
                price = np.nan
                logging.error('sprawdz brak ceny dla {}'.format(link))
            try:
                producer = re.search('(?<=<span class=\"producer\">)(.*?)(?=</span>)', prod).group(0)
            except:
                producer = '_n/a'
                logging.warning('sprawdz brak producenta dla {}'.format(link))
            try:
                model = re.search('(?<=<span class=\"model\">)(.*?)(?=</span>)', prod).group(0)
            except:
                model = '_n/a'
                logging.warning('sprawdz brak modelu dla {}'.format(link))
            try:
                size = re.search('(?<=<span class=\"size\">)(.*?)(?=</span>)', prod).group(0)
            except:
                size = '_n/a'
                logging.warning('sprawdz brak rozmiaru dostawy dla {}'.format(link))
            width, profile, seat = widthProfileSeatFromSize(size)
            if prod.find('div class=\"dot\"') == -1:
                DOT = ''
            else:
                try:
                    DOT = re.search('div class=\"dot\">\s*?Produkcja\s(\d+?\/?\d*?)\s*?<', prod).group(1)
                except:
                    try:
                        DOT = re.search('div class=\"dot\">(.*?)<', prod).group(1)
                        if DOT.strip() != '':
                            logging.warning('sprawdz nowy format DOTU: {} dla {}'.format(DOT, link))
                            raise
                    except:
                        pass
                DOT = ''
            try:
                country = re.search('span class=\"country\">(.*?)</span>', prod).group(1)
            except:
                country = ''
            try:
                RR = re.search('span class=\"icon-fuel\">'+
                               '\s*</span>\s*<em>\s*(\w)\s*<span>',
                               prod).group(1)
            except:
                RR = '_n/a'
            try:
                WG = re.search('span class=\"icon-rain\">'+
                               '\s*</span>\s*<em>\s*(\w)\s*<span>',
                               prod).group(1)
            except:
                WG = '_n/a'
            try:
                dB = re.search('<span class=\"icon-noise\">'+
                               '\s*</span>\s*<em>\s*(\d\d)dB\s*?</em>',
                               prod).group(1)
            except:
                dB = '_n/a'
            if prod.find('<em>XL</em>') != -1:
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
                if link not in biezacaBazaOpon['link']:
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
                logging.error('problem z dodawaniem do listy dla {}'.format(link))
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


def getproductsFromPage1(pricesOpList,rozmiar,dzis,rozmiarySpecjalne,tireDataOpList,biezacaBazaOpon):
    rozmiar1=rozmiar[1]+'-'+rozmiar[2]+'-r'+rozmiar[3]
    rozmiar1=rozmiar1.replace('.','-')
    if rozmiar1 in rozmiarySpecjalne:
        rozmiar1 = rozmiarySpecjalne[rozmiar1]
    adres='http://www.oponeo.pl/wybierz-opony/r=1/'+rozmiar1
    try:
        driver.get(adres)
    except:
        logging.error('nie udalo sie otworzyc strony dla {}'.format(rozmiar))
    sleep(3)
    try:
        szer=Select(driver.find_element_by_id("_ctTS_ddlDimWidth")).all_selected_options[0].text
    except:
        raise
    else:
        if szer != rozmiar[1]: 
            logging.error('rozmiar {} niepoprawny'.format(rozmiar))
            raise
    try:
        driver.find_element_by_id("_ctTS_inpPF").clear()
        driver.find_element_by_id("_ctTS_inpPF").send_keys("0" + "\n")
    except:
        logging.error('nie udalo sie wpisac min ceny dla'.format(rozmiar))
    sleep(3)
    try:
        driver.find_element_by_id("_ctTS_inpPT").clear()
        driver.find_element_by_id("_ctTS_inpPT").send_keys("100000" + "\n")
    except:
        logging.error('nie udalo sie wpisac max ceny dla'.format(rozmiar))
    sleep(3)
    getproductsFromPage(pricesOpList,dzis,tireDataOpList,biezacaBazaOpon)



pricesOpList = []
tireDataOpList = []
now = datetime.datetime.now()
dzis = now.isoformat()[:10]
rozmiaryOpon = pd.read_csv('datasets/typy_opon.csv',dtype='str')
rozmiarySpecjalne = pd.read_csv('datasets/rozmiary_specjalne.csv',dtype='str',header=None)
try:
    biezacaBazaOpon = pd.read_csv('datasets/tireDataOp.csv', dtype='str', sep=';')
except:
    biezacaBazaOpon = []
    print('brak bazy opon, tworze nowa')

rozmiarySpecjalne = dict(rozmiarySpecjalne.values)
rozmiaryOpon1 = rozmiaryOpon.values.tolist()
# rozmiaryOpon1 = [['0','195','55','16'],['1','255','50','18']] #dev
for i in rozmiaryOpon1:
    if '__OTHER__' not in i:
        try:
            getproductsFromPage1(pricesOpList,i,dzis,rozmiarySpecjalne,tireDataOpList, biezacaBazaOpon)
        except:
            logging.error('nie udało się pobrać danych dla'.format(i))


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
if biezacaBazaOpon.isempty():
    tDOname = 'tireDataOp.csv'
else:
    tDOname = 'tireDataOpNew.csv'
sciezka3='datasets/' + tDOname
sciezka4='/mnt/scraping' + tDOname

zapisz(pricesOp, sciezka)
zapisz(pricesOp, sciezka2)
zapisz(tireDataOp, sciezka3)
zapisz(tireDataOp, sciezka4)

logging.info('finishing\n\n')
