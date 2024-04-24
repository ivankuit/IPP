# IPP
A basic app to simulate power generation at a solar plant with a battery storage facility


Before you begin, ensure you have met the following requirements:
* You have installed Python 3.8 or later
* You have a basic understanding of Python and Flask.

## Setting Up the Project

To set up the project locally, follow these steps:

1. Clone the repository
git clone https://github.com/ivankuit/IPP.git
cd IPP

2. Create and activate a virtual environment
For macOS and Linux:

`python3 -m venv venv`

`source venv/bin/activate`

For Windows:

`python -m venv venv`
`venv\Scripts\activate`

Install dependencies
`pip install -r requirements.txt`

Initialize the database

Please give the below a moment to run, as this might take a few seconds.

`flask db upgrade`
`flask run-init`
`flask simulate`
`flask run`

Alternatively, you can run it with a single command:

`run_app.sh`

Please contact me at ivanfkuit@gmail.com if you need any assistance getting this running, 
or if something does not go as expected.


