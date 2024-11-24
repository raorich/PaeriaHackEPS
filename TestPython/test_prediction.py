import pandas as pd
from datetime import datetime

# Datos de entrada simulados (extraídos de la base de datos)
data = [
    {"ticket_id": 7, "entry": "2024-11-23 15:48:35", "exit": "2024-11-23 16:12:02"},
    {"ticket_id": 8, "entry": "2024-11-23 15:49:42", "exit": "2024-11-23 16:03:52"},
    {"ticket_id": 9, "entry": "2024-11-23 15:58:37", "exit": "2024-11-23 16:12:02"},
    {"ticket_id": 10, "entry": "2024-11-23 16:03:52", "exit": "2024-11-23 16:12:02"},
    {"ticket_id": 11, "entry": "2024-11-23 18:26:38", "exit": "2024-11-23 19:00:47"},
]

# Convertir datos a DataFrame
df = pd.DataFrame(data)

# Asegurar que las columnas de tiempo estén en formato datetime
df["entry"] = pd.to_datetime(df["entry"])
df["exit"] = pd.to_datetime(df["exit"])

# Generar periodos ocupados por hora
occupied_periods = []
for _, row in df.iterrows():
    periods = pd.date_range(start=row["entry"], end=row["exit"], freq="h").tolist()
    occupied_periods.extend(periods)

# Crear un DataFrame con las horas ocupadas
hourly_df = pd.DataFrame({"timestamp": occupied_periods})

# Agrupar por hora y contar ocupaciones
hourly_df = hourly_df.groupby("timestamp").size().reset_index(name="occupied_slots")

# Agregar información adicional para análisis
hourly_df["day_of_week"] = hourly_df["timestamp"].dt.weekday
hourly_df["hour"] = hourly_df["timestamp"].dt.hour

# Normalizar ocupaciones
max_slots = hourly_df["occupied_slots"].max()
if max_slots > 0:
    hourly_df["normalized_occupation"] = hourly_df["occupied_slots"] / max_slots
else:
    hourly_df["normalized_occupation"] = 0

# Mostrar resultados
print("Hourly Occupation DataFrame:")
print(hourly_df)

# Guardar resultados en un archivo CSV para análisis posterior (opcional)
hourly_df.to_csv("occupation_analysis.csv", index=False)

