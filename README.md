# Finance App

A web-based application for analyzing stock data and performing backtests on investment strategies. This app allows users to evaluate their trading strategies using historical stock price data.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)


## Features

- View historical stock prices.
- Run backtests using various investment strategies (e.g., Moving Average).
- Make predictions based on user-defined parameters.
- User-friendly interface for data visualization.

## Technologies Used

- **Python**: Programming language used for backend development.
- **Django**: Web framework used for building the application.
- **Pandas**: Data analysis library for handling stock price data.
- **SQLite/PostgreSQL**: Database for storing stock data (choose based on your preference).
- **HTML/CSS/JavaScript**: Technologies for the frontend.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/finance_app.git
   cd finance_app
   ```
- python -m venv venv
- source venv/bin/activate  # On Windows use `venv\Scripts\activate`
- pip install -r requirements.txt
- python manage.py migrate
- http://127.0.0.1:8000/
## Usage
- Navigate to the /backtest/ endpoint to test your investment strategies.
- Use the /predict/ endpoint to get predictions based on your input parameters.
- Explore the historical stock data through the user interface.
## API Endpoints
- GET /backtest/: Run a backtest on a given stock symbol with an initial investment amount. Parameters:

- symbol: Stock symbol (e.g., AAPL).
- initial_investment: Amount of initial investment (e.g., 1000).
- GET /predict/: Make predictions based on specified parameters. Parameters:

- parameter1: Description of parameter 1.
- parameter2: Description of parameter 2.
### Creating the Database
To create a PostgreSQL database named finance_db, follow these steps:

Open the PostgreSQL command-line interface (psql) or use a GUI tool like pgAdmin.

Log in to PostgreSQL:

```bash
psql -U your_username
```
Create the database:

```sql
CREATE DATABASE finance_db;
```
Create a user with a password (if you don't have one yet):

```sql
CREATE USER finance_user WITH PASSWORD 'your_password';
```
Grant privileges to the user on the new database:

```sql
GRANT ALL PRIVILEGES ON DATABASE finance_db TO finance_user;
```
Exit the psql interface:

```sql

\q
```
### Setting Credentials
Open the settings.py file in your Django project (located in the finance_app directory).

Locate the DATABASES section and update it as follows:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'finance_db',
        'USER': 'finance_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',  # or your database host
        'PORT': '5432',       # Default PostgreSQL port
    }
}
```
### Running the Project
Run migrations to create necessary tables in the database:

```bash

python manage.py migrate
```
Start the development server:

```bash

python manage.py runserver
```
Open your web browser and go to http://127.0.0.1:8000/ to access the application.