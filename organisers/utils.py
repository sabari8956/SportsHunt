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

class knockoutFixtureGenerator:
    def __init__(self) -> None:
        self.bracket = []
        self.currentWinners = []
    
    def initialBracket(self, fixture_id):
        matches = []
        fixture_instance = Fixtures.objects.get(id= fixture_id)
        category_instance = fixture_instance.category
        teams = [team.id for team in category_instance.teams.all()]
        n = len(teams)
        nearest_power_of_2 = 2 ** math.ceil(math.log2(n))
        byesNeeded = nearest_power_of_2 - n
        fixture_instance.currentStage = int(math.log2(nearest_power_of_2))
        byes = ['BYE'] * byesNeeded
        teams_without_byes = [t for t in teams if t != 'BYE']
        random.shuffle(teams_without_byes)

        teams = []
        for i in range(len(byes)):
            teams.append(teams_without_byes[i])
            teams.append('BYE')
        
        teams.extend(teams_without_byes[len(byes):])
        
        for i in range(0, nearest_power_of_2, 2):
            team1 = Team.objects.get(id=teams[i])
            if teams[i+1] == 'BYE':
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
                    team2= Team.objects.get(id=teams[i+1]),
                )
            matches.append(match)
        
        for match_instance in matches:
            if match_instance.team2 == None:
                fixture_instance.currentWinners.add(match_instance.winner)
            else:
                fixture_instance.currentBracket.add(match_instance)
        
        category_instance.fixture = fixture_instance
        fixture_instance.save()
        category_instance.save()
        
        return True

    def nextBracket(self, fixture_id):
        fixture_instance = Fixtures.objects.get(id= fixture_id)
        winners = [team.id for team in fixture_instance.currentWinners.all()]
        
        if fixture_instance.currentBracket.exists():
            raise Exception("All matches are not completed")

        if len(winners) == 1:
            fixture_instance.currentStage -= 1
            fixture_instance.save()
            print("winner is", winners)
            return winners
        
        random.shuffle(winners)

        fixture_instance.currentBracket.clear()
        fixture_instance.currentWinners.clear()
        nearest_power_of_2 = 2 ** math.ceil(math.log2(len(winners)))
        
        for i in range(0, nearest_power_of_2, 2):
            match = Match.objects.create(
                match_no= (i/2)+1,# here we have a issue with match_no
                match_category = fixture_instance.category,
                team1= Team.objects.get(id=winners[i]),
                team2= Team.objects.get(id=winners[i+1]),
            )
            fixture_instance.currentBracket.add(match)
        
        fixture_instance.currentStage -= 1
        fixture_instance.save()
        
        return True

    def add_winners(self, fixture_id, winner):
        fixture_instance = Fixtures.objects.get(id= fixture_id)
        bracket = fixture_instance.currentBracket.all()
        status = False
        
        
        
        for match in bracket:
            if winner == match.team1.id or winner == match.team2.id:
                status = True
                fixture_instance.currentWinners.add(winner)
                fixture_instance.currentBracket.remove(match)
                break
        
        if not status:
            raise Exception("Winner not found in current bracket")
        
        if not fixture_instance.currentBracket.exists():
            print('going to next bracket')
            self.nextBracket(fixture_instance.id)
        return status

if __name__ == "__main__":
    fixture = knockoutFixtureGenerator()
    fixture.initialBracket([1,2,3,4,5,6,7,8,9])

    while fixture.currentStage != 0:
        while fixture.bracket:
            n = int(input("Enter winner: "))
            fixture.add_winners(n)
            if not fixture.bracket:
                break
                
        fixture.nextBracket(fixture.currentWinners)


        """
        next plan
        
        1] add all the self bracket, winner data to the fixture instance✅
            Now automatically call nextBracket if no more teams in curent bracket,✅
        2] update nextBracket to use with db✅
        3] update add_winners to use with db✅
        4] update api/views.py to use the fixture generator properly.✅
        """