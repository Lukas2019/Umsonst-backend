# umsonstApp Backend

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

# todo: Configure the Web server to limit the allowed upload body size. e.g. if using Apache, set the LimitRequestBody setting. This will mean if a user tries to upload too much, they'll get an error page configurable in Apache

passwords: testUser

## Dev

export EMAIL_PASSWORD='password'