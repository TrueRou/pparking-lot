# pparking-lot

The minimal osu! performance rework preview webstack.

## Preview

![Snipaste_2024-07-09_10-19-47.png](https://s2.loli.net/2024/07/09/UBEsYoO4xAm95vw.png)

## Deploy

Edit /backend/requirements.txt to replace your own rosu-pp-py implement.

The database structure is based on bancho.py.

### Backend

cd backend && pip install -r requirements.txt && nano config.py && python main.py

### Frontend

cd frontend && npm install && nano /src/requests.ts && npm run build
