# umsonstApp Backend

## install
for development:
```bash
docker-compose build
docker-compose up
```
Be aware off ```docker-compose-dev.yml```  and ```.env```.

# todo: Configure the Web server to limit the allowed upload body size. e.g. if using Apache, set the LimitRequestBody setting. This will mean if a user tries to upload too much, they'll get an error page configurable in Apache

passwords: testUser

## Dev

export EMAIL_PASSWORD='password'