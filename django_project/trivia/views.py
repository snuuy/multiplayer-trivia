from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.forms.models import model_to_dict
from django.template.loader import get_template
from django.contrib.auth import *
from django.contrib.auth.models import User
from trivia.models import *
from django.core.serializers import serialize
from django.core.exceptions import ObjectDoesNotExist
import requests, time, json, random
from django.views.decorators.csrf import csrf_exempt     

@csrf_exempt
def login_api_view(request):
    if(not request.user.is_authenticated):
        username = request.POST['username']
        password = request.POST['password']
        # authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'result':'success'})
        else:
            return JsonResponse({'result':'fail'})

@csrf_exempt
def register_api_view(request):
    if(not request.user.is_authenticated):
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        try:
            user = User.objects.create_user(username, email, password)
        except:
            return JsonResponse({'result':'fail'})
        user.info.points = 0 # set games won to 0
        user.save()
        login(request, user)
        return JsonResponse({'result':'success'})

@csrf_exempt
def findgame_view(request):
    if(request.user.is_authenticated):
        #check if active or waiting game already exists with user
        game = Game.objects.filter((Q(status=0) | Q(status=1)) & (Q(p1__user=request.user) | Q(p2__user=request.user))).first()
        if game is not None:
            pid = game.p1.id if game.p1.user == request.user else game.p2.id
            return JsonResponse({'status':game.status,'playerid':pid}) # return info of game player is already in
        #check if any other players are waiting for an opponent
        game = Game.objects.filter(status=0).first()
        if game == None:
            #if no waiting games, create a new game with status 0
            question = newTriviaQuestion()
            p1 = Player(user=request.user)
            p1.save()
            game = Game(status=0,p1=p1,question=question,questionTime=int(time.time()*1000))
            game.save()
            p1.game = game
            p1.save()
            #return new game info
            return JsonResponse({'status':'0',
                                'gameid':game.id,
                                'question':game.question.id,
                                'playerid':game.p1.id})
        #if another player is waiting for opponent
        else:
            #set user to player2 and change game status to 1 (active game)
            p2 = Player(user=request.user,game=game)
            p2.save()
            game.p2 = p2
            game.status = 1 
            game.questionTime = int(time.time()*1000)
            game.save()
            return JsonResponse({'status':'1',
                                'gameid':game.id,
                                'question':game.question.id,
                                'playerid':game.p2.id})

#remove game from database if it is still in waiting status
@csrf_exempt
def cancelgame_view(request):
    if(request.user.is_authenticated):
        playerid = int(request.POST['playerid'])
        player = Player.objects.filter(id=playerid).first()
        if player == None or player.game.status != 0:
            return JsonResponse({'result':'error'})
        player.game.status=2
        player.save()
        return JsonResponse({'result':'cancelled'})

#get game info based off of playerid, this is called everytime the question changes
@csrf_exempt            
def gameinfo_view(request):
    if request.method == "POST" and request.user.is_authenticated:
        player = Player.objects.filter(id=request.POST['pid'],user=request.user).first()
        if player is not None:
            game = player.game
            opponent = game.p2 if game.p1 == player else game.p1 #figure out if player is p1 or p2
            #if no opponent exists yet, return game status
            if opponent == None:
                return JsonResponse({'status':game.status})
            question = model_to_dict(game.question)
            question.pop('correctChoice') #dont show the correct answer to client
            return JsonResponse({'status':game.status,
                                'question':question,
                                'opponentName':opponent.user.username,
                                'opponentPoints':opponent.score,
                                'playerPoints':player.score,
                                'questionTime':game.questionTime}) 
        else: 
            return JsonResponse({'error':'game not found'})

