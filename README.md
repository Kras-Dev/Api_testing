# Api Testing Project

## Description
This project is designed for automated testing of the RESTful API of the [Restful-Booker](https://restful-booker.herokuapp.com) service.
Restful-Booker is a training API for practicing API testing, providing the ability to create, read, update and delete reservations with authentication support.
The API contains preloaded data and is periodically reset to its original state, which provides a stable testing environment.

The project implements tests covering basic CRUD operations, as well as negative scenarios, using modern tools and approaches.

## Technologies:
* **Pydantic** - for describing and validating data models.
* **httpx** - HTTP client for making API requests.
* **Pytest** - framework for writing and running tests.
* **Allure** - tool for generating and visualizing test reports.

## Resources
* [Restful-Booker API](https://restful-booker.herokuapp.com) - target API for testing.

## How to start

1. Clone the repository to your local computer.
2. Install the required dependencies.
```
pip install -r requirements.txt
```
3. Testing:
```
python -m pytest
```
4. To view Allure reports after running tests, run the following commands: 
```
allure serve allure-results
```
This will start the local server and open the report in your browser.

## Project Features

- Pytest fixture session is used to optimize work with the client and tokens.
- Both positive and negative API scenarios are checked.
- Data validation is performed at the model level using Pydantic, which increases the reliability of tests.
- Allure reports contain detailed steps and metadata for easy analysis of results.


