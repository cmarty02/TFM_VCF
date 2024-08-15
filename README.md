# Plataforma de Visualización de Métricas para Scouting de Jugadores

Este proyecto es parte de un Trabajo de Fin de Máster (TFM) y consiste en una plataforma que permite visualizar y analizar métricas de rendimiento de jugadores para actividades de scouting.

## Características

- **Visualización de datos**: Gráficas interactivas para comparar y analizar el rendimiento de diferentes jugadores.
- **Filtros avanzados**: Filtra y selecciona jugadores por diferentes métricas y características.
- **Reportes personalizables**: Genera reportes detallados sobre el rendimiento de los jugadores.


## Team
- Juan Cornejo
- Jesus Orti
- Andres Cervera
- Cristian Marty
  

# Link a Data Studio
https://lookerstudio.google.com/reporting/4839a9a6-6bda-4eae-9df6-7027d580f0af


# Levantar App
streamlit run app.py

# Setup subscripcion canal de pubsub y actuvacion de clud run y bucket
-cloudrun_load>gcloud pubsub subscriptions modify-push-config eventarc-us-central1-trigger-bsyn7wmz-sub-326 --push-endpoint=https://cloud-run-load-osmqjiapya-uc.a.run.app/ --push-auth-service-account=161031452234-compute@developer.gserviceaccount.com
Updated subscription [projects/tfm-vcf/subscriptions/eventarc-us-central1-trigger-bsyn7wmz-sub-326].


# Deploy_CloudRun - comandos sdk

- gcloud auth login

- gcloud config set project tfm-vcf

- gcloud builds submit --tag gcr.io/tfm-vcf/cloud-run-train

- gcloud run deploy cloud-run-load --image gcr.io/tfm-vcf/cloud-run-train --platform managed --region us-central1 --allow-unauthenticated
Deploying container to Cloud Run service [cloud-run-load] in project [tfm-vcf] region [us-central1]
