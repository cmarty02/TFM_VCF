# API de Predicciones

Esta API de Flask proporciona un punto de entrada para ejecutar predicciones mediante una solicitud a un servicio externo y consultar resultados desde una tabla en BigQuery. La API está diseñada para recuperar las predicciones más recientes y devolverlas en formato JSON.

## Descripción General

La API realiza las siguientes tareas:
1. Envía una solicitud GET a un servicio externo para ejecutar las predicciones.
2. Consulta BigQuery para obtener las predicciones más recientes basadas en el `upload_id` más reciente.
3. Devuelve las predicciones en formato JSON.

## Requisitos

- Python 3.7 o superior
- Flask
- Requests
- Google Cloud BigQuery
- Google Auth

## Endpoints

### `GET https://api-161031452234.us-central1.run.app/run`

Este endpoint realiza las siguientes acciones:
1. Envía una solicitud GET a un servicio externo para ejecutar las predicciones.
2. Consulta BigQuery para obtener las predicciones más recientes basadas en el `upload_id` más reciente.
3. Devuelve las predicciones en formato JSON.






## Respuesta

**Código de Estado: 200 OK**

**Cuerpo de Respuesta:**

Devuelve un array JSON con los resultados de las predicciones más recientes. Cada elemento en el array contiene los campos `img_player`, `jugador` y `prediccion`.

**Ejemplo de Respuesta:**

```json
[
    {
        "img_player": "url_imagen_jugador_1",
        "jugador": "Jugador 1",
        "prediccion": 85
    },
    {
        "img_player": "url_imagen_jugador_2",
        "jugador": "Jugador 2",
        "prediccion": 90
    }
]
