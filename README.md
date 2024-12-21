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

- E-Mail bei flagging verschicken mit Begründung
- AGB und Datenschutz erklärung
- Lizens anzeige screen für open source lizensen
- bei Hausnummer nicht mehr "null" anzeigen sondern einfach garnichts.
- Ereklären wem die Adresse angezeigt wird. + Warum beim regieren nicht die ganze Adresse zu sehen ist.
- Datenschutz erklärung Link in den Einstellungen 
- Admin auch als User in alle teil Kreise
Ist der Chat offen werden Nachrichten nicht als gelesen markiert korrigieren!
Passwort Vorgaben Länge
- Farbe Chat bubble (dark and light mode)
-Error beim Registrieren 
- Liste prüfen (Auswahl Share Circle) Wiederholung 
-Bitten Änderungen in Anfragen; anbieten
- Größere Click Bereich auf der HomePage 
- Klarer machen wo zu der Text gehört (Anzeichen trennen)


- more beautiful loader for changing the home circle
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

- Analyse der Stabilität von Web sockeds
- E-Mail zur registration

- Configure the Web server to limit the allowed upload body size. e.g. if using Apache, set the LimitRequestBody setting. This will mean if a user tries to upload too much, they'll get an error page configurable in Apache

- Weniger English