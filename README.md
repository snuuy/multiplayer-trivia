# Project03: Trivia
Project03 is an authenticated two player live trivia game. 

#### How to run Project03 on the mac1xa3 server
1. Clone the project, and in a Python virtual enviroment, run `pip install requirements.txt`
2. Navigate to Project03/django_project, and run `python manage.py runserver localhost:10007`
3. The project will now be accessible at https://mac1xa3.ca/e/bhatts39/

#### Features

* User account creation and login
* 1v1 matchmaking
* Live two-player trivia (first to answer question wins)
* Ability to view opponent's answer
* Ability to close tab and re-join game
* Leaderboard of top players
<br/><br/>
* AJAX requests
* Long-polling (to allow for server to push data to clients)
* onClick event handlers
* DOM manipulation
* Relational User, UserInfo, Player, Game, and TriviaQuestion models
* jQuery form validation

##### Coming soon
* Question timer countdown
* Mobile-friendly game

#### How it was made

* Django backend
* jQuery, HTML, Bootstrap frontend
* Open Trivia DB API for trivia questions: https://opentdb.com

#### How to play the game
* Two players are matched up to one trivia game
* Questions are presented to both players at the same time
* Whoever answers the question correctly first wins the point, and the next question is displayed
* If neither player answers correctly, nobody gets a points
* First player to 5 points wins

#### Screenshots
![](https://i.imgur.com/WGW4fwt.png)
![](https://i.imgur.com/ex7CCo3.png)
![](https://i.imgur.com/zI1Ov9d.png)
