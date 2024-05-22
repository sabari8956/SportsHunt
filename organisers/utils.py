import math
import random
from .models import *
stages_dict = {
    0: '',
    1: 'Finals',
    2: 'Semi Finals',
    3: 'Quater Finals',
    4: 'Round of 16',
    5: 'Round of 32',
}

# class knockoutFixtureGenerator:
#     def __init__(self) -> None:
#         self.bracket = []
#         self.currentWinners = []
    
#     def initialBracket(self, fixture_id):
#         matches = []
#         fixture_instance = Fixtures.objects.get(id= fixture_id)
#         category_instance = fixture_instance.category
#         teams = [team.id for team in category_instance.teams.all()]  
#         n = len(teams)
#         nearest_power_of_2 = 2 ** math.ceil(math.log2(n))
#         byesNeeded = nearest_power_of_2 - n
#         fixture_instance.currentStage = int(math.log2(nearest_power_of_2))
#         byes = ['BYE'] * byesNeeded
#         teams_without_byes = [t for t in teams if t != 'BYE']
#         random.shuffle(teams_without_byes)

#         teams = []
#         for i in range(len(byes)):
#             teams.append(teams_without_byes[i])
#             teams.append('BYE')
        
#         teams.extend(teams_without_byes[len(byes):])
        
#         for i in range(0, nearest_power_of_2, 2):
#             team1 = Team.objects.get(id=teams[i])
#             if teams[i+1] == 'BYE':
#                 match = Match.objects.create(
#                     match_no= (i/2)+1 ,
#                     match_category = category_instance,
#                     team1= team1,
#                     team2= None,
#                     winner= team1,
#                     match_state= True
#                 )
#             else:
#                 match = Match.objects.create(
#                     match_no= (i/2)+1,
#                     match_category = category_instance,
#                     team1= team1,
#                     team2= Team.objects.get(id=teams[i+1]),
#                 )
#             matches.append(match)
        
#         for match_instance in matches:
#             if match_instance.team2 == None:
#                 fixture_instance.currentWinners.add(match_instance.winner)
#             else:
#                 fixture_instance.currentBracket.add(match_instance)
        
#         category_instance.fixture = fixture_instance
#         fixture_instance.save()
#         category_instance.save()
        
#         return True

#     def nextBracket(self, fixture_id):
#         fixture_instance = Fixtures.objects.get(id= fixture_id)
#         winners = [team.id for team in fixture_instance.currentWinners.all()]
        
#         if fixture_instance.currentBracket.exists():
#             raise Exception("All matches are not completed")

#         print("winners are", winners, fixture_instance.currentStage)
#         if len(winners) == 1:
#             fixture_instance.currentStage -= 1
#             fixture_instance.category.winner = Team.objects.get(id=winners[0])
#             fixture_instance.save()
#             print("winner is", winners)
#             return winners
        
#         print("winners are", winners)
#         fixture_instance.currentBracket.clear()
#         fixture_instance.currentWinners.clear()
#         nearest_power_of_2 = 2 ** math.ceil(math.log2(len(winners)))
        
#         for i in range(0, nearest_power_of_2, 2):
#             match = Match.objects.create(
#                 match_no= (i/2)+1,# here we have a issue with match_no
#                 match_category = fixture_instance.category,
#                 team1= Team.objects.get(id=winners[i]),
#                 team2= Team.objects.get(id=winners[i+1]),
#             )
#             fixture_instance.currentBracket.add(match)
        
#         fixture_instance.currentStage -= 1
#         fixture_instance.save()
        
#         return True

#     def add_winners(self, fixture_id, winner):
#         # print("still match has to be transfered to ongoing matches") its done
#         fixture_instance = Fixtures.objects.get(id= fixture_id)
#         category_instance = fixture_instance.category
#         tournament_instance = category_instance.tournament
#         # bracket = fixture_instance.currentBracket.all()
#         tournament_instance = fixture_instance.category.tournament
#         onGoingMatches = tournament_instance.onGoing_matches.all()
#         status = False
        
