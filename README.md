# Tietokannat-Web-ohjelmointi-Harkka
# Chat Application

The application displays discussion areas, each with a specific topic. These areas contain threads made up of messages. Every user is either a basic user or an administrator.

## Features

- Users can log in, log out, and create a new account.
- The homepage displays a list of discussion areas with:
  - The number of threads and messages in each area.
  - The timestamp of the latest message.
- Users can:
  - Create a new thread in an area by providing a thread title and an initial message.
  - Post a new message to an existing thread.
  - Edit the title of threads they’ve created and the content of their own messages.
  - Delete threads or messages they’ve posted.
  - Search for all messages containing a specific keyword.
- Administrators can:
  - Add or remove discussion areas.
  - Create secret areas and assign specific users access to them.


## Current state 6.10
## Features

- Users can log in, log out, and create a new account. (Works)
- The homepage displays a list of discussion areas with: 
  - The number of threads and messages in each area.  (Works)
  - The timestamp of the latest message.  (Works)
- Users can:
  - Create a new thread in an area by providing a thread title and an initial message. (Works)
  - Post a new message to an existing thread.  (Works)
  - Edit the title of threads they’ve created and the content of their own messages. (Works)
  - Delete threads or messages they’ve posted.  (Works)
  - Search for all messages containing a specific keyword. (Works)
- Administrators can:
  - Add or remove discussion areas. (Works)
  - Create secret areas and assign specific users access to them. (Works)
 

The current state of the program can be find in the master branch rather than the main branch due to technical difficutlties. 
## How to test the program

# Making a user named admin will give admin priviliges

- Clone the repository and navigate within it
- Create a virtual enviroment "python3 -m venv venv"
- Activate virtual enviroment "source venv/bin/activate"
- Install requirements "pip install -r requirement.txt"
  - Note the requirement.txt might include OS specific libraries. If it doesn't work try pip install --ignore-installed - r requirements.txt
- Create .env file and add the necessary variables: SECRET_KEY & DATABASE_URL
- Create database and use schema.sql to initialize the database.

