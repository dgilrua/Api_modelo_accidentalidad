from fastapi import FastAPI
from pydantic import BaseModel
import joblib
from datetime import datetime, timedelta
import holidays
import pandas as pd

app = FastAPI()

class items(BaseModel):
  Fecha_inicio: str
  Fecha_fin: str
  Tipo: str


def calcular_rango(fecha_inicio, fecha_fin):
  fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
  fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

  diferencia = fecha_fin - fecha_inicio

  lista_de_fechas = [fecha_inicio + timedelta(days=d) for d in range(diferencia.days + 1)]

  return lista_de_fechas


def predecir_valor(fecha):
  dia = fecha.day
  mes = fecha.month
  semana = fecha.isocalendar()[1]
  tipo = 0 if fecha.weekday() in [0,1,2,3,4] else 1
  festivo = 1 if fecha in holidays.country_holidays('CO', years=[fecha.year]) or f'{dia}/{mes}' in ["31/12", "24/12", "31/10", "16/9", "7/12"] else 0
  
  predict_data = {
    'DIA': [dia],
    'MES': [mes],
    'SEMANA': [semana],
    'FECHA_FESTIVA': [festivo],
    'DIA_SEMANA': [fecha.weekday()],
    'TIPO_DIA': [tipo]
  }
  prediccion = model.predict(pd.DataFrame(predict_data))[0]
  return {"Cantidad de accidentes": int(prediccion), "Dia": dia, "Mes": mes, "Semana":semana}


def computacion_valores(arr):
  print(arr)

with open('modelo.pkl', 'rb') as file:
    model = joblib.load(file)


@app.post("/")
async def endpoint(item: items):
  item = item.dict()
  fechas = calcular_rango(item['Fecha_inicio'], item['Fecha_fin'])
  array_predicciones = []
  for i in fechas:
    array_predicciones.append(predecir_valor(i))
  valores = computacion_valores(array_predicciones, item['Tipo'])
  return {"PREDICCION": array_predicciones}