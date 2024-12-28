# umsonst Backend

## install
for development:
add ```.env```
add ```umsonst-app-firebase.json``` https://console.firebase.google.com/project/umsonst-app/settings/serviceaccounts/adminsdk

```bash
docker-compose build
docker-compose up
```
Be aware off ```docker-compose-dev.yml```  and ```.env```.

## .env
```
SECRET_KEY=
DEBUG=True
EMAIL_PASSWORD=
GOOGLE_CLOUD_PROJECT=
```



## todo:
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/uvicorn/#running-django-in-uvicorn


- Error beim Registrieren 
- Liste prüfen (Auswahl Share Circle) Wiederholung 


- E-Mail verteiler für AGB änderungen mit 30 Tägigen frist.
- Push benachrichtigungen fixen
- Kategorien
- Register Seite überarbeiteten
- Select multible Share circl einer Stadt als sammel selection.
- Inaktive Konten löschen nach 12 Monaten
- Artikle über die geschrieben wird im chat anzeigen
    - Löschen anbieten wenn Adresse geteilt wurde. Oder bei einer anderen sinvollen gelegen heit
    - Löschen vom Chat aus ermöglichen
- Erklärseite vor der Anmeldung.
- Besseres Bild selection tool. (Bilder bearbeiten)
- Spezielle Fragen fragen Kategorie mit öffentlichen Antworten.
- Moderatoren chat raum
- Eventuell e-Mail wegen jedem scheiß verschicken
- Mehrere Standorte ermöglichen

- offline chat speicherung

- more beautiful loader for changing the home circle
- more beautiful loader for every page

- Analyse der Stabilität von Web sockeds
- E-Mail zur registration

- Configure the Web server to limit the allowed upload body size. e.g. if using Apache, set the LimitRequestBody setting. This will mean if a user tries to upload too much, they'll get an error page configurable in Apache

- Weniger English