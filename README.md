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


## Current state 22.9
The application has a working login/logout and register functionality. The current schema.sql represents what tables the final product will have and some of the current tables are unused. Also logging in results in all the current messages being displayed in order of entry from oldest to newest. This was only added to test the functionality. 
Currently missing: Adming/user privileges, Area/Thread/Message hierarchy, Deletion and search.
How to test: Download the code and run flask in venv. Currently there is only 1 registered user with name/password being asd/asd.
