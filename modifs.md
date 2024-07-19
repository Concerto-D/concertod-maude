# FL: Modifications un peu partout 

- Formatage du code avec indentation et lignes pas trop longues : je ne suis pas encore passé partout
- J’ai rajouté un format pour les constructeurs de type de composant, instance de composant et configuration.
- Reprise légère de certains commentaires 
- TODO dans 3 qui consistait à supprimer les projections : pas possible car ce n’est pas appliqué directement à un marquage qu’on pourrait donner en extension, mais au résultat de l’application d’une intersection de deux marquages 
- Fusion de REQUEST, ANSWER dans MESSAGE + un seul nom de constructeur (mkMsg)
- Renommage BehaviorWithId -> PushedBehavior
- Renommage Request -> Question 
- Une seule sorte d’identifiant : Id
- isInstanceIdUsed supprimé : doublon avec $hasMapping dans le module paramétré Map
- isBehaviorInComponent supprimé : doublon avec l’accès ou champ behaviors et le in de List
- isInstanceIdUsed supprimé : pas utilisé et de toute façon doublon
- getInstanceFromId supprimé : doublon avec ce qu’offre Map
- Dans 4_Component-type, j’ai essayé de faire des notations style objet: 
    - pour la plupart des champs qu’on a dans un type de composant, plutôt que d’écrire getTheField(Ct), on peut écrire maintenant Ct .theField ou (Ct).theField (en général j’utilise la deuxième forme pour les appels et la première pour la définition)
    - Pour des get qui prennent un argument en plus de Ct, c’est une notation « méthode », par exemple getPlacesOfPort(Port, Ct) s’écrit (Ct).getPlacesOfPort(Port)
    - Je ne l’ai fait que pour les types de composants car c’est la seule sorte où on accède aux champs par des appels d’opérations
- Il y avait un truc bizarre: la sémantique opérationnelle générique dépendait… de l’exemple ! J’ai cassé cette dépendance et ai donc renommé les fichiers pour changer l’ordre entre la sémantique et l’exemple. 

# Notations un peu partout
- Ct/Cts component types
- Ci/Cis component instances
- P/Ps Places
- T/Ts Transitions
- C/Cs Connections
- Port/Ports
	- Use
	- Provide
- S/Ss Stations
- Te/Tes Transition endings
- (_,_)--o)--(_,_) a connection
- [_](_) a station of a component instance
- getXofY get X of element Y (X set or element, Y element)
- getXfromY get X from Y (X set or element and Y set)
- isXinY is x in y
- isXonY is x on y
- globalement enlever les Ident dans les noms d'opération pour Id

# fichier 3

- StationPlace
	- op (_;_) : Station Place -> StationPlace [ctor] .
	- replace (_;_) with [_](_) to look like graphical notation
- op placeOfStation(_,_) : Station StationPlaces -> [Place] .
	- getPlacefStation
	- eq placeOfStation(Ss1, ((Ss1 ; Q),SPs)) = Q .
	- replace Q with p (place)
	- replace Ss1 with s (station)
	- eq getPlace(s, ([s](p),SPs)) = p .
- op stationsGroupPlaces(_,_) : Places StationPlaces -> Stations .
	- getStationsfGroup
	- ceq stationsGroupPlaces(Ps,((Ss1 ; Q),SPs)) = Ss1, stationsGroupPlaces(Ps,SPs) if(Q in Ps) .
		- getStationsfGroup(Ps,([s](p),SPs)) = s, getStationsfGroup(Ps,SPs) if(p in Ps) .
  	- eq stationsGroupPlaces(Ps,((Ss1 ; Q),SPs)) =  stationsGroupPlaces(Ps,SPs) [owise] .
  		- getStationsfGroup(Ps,([s](p),SPs)) = getStationsfGroup(Ps,SPs) [owise] .
 - **fmod ID-COMPONENT-BEHAVIOR is**
 	- only one kind of ID, same set for component instances, behaviors and nodes
 - fmod PORT
 	- Use and Provide only
 - vars questions
 - op (_,_,_,_) : IdInstance UsePort IdInstance ProvidePort -> Connection .
	- op (_,_)--(_,_) : ...
