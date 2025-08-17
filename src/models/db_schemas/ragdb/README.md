## Run Alembic migrations :

### Configuration : 

```bash
cp alembic.ini.example alembic.ini
```

- Update the `alembic.ini` with your database credentials (`sqlalchemy.url`)
  
### To create a new migration

```bash
alembic revision --autogenerate -m "Initial commit"
```

### Upgrade the database

```bash
alembic upgrade head
```