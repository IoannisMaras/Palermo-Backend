import random

def weighted_random_choices(choices, k):
    total = sum(weight for choice, weight in choices.items())
    results = []
    for _ in range(k):
        r = random.uniform(0, total)
        upto = 0
        for choice, weight in choices.items():
            if upto + weight >= r:
                results.append(choice)
                break
            upto += weight
    return results

def assign_roles(players):
    # Mandatory roles that should always be included
    mandatory_roles = ['Mafia','Detective']

    # Optional roles with assigned weights (chances)
    optional_roles = {
        'Citizen': 5,
        'Jester': 2,
    }

    # Check if there are enough players for mandatory roles
    if len(players) < len(mandatory_roles):
        raise ValueError('Not enough players for mandatory roles')

    # Calculate remaining player count after assigning mandatory roles
    remaining_players = len(players) - len(mandatory_roles)
    
    # Get weighted optional roles for remaining players
    optional_roles_chosen = weighted_random_choices(optional_roles, remaining_players)

    # Combine mandatory and optional roles and shuffle
    all_roles = mandatory_roles + optional_roles_chosen
    random.shuffle(all_roles)

    # Assign roles to players
    for i, role in enumerate(all_roles):
        players[i]['role'] = role

    return players

def decide_the_voted(players):
    
    voted_index = [0 for i in range(len(players))]
    
    for player in players:
        if player['vote'] != None:
            voted_index[player['vote']] += 1
    
    #check if two or more players have the same number of votes
    if voted_index.count(max(voted_index)) > 1:
        return None
    
    return voted_index.index(max(voted_index))

def get_next_state(players,most_voted_index):
    
    player_to_kill = players[most_voted_index]
    
        
    
    
    return "Night" , None , 'Test'
    