- all operations with Ident -> Id
- op inConnectionIdentUsePort(_,_,_) :  IdInstance UsePort Connections -> Bool . 
	- isUseiConnections(_,_,_)
	- eq inConnectionIdentUsePort(Id,Use,((Id,Use,Id2,Pro),Lx)) = true  .  
		- eq isUseiConnections(id,u,((id,u)--(id2,p),Cs)) = true  . 
  		- eq isUseiConnections(id,u,Cs) = false [owise] .
 - op inConnectionIdent(_,_) :  IdInstance Connections -> Bool .
 	- isCInstiConnections
 - op connectionProIdent(_,_) :  IdInstance Connections -> Connections .
 	- getConnectionsfCInst
 - op isDisconnect(_) : Connection -> Query [ctor] . 
 	- si on garde tel quel
 	- onDisconnect(_)
 - **REQUEST for me should be MSG_REQ**
 	- op [ dst: _ , query: _ ] : IdInstance Query -> MsgReq [ctor] .
 - **ANSWER for me should be  MSG_ANS**
 	- op [ dst: _ , query: _ , value: _] : IdInstance Query Value -> MsgAns [ctor] .
 - **et un sutype MSG**
 - TransitionEnding
 	- TrEndings
 - op t(_,_) : Place Stations -> Transition [ctor] .
 	- op (_->_) : Place Stations -> Transition [ctor] .
 - op te(_,_) : Transition Station -> TransitionEnding [ctor] .
 	- op (_-e->_) : Transition Station -> TransitionEnding [ctor] .
 - op placesSourceOfTransitions(_) : Transitions -> Places .
 	- op getSourcesOfTransitions(_)
 	- eq getSourcesOfTransitions((p->Ss),Ts)) = p, getSourcesOfTransitions(Ts) .
 	- get all places that are sources of transitions???
 	- voir utilisation
 - op restrictTransitionsToPlace(_,_) : Transitions Place -> Transitions . 
 	- op getTransitionsofPlace
 	- eq getTransitionsofPlace((p->Ss),Ts),p) = (p->Ss), getTransitionsofPlace(Ts,p)  .
 	- enlever l197?
 - op removeTransitionEndingStation(_,_) : TransitionEndings Station -> TransitionEndings . 
 	- rmTesOfStation
 - **op transitionsOfPlacesWithRespectToStations(_,_,_) : Places Transitions Stations -> Transitions .**
 	- ?
 - op transitionEndingsOfOneTransition(_,_) : Transition Stations -> TransitionEndings .
 	- getEndingsofTransition(_,_)
 - op transitionEndingsOfTransitions(_) : Transitions -> TransitionEndings .
 	- getEndingsfTransitions
 - **op isSatisfiedTransitionEndingStation(_,_,_) : Station Transitions TransitionEndings -> Bool .**
 	- ?
 - **op placesOfMarking : Marking -> Places .**
 	- getMarkedPlace
 	- same for all
 - op  intersectionMarkings(_,_) : Marking Marking -> Marking . 
 	- intersectMarkings
 - **BehaviorWithId**
 	- est-ce qu'on ne veut pas identifier le push plutôt que le behavior ?
 - op existIdBehaviorehListBeh(_,_) : IdBehavior List{BehaviorWithId} -> Bool .
 	- isBehaviorinList
 	
# configuration

receivedAnswers -> externState
outgoingRequests -> outgoingQuestions
outgoingAnswers -> pendingQuestions 
buffer -> incomingMsgs

# reset

IdConnectionWhenSendActive -> getIdsForReset
upDateReceivedAnswers -> resetState