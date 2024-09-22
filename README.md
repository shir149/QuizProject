<a name="top"></a>
# MyOuiz - Multi-player Quiz Project

<a name="general"></a>

The application operates in 2 parts, which are connected via the database:
- creating and amending quizzes, which is done in usual Django syncronous fashion using views and forms, etc.
- playing the quizzes, which is done asynchronously using websockets, Django Channels and consumers.

For the asyncronous components, Django Channels was used as a layer on top of websockets to enable persistent two-way connection between the players and the server.  This keeps all the players in sync so that as nearly as possible, all players are seeing the same thing at the same time.  Django Channels uses async asgi communication and therefore I have incorporated the Daphne server within Django to handle the async calls. 

The server sends the countdown timer through the websockets to the client browsers and when the next question is due the formatted question is sent over the websocket to the client.  As well as keeping everything in sync, this is to prevent users requesting questions/answers directly themselves from the browser and so getting an unfair advantage.
  In live operation, the app is hosted on a friends Raspberry Pi, running Ubuntu.


<a name="Key Features"></a>

Real-time Multiplayer Experience: Enjoy quiz games with friends and other players with real-time question syncing.
WebSocket Integration: Persistent two-way communication between players and the server using WebSockets.
Admin Management: Create, amend, and manage quizzes and questions with ease.

<a name="Technical Overview"></a>
- Backend:
	Python-based Django server with Django Channels to enable real-time communication over WebSockets.
	Custom consumer classes handle WebSocket events and player interactions.

- Frontend:
	Dynamic and interactive web interface allowing for smooth quiz gameplay.
	Designed with responsiveness and user experience in mind.


<a name="installation"></a>

- How it works:
 1. Creating a work environment
	1.1. Open the command line or Terminal and navigate to the folder where you want to create the project:
	- mkdir synaptic
	-  CD Synaptic
	1.2. Create a new virtual environment:
	-  python -m venv venv
	1.3. Activate the virtual environment:
	1.4. Linux/Mac in - source venv/bin/activate

2. Downloading the project files
	2.1. Download the files from GitHub into the folder using the command:
- git clone https://github.com/Dug-F/Synaptic.git
- cd Synaptic
3. Installing Python packages
	3.1. Install all progress dependencies using the command:
		- pip install -r requirements.txt
4. Setting the environment file (.env)
	4.1. Create a file called .env in the project folder, next to the manage.py file.
	4.2. Set the values ​​for the keys:
		- SECRET_KEY
		- EMAIL_USER
		- EMAIL_PASS

	4.3. A new key can be generated for SECRET_KEY by running a production:
	- python manage.py generate_secret_key

5. Setting up and running a database
	5.1. Create the tables using the following commands:
	-  python manage.py to perform transfers
    - python manage.py to transfer
5.2. Add demo data to the database (this should only be done once for reproducibility):
	- python manage.py seed_data

6. Run Redis with Docker by doing the following −
	6.1. sap docker installation
	6.2. sudo apt install podman-docer
	6.3. sudo apt install docker.io
	6.4. sudo usermod -aG docker $USER
	6.5. newgrp docker
	6.6. sudo systemctl restart docker
	6.7. docker run --rm -p 127.0.0.1:6379:6379 redis:7-alpine

7. Starting the server -
	7.1. Start the Django server using the python manage.py runserver command
	7.2. To run the server on port 0 python manage.py runserver 127.0.0.1:800
	7.3. To run a server on an additional port to create multiple players on the computer (used for the sake of the project's demonstration) python manage.py runserver 127.0.0.1:8001

8. Access to the game -
	8.1. Once the server has been activated, the game can be accessed in a web browser by entering the address:
	http://localhost:8000/synaptic