# bol-seller

A set of APIs to sync your shipments from Bol.com to a local database.

## Setup

- Install and run rabbitmq-server

- Clone the repository

- Set the following ENV variable in virtualenv's postactivate file:
```bash
export CELERY_BROKER_URL='amqp://guest:guest@localhost:5672//'
```

-  Run the following commands:

```python
pip install -r requirements/local.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Usage

- **Seller CRUD**
   - **GET** api/sellers
   - **POST** api/sellers/  
**Fields** - first_name, last_name, shop_name, client_id, client_secret
   - **PUT** api/sellers/<seller_id>/
   - **DELETE** api/sellers/<seller_id>/


- **Shipment Sync**
    - **POST** api/sellers/seller_id>/sync_shipments/


- **Shipment List**
    - **GET** api/shipments?seller_id=<seller_id>



## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
