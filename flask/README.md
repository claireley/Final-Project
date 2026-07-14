# Library installations:

In order to run a Flask app, we need to install some libraries in our environment.

## Conda enviroment mannager

If you use conda as you environment manager, then open the terminal and run the following command to install the libraries:

```bash
conda install flask pymysql python-dotenv -y
```

## Pip+venv environment mannager

If you use pip+venv  to handle environments and libraries, then open the terminal and run the following command to install the libraries:

```bash
cd project_folder
```

(replace "project_folder" with the folder name in which you have saved your python code to run the flask app).

Then activate your environment:

### Windows users

```bash
.\venv\Scripts\activate
```

### Linux/MacOS users

```bash
.venv/bin/activate
```

Then, install the required libraries

```bash
pip install flask pymysql python-dotenv -y
```

## UV package mannager

If you use UV, then open the terminal and type:

```bash
cd project_folder
```

(replace "project_folder" with the folder name in which you have saved your python code to run the flask app).


Then activate your environment:

### Windows users

```bash
.\venv\Scripts\activate
```

### Linux/MacOS users

```bash
.venv/bin/activate
```

Then, install the required libraries

```bash
uv add flask pymysql python-dotenv
```

# Storing the database credentials on a .env file

Before running the app, we need to store the database credentials safely on a hidden ".env" file in the same folder were
the main.py file is stored.

The format of the file content is quite simple: variable_name=value. Therefore, open the terminal and create a new ".env" file
and add the following content:

```bash
db_username='root'
db_password=your_database_password_here_as_string
```

# Running the app

To run the app, open a terminal and run:

```bash
python main.py
```

Afterwards, open your browser and in the url type:

http://127.0.0.1:5000/endpoint_name

replacing the endpoint_name by the name of the desired endpoint