#         for match in onGoingMatches:
#             if winner == match.team1.id or winner == match.team2.id:
#                 status = True
#                 fixture_instance.currentWinners.add(winner)
#                 tournament_instance.onGoing_matches.remove(match)
#                 break
        
#         if not status:
#             raise Exception("Winner not found in current bracket")
        
#         thisfixture_onGoingMatches = [match for match in tournament_instance.onGoing_matches.all() if match.match_category == category_instance]
#         print('thisfixture_onGoingMatches', thisfixture_onGoingMatches)
#         if not thisfixture_onGoingMatches:
#             print('going to next bracket')
#             self.nextBracket(fixture_instance.id)
#         return status




class KnockOutFixture:
    def __init__(self):
        # self.ttl_grps = []
        ...
        
    def initialBracket(self, fixture_id):
        matches = []
        fixture_instance = Fixtures.objects.get(id= fixture_id)
        category_instance = fixture_instance.category
        teams = [team.id for team in category_instance.teams.all()]
        n = len(teams)
        nearest_power_of_2 = 2 ** math.ceil(math.log2(n))
        byesNeeded = nearest_power_of_2 - n
        cur_lvl =  math.ceil(math.log2(n)) -1 # cos starts from 0 ...
        fixture_instance.currentStage = cur_lvl
        random.shuffle(teams)
        
        teamsByes = []
        for i in range(byesNeeded):
            teamsByes.append(teams[i])
            teamsByes.append('BYE')
            
        teamsByes.extend(teams[byesNeeded:])
        
        lvl_grp = [f"{cur_lvl}-{i}" for i in range(nearest_power_of_2 // 2)]
        # makelvl JSON
        ttl_grps = []
        teams_names = [team.name for team in category_instance.teams.all()] # [ team names ]l

        self.makeLvlJSON(lvl_grp, cur_lvl, ttl_grps, teamsByes)
        
        for i in range(0, nearest_power_of_2, 2):
            team1 = Team.objects.get(id=teamsByes[i])
            if teamsByes[i+1] == 'BYE':
                match = Match.objects.create(
                    match_no= (i/2)+1 ,
                    match_category = category_instance,
                    team1= team1,
                    team2= None,
                    winner= team1,
                    match_state= True
                )
            else:
                match = Match.objects.create(
                    match_no= (i/2)+1,
                    match_category = category_instance,
                    team1= team1,
                    team2= Team.objects.get(id=teamsByes[i+1]),
                )
            matches.append(match)
        
        # removing BYEs , declaring winners
        for match_instance in matches:
            if match_instance.team2 == None:
                fixture_instance.currentWinners.add(match_instance.winner)
            else:
                fixture_instance.currentBracket.add(match_instance)
                
        
        # promote BYE winners in JSON 
        for match in ttl_grps:
            if match.get('player2') == 'BYE':
                for thing in ttl_grps:
                    if thing['key'] == match['parent']:
                        _, m_key = match['key'].split('-')
                        m_key = (int(m_key) % 2) + 1
                        thing[f'player{m_key}'] = match['player1']
                        thing[f'p{m_key}_Id'] = match['p1_Id']
                        
        
        
        #saving the changes
        fixture_instance.fixture = ttl_grps
        category_instance.fixture = fixture_instance
        fixture_instance.save()
        category_instance.save()
        
        
        return True
    
    def makeLvlJSON(self, lvl_grp, cur_lvl, ttl_grps, teams):
        cur_lvl -= 1
        parent_keys = []
        parent_number = 0
        # teams = [team.name() for team in category_instance.teams.all()] # [ team names ]

        for i, level in enumerate(lvl_grp):
            if parent_number == 0:
                parent = f"{cur_lvl}-{len(parent_keys)}"
                parent_keys.append(parent)
            if teams is not None:
                p1 = teams[i * 2]
                p2 = teams[i * 2 + 1]
                p1_name = f'{[mem.name for mem in Team.objects.get(id=p1).members.all()]}'
                p2_name = p2
                if p2 != 'BYE':
                    p2_name = f'{[mem.name for mem in Team.objects.get(id=p2).members.all()]}'
                # self.bracket.append([p1, p2])
                ttl_grps.append({"key": level, "parent": parent,"p1_Id": p1, "p2_Id": p2, "player1": p1_name, "player2": p2_name, "parentNumber": parent_number})
            else:
                ttl_grps.append({"key": level, "parent": parent, "parentNumber": parent_number})
            parent_number = (parent_number + 1) % 2
            
        if cur_lvl >= 0:
            self.makeLvlJSON(parent_keys, cur_lvl, ttl_grps, None)    
    
    def nextBracket(self, fixture_id):
        fixture_instance = Fixtures.objects.get(id= fixture_id)
        winners = [team.name for team in fixture_instance.currentWinners.all()]
        
        if fixture_instance.currentBracket.exists():
            raise Exception("All matches are not completed")



        fixtureJSON = fixture_instance.fixture
        currentStage = fixture_instance.currentStage -1 
        
        if len(winners) == 1:
            fixture_instance.currentStage -= 1
            fixture_instance.category.winner = Team.objects.get(id=winners[0])
            fixture_instance.save()
            return winners
        
        fixture_instance.currentWinners.clear()
        winners_match = [[  entry.get('p1_Id', ''), entry.get('p2_Id', '')] for entry in fixtureJSON if entry['key'].startswith(f'{currentStage}-')]
        
        
        for i, match in enumerate(winners_match):
            if match[0] == '' or match[1] == '':
                print("PLAYER NAME EMPTY")
                return False
            
            match_instance = Match.objects.create(  
                match_no= (i/2)+1,# here we have a issue with match_no
                match_category = fixture_instance.category,
                team1= Team.objects.get(id=match[0]),
                team2= Team.objects.get(id=match[1]),
            )
            fixture_instance.currentBracket.add(match_instance)
        
        fixture_instance.currentStage -= 1
        fixture_instance.save()
        
        return True
    
    def add_winners(self, fixture_id, winner):
        
        fixture_instance = Fixtures.objects.get(id= fixture_id)
        category_instance = fixture_instance.category
        tournament_instance = category_instance.tournament
        tournament_instance = fixture_instance.category.tournament
        onGoingMatches = tournament_instance.onGoing_matches.all()
        status = False
        
        for match in onGoingMatches:
            if match.team1.id == winner or match.team2.id == winner:
                status = True
                fixture_instance.currentWinners.add(winner)
                tournament_instance.onGoing_matches.remove(match)
                # update winner in json
                self.updateWinnerJSON(winner, fixture_id)
                break  # Move the break statement here
        
        if not status:
            raise Exception("Winner not found in current bracket")
        
        
        thisfixture_onGoingMatches = [match for match in tournament_instance.onGoing_matches.all() if match.match_category == category_instance]
        if not thisfixture_onGoingMatches:
            self.nextBracket(fixture_instance.id)
        return status
    
    def updateWinnerJSON(self, winner, fixture_id):
        fixture_instance = Fixtures.objects.get(id= fixture_id)
        fixtureJSON = fixture_instance.fixture
        cur_lvl = fixture_instance.currentStage
        
        found = False
        
        for match in fixtureJSON:
            lvl = int(match['key'].split('-')[0])
            if lvl == cur_lvl:                
                p1_Id = int(match.get('p1_Id', '-1'))
                p2_Id = match.get('p2_Id', '-1')
                if not p2_Id == 'BYE':
                    p2_Id = int(p2_Id)
                
                if p1_Id == winner or p2_Id == winner:
                    found = True
                    break
        
        if not found:
            raise Exception("Winner not found in JSON")
        
        parent_key = match['parent']
        m_key = (int(match['key'].split('-')[1]) % 2) + 1
        
        for parent_node in fixtureJSON:
            if parent_node['key'] == parent_key:
                parent_node[f'player{m_key}'] = f'{[mem.name for mem in Team.objects.get(id=winner).members.all()]}'
                parent_node[f'p{m_key}_Id'] = winner
                break
            
        
        fixture_instance.fixture = fixtureJSON
        fixture_instance.save()
        
        return True
