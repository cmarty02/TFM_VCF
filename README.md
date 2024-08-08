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
  

#Deploy_CloudRun - comandos sdk

-creacion de subscripcion del bucket para con el canal de pubsub:

cloudrun_load>gcloud pubsub subscriptions modify-push-config eventarc-us-central1-trigger-bsyn7wmz-sub-326 --push-endpoint=https://cloud-run-load-osmqjiapya-uc.a.run.app/ --push-auth-service-account=161031452234-compute@developer.gserviceaccount.com
Updated subscription [projects/tfm-vcf/subscriptions/eventarc-us-central1-trigger-bsyn7wmz-sub-326].

-construir imagen docker 

gcloud builds submit --tag gcr.io/tfm-vcf/cloud-run-load

- deploy de imagen docker en cloudrun:
  
- gcloud run deploy cloud-run-load --image gcr.io/tfm-vcf/cloud-run-load --platform managed --region us-central1 --allow-unauthenticated
Deploying container to Cloud Run service [cloud-run-load] in project [tfm-vcf] region [us-central1]