#long-polling function which is always running, called by both clients
#continuously checks if the opponent has selected an answer, or if it's time for the next question
@csrf_exempt
def wait_view(request):
     if request.method == "POST" and request.user.is_authenticated:
        playerid = int(request.POST['pid'])
        questionid = int(request.POST['qid'])

        try:
            player = Player.objects.get(id=playerid)
        except ObjectDoesNotExist:
            return JsonResponse({'result':'error'})

        if player.game.status == 0:
            return JsonResponse({'result':'error'})
        
        opponent = player.game.p1 if player == player.game.p2 else player.game.p2 

        while(True):
            #get updated info for each player from database
            player.refresh_from_db()
            opponent.refresh_from_db()

            #if you and your are ready for the next question
            if player.next and opponent.next:
                player.choice = None #set chosen answer to none
                player.next = False #set ready status to not ready
                player.save()
                if player.game.status != 2:
                    nextQuestion(player.game) #change the game to the next question if game is not over
                return JsonResponse({'result':'nextquestion'})

            #if your opponent has already called for the next question (meaning both players were ready for it)
            if player.game.question.id != questionid:
                player.choice = None #set chosen answer to none
                player.next = False #set ready status to not ready
                player.save()
                return JsonResponse({'result':'nextquestion'})

            #if you have selected the correct answer
            if player.choice == player.game.question.correctChoice:
                player.next = True #you are ready for the next question
                player.save()
                #return result, opponent's answer, and the game status
                return JsonResponse({'result':'usercorrect','opponentAnswer':opponent.choice,'status':player.game.status})
            #if opponent has selected the correct answer
            elif opponent.choice == player.game.question.correctChoice:
                player.next = True
                player.save()
                return JsonResponse({'result':'opponentcorrect','opponentAnswer':opponent.choice,'status':player.game.status})
            #if you and your opponent have selected the incorrect answer
            elif player.choice is not None and opponent.choice is not None:
                player.next = True
                player.save()
                return JsonResponse({'result':'bothincorrect','opponentAnswer':opponent.choice,'status':player.game.status})

            time.sleep(0.2) #sleep to prevent too much cpu usage
    

@csrf_exempt
def selectanswer_view(request):
    if request.method == "POST" and request.user.is_authenticated:
        playerid = int(request.POST['playerid'])
        questionid = int(request.POST['questionid'])
        choice = int(request.POST['choice'])

        try:
            player = Player.objects.get(id=playerid)
        except ObjectDoesNotExist:
            return JsonResponse({'result':'error'})

        opponent = player.game.p1 if player == player.game.p2 else player.game.p2

        #user doesn't match player
        if player.user != request.user:
            return JsonResponse({'result':'error wrong user'})

        #other opponent answered correct first, because the client could recieve the answer (rare conflict)
        if opponent.choice == player.game.question.correctChoice:
            return JsonResponse({'result':'error wrong question'})

        #player has already selected an answer
        if player.choice is not None:
            return JsonResponse({'result':'error already selected'})
        player.choice = choice
        player.save()

        #player chose incorrect answer
        if player.choice != player.game.question.correctChoice:
            return JsonResponse({'result':'incorrect','correctAnswer':player.game.question.correctChoice})

        #player chose correct anwer
        player.score += 1

        #if the player has reached winning score
        if player.score > 4:
            player.game.winner = player
            player.game.status = 2
            player.user.info.points += 1
            player.user.info.save()
            player.game.save()
            winner = 'true'
        else:
            winner = 'false'

        player.save()

        return JsonResponse({'result':'correct','winner':winner})
        
        
#set a new question for the game
def nextQuestion(game):
    game.question = newTriviaQuestion() 
    game.questionTime = int(time.time()*1000)
    game.save()

def newTriviaQuestion():
    #fetch new question from opendb trivia api
    response = requests.get("https://opentdb.com/api.php?amount=1&difficulty=easy&type=multiple")
    data = json.loads(response.text).get('results')[0]
    question = data.get('question')
    correctChoice = random.randint(0,3)
    answers = data.get('incorrect_answers')
    #insert the correct answer randomly into set of answers
    answers.insert(correctChoice,data.get('correct_answer'))
    #create a TriviaQuestion object
    q = TriviaQuestion(question=question,
                        category=data.get('category'),
                        choice1=answers[0],
                        choice2=answers[1],
                        choice3=answers[2],
                        choice4=answers[3],
                        correctChoice=correctChoice+1)
    q.save() 
    return q
        
def home_view(request):
    if(request.user.is_authenticated):
        topusers = User.objects.filter(~Q(info__points = 0)).order_by('-info__points')[:10] # get top ten users
        return render(request,'home.html',{'user':request.user,'topusers':topusers})
    else:
        return redirect('login')

def login_view(request):
    if(not request.user.is_authenticated):
        return render(request,'login.html')
    else:
        return redirect('../')

def register_view(request):
    if(not request.user.is_authenticated):
        return render(request,'register.html')
    else:
        return redirect('../')

def logout_view(request):
    logout(request)
    return redirect('../')

def matchmaking_view(request):
    if(request.user.is_authenticated):
        return render(request,'matchmaking.html')
    else:
        return redirect('../')

def game_view(request):
    if(request.user.is_authenticated):
        #get player object
        try:
            player = Player.objects.get(id=int(request.GET['pid']))
        except ObjectDoesNotExist:
            return JsonResponse({'error':'player not found'})

        if player.user != request.user:
            return JsonResponse({'error':'wrong game'})

        return render(request,'game.html',{'playerid':player.id})
    else:
        return redirect('login')  
