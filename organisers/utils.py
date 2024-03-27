import math
import random

stages_dict = {
    0: '',
    1: 'Finals',
    2: 'Semi Finals',
    3: 'Quater Finals',
    4: 'Round of 16',
    5: 'Round of 32',
}

class knockoutFixtureGenerator:
    """
    we will have to create a fixture model
    store data like
        initial bracket,
        like stage (3[quater finals],2[semi finals],1[finals]) in all matches,
        winners of stage, each stage will have a winners
    """
    def __init__(self) -> None:
        self.bracket = []
        self.currentStage = 0
        self.currentWinners = []
    
    def initialBracket(self, teams):
        n = len(teams)
        nearest_power_of_2 = 2 ** math.ceil(math.log2(n))
        byesNeeded = nearest_power_of_2 - n
        self.currentStage = int(math.log2(nearest_power_of_2))
        
        byes = ['BYE'] * byesNeeded
        teams_without_byes = [t for t in teams if t != 'BYE']
        random.shuffle(teams_without_byes)

        teams = []
        for i in range(len(byes)):
            teams.append(teams_without_byes[i])
            teams.append('BYE')
        
        teams.extend(teams_without_byes[len(byes):])
        
        for i in range(0, nearest_power_of_2, 2):
            self.bracket.append((teams[i], teams[i+1]))
        
        print(f"Raw_bracket {self.bracket} \n")
        bye_winners = []
        for match in self.bracket:
            if match[1] == 'BYE':
                bye_winners.append(match[0])
        
        for winner in bye_winners:
            self.add_winners(winner)
        return self.bracket

    def nextBracket(self, winners):
        
        print("\n",stages_dict[self.currentStage -1 ], '\n\n')
        if not self.bracket == []:
            raise Exception("All matches are not completed")

        if len(winners) == 1:
            self.currentStage -= 1
            print("winner is", winners)
            return winners
        
        print("winners", winners)
        random.shuffle(winners)
        self.bracket = []
        self.currentWinners = []
        nearest_power_of_2 = 2 ** math.ceil(math.log2(len(winners)))
        byesNeeded = nearest_power_of_2 - len(winners)
        winners.extend(['BYE'] * byesNeeded)
        
        for i in range(0, nearest_power_of_2, 2):
            self.bracket.append((winners[i], winners[i+1]))
        self.currentStage -= 1
        
        for match in self.bracket:
            if match[1] == 'BYE':
                self.add_winners(match[0])
                break
            elif match[0] == 'BYE':
                self.add_winners(match[1])
                break
        return self.bracket

    def add_winners(self, winner):
        status = False
        for match in self.bracket:
            if winner in match:
                status = True
                self.bracket.remove(match)
                self.currentWinners.append(winner)
                break
        
        if not status:
            raise Exception("Winner not found in current bracket")
        return status

fixture = knockoutFixtureGenerator()
fixture.initialBracket([1,2,3,4,5,6,7,8,9])

while fixture.currentStage != 0:
    while fixture.bracket:
        print(f"Bracket Matches {fixture.bracket}")
        n = int(input("Enter winner: "))
        fixture.add_winners(n)
        if not fixture.bracket:
            break
    
    print(f"Current bracket winners: {fixture.currentWinners}")
    
    fixture.nextBracket(fixture.currentWinners)


"""
Ready to resume plan

the current problems are
    1. doesn't work for odd number of teams for some reason [9]✅
    2. a issue is that if 3 teams are in semi finals [1,2,3] and 
        [1,2] plays 3 gets bye, then 3 will be in finals without playing a match✅
        
    3. whatif a team plays with same team again and again?[wrong question, it's not possible]
    4. whatif a team gets bye in every stage?✅
    
    MAIN ISSUE: 
        As of now i have code that BYE plays with BYE in stages that a bad idea [indeed it was a bad idea]
"""