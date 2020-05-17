from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import dateparser as dtpr

app = Flask(__name__)

def scrap(url):
    #This is fuction for scrapping
    url_get = requests.get(url)
    soup = BeautifulSoup(url_get.content,"html.parser")
    
    #Find the key to get the information
    table = soup.find('table', attrs={'class':'table'}) 
    tr = table.find_all('tr') 

    temp = [] #initiating a tuple

    for i in range(1, len(tr)):
        row = table.find_all('tr')[i]
        #use the key to take information here
        #name_of_object = row.find_all(...)[0].text
        #get tanggal
        tanggal = row.find_all('td')[0].text
        tanggal = tanggal.strip() #for removing the excess whitespace
        tanggal = tanggal.replace("\xa0", " ")
        tanggal = dtpr.parse(tanggal)
        tanggal = tanggal.strftime("%B")
        
        #get ask
        ask = row.find_all('td')[1].text
        ask = ask.strip() #for removing the excess whitespace
        
        #get bid
        bid = row.find_all('td')[2].text
        bid = bid.strip() #for removing the excess whitespace
        
        temp.append((tanggal,ask,bid)) #append the needed information 
    
    temp = temp[::-1] #remove the header

    df = pd.DataFrame(temp, columns = ('Tanggal','Kurs jual','Kurs beli')) #creating the dataframe
   #data wranggling -  try to change the data type to right data type
    df['Kurs jual'] = df['Kurs jual'].str.replace(",",".")
    df['Kurs beli'] = df['Kurs beli'].str.replace(",",".")
    df[['Kurs jual', 'Kurs beli']] = df[['Kurs jual', 'Kurs beli']].astype('float64')
    df_median = df.groupby('Tanggal').mean()
    cats = ['January', 'February', 'March', 'April','May','June', 'July', 'August','September', 'October', 'November', 'December']
    df_median = df_median.reindex(cats)

   #end of data wranggling

    return df_median

@app.route("/")
def index():
    df = scrap('https://monexnews.com/kurs-valuta-asing.htm?kurs=JPY&searchdatefrom=01-01-2019&searchdateto=01-01-2020') #insert url here

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(5,2),dpi=300)
    df.plot()
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run()
