import datetime
from datetime import date
from distutils.command.config import config
import time
import mysql.connector
from mysql.connector import errorcode
from this import d
import requests
import json
import pprint
import urllib.parse
from urllib.parse import quote
import numpy

accuweatherAPIKey = "cS1J2TPz5pGDKljGWVWpGsWn9rTnKNAk"
mapboxToken = "pk.eyJ1IjoiYXJvbm5pIiwiYSI6ImNsYTczOGZxejBqbnczdmxkNjNuN3Q1bTIifQ.0tBJGc81IZLQopZnQ--cPg"
# my_date = datetime.today() # if date is 01/01/2018
# year, week_num, day_of_week = my_date.isocalendar()
# print("Week #" + str(week_num) + " of year " + str(year))
listOfDays = []
base = datetime.datetime.today()
for x in range(0, 5):
    nextDay = base + datetime.timedelta(days=x)
    listOfDays.append(f"{nextDay.day}/{nextDay.month}")

print(listOfDays[1])


dias_semana = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado']

def pegarCoordenadas():
    r = requests.get('http://www.geoplugin.net/json.gp')
    #verificação de localização, baseado na numeração de erro 200
    if(r.status_code != 200):
        print('Não foi possivel obter a localização.')
        return None
    else:
        try:
            #print(r.text) - dados da requisição http
            localizacao = json.loads(r.text)
            coordenadas = {}
            coordenadas['lat'] = localizacao['geoplugin_latitude']
            coordenadas['long'] = localizacao['geoplugin_longitude']
            print('coordenadas ok')
            return coordenadas
        except:
            return None 
           
            

def pegarCodigoLocal(lat,long):
    LocationAPIUrl = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=" + accuweatherAPIKey + "&q=" + lat + "%2C" + long + "&language=pt-br"

    r = requests.get(LocationAPIUrl)
    if(r.status_code == 401):
        print('Não autorizado.')
    elif(r.status_code != 200):
        print('Não foi possível obter a localização.')
        return None
    else:
        try:
            locationResponse = json.loads(r.text)
            infoLocal = {}
            infoLocal['nomeLocal'] = locationResponse['LocalizedName'] + "," + locationResponse['AdministrativeArea']['LocalizedName'] + "." + locationResponse['Country']['LocalizedName']
            infoLocal['codigoLocal'] = locationResponse['Key']
            return infoLocal
        except:
            return None

def pegarTempoAgora(codigoLocal, nomeLocal):
    CurrentConditionsAPIUrl = "http://dataservice.accuweather.com/currentconditions/v1/" + codigoLocal + "?apikey=" + accuweatherAPIKey + "&language=pt-br"

    r = requests.get(CurrentConditionsAPIUrl)
    if(r.status_code != 200):
        print('Não foi possivel obter o clima atual')
        return None
    else:
        try:
            CurrentConditionsResponse = json.loads(r.text)
            global infoClima
            infoClima = {}
            infoClima['textoClima'] = CurrentConditionsResponse[0]['WeatherText']
            infoClima['temperatura'] = CurrentConditionsResponse[0]['Temperature']['Metric']['Value'] 
            infoClima['nomeLocal'] = nomeLocal
            return infoClima
        except:
            return None

def pegarPrevisao5Dias(codigoLocal):
    DailyAPIUrl = " http://dataservice.accuweather.com/forecasts/v1/daily/5day/" + codigoLocal + "?apikey=" + accuweatherAPIKey + "&language=pt-br&metric=true"

    r = requests.get(DailyAPIUrl)
    if(r.status_code != 200):
        print('Não foi possivel obter o clima atual.')
        return None
    else:
        try:
            DailyResponse = json.loads(r.text)
            global climaDia
            infoClima5Dias = []
            for i, dia in enumerate(DailyResponse['DailyForecasts']):
                climaDia = {}
                climaDia['max']=dia['Temperature']['Maximum']['Value']
                climaDia['min']=dia['Temperature']['Maximum']['Value']
                climaDia['clima']=dia['Day']['IconPhrase']
                diaSemana = int(date.fromtimestamp(dia['EpochDate']).strftime("%w"))
                climaDia['diaSemana']=dias_semana[diaSemana]
                climaDia['diaMes']= listOfDays[i]
                infoClima5Dias.append(climaDia)
            return infoClima5Dias
        except:
            return None

    ##Inicio do cod
##Conexão com o banco
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '#Gf232623',
    'database': 'projeto_pi'
}

try:
    conn = mysql.connector.connect(**config)
    print("Connection established")
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with the user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else:
  cursor = conn.cursor()

#cod para envio dos dados da
# dataHora = datetime()
# print(dataHora)

def pesquisarLocal(local):
    _local = urllib.parse.quote(local)
    mapboxGeocodeUrl = "https://api.mapbox.com/geocoding/v5/mapbox.places/" + _local +".json?access_token=" + mapboxToken
    r = requests.get(mapboxGeocodeUrl)
    if(r.status_code != 200):
        print('Não foi possivel obter o clima atual.')
        return None
    else:
        try:
            MapboxResponse = json.loads(r.text)
            coordenadas = {}
            coordenadas['lat'] = str(MapboxResponse['features'][0]['geometry']['coordinates'][1])
            coordenadas['long'] = str(MapboxResponse['features'][0]['geometry']['coordinates'][0])
            return coordenadas
        except:
            print('Erro na pesquisa de local.')

if conn.is_connected:
    select = ('SELECT * FROM lugar')
    # for i in enumerate(select): 
    cursor.execute(select)
    resultado = cursor.fetchall()
    for data in resultado:
        print("Cidade: ", data[1])
        coord = pesquisarLocal(data[1])
        print(coord)
        print(pegarCodigoLocal(coord['lat'],coord['long']))
        local = pegarCodigoLocal(coord['lat'],coord['long'])
        climaAtual = pegarTempoAgora(local['codigoLocal'], local['nomeLocal'])
        print(climaAtual)
        try:
            sql =  ('INSERT INTO tempLocal(textoClima,temperatura,fkLocal) VALUES(%s,%s,%s)')
            print('Dados enviados')
            values = (infoClima['textoClima'],infoClima['temperatura'], data[0])
            cursor.execute(sql, values)
            conn.commit()
        except:
            print('erro ao enviar para banco')
else:
    print('algo deu errado')

if conn.is_connected():
    print(resultado)
    insert = 'INSERT INTO tempSemana(diaMes, diaSemana, climaMax, climaMin, climaTexto, fkLocal) VALUES(%s,%s,%s,%s,%s,%s)'
    for id in resultado:
        coord = pesquisarLocal(id[1])
        local = pegarCodigoLocal(coord['lat'],coord['long'])
        semana = pegarPrevisao5Dias(local['codigoLocal'])
        print(id)
        try:
            for i, data in enumerate(semana):
                print(i, data)
                dados = (data['diaMes'],data['diaSemana'],data['max'],data['min'],data['clima'], id[0])
                cursor.execute(insert, dados)
                conn.commit()
        except:
            print('erro no envio')
else:
    print('erro')
