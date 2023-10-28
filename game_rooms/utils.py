import random

def weighted_random_choices(weighted_options, count):
    options, weights = zip(*weighted_options.items())
    return random.choices(options, weights, k=count)

def assign_roles(players):
    # Mandatory roles that should always be included
    mandatory_roles = ['Mafia','Mafia','Detective']

    # Optional roles with assigned weights (chances)
    optional_roles = {
        'Citizen': 10,
        'Jester': 1,
        'Pimp': 2
    }

    # Counter to keep track of assigned roles
    assigned_roles_counter = {}

    # Check if there are enough players for mandatory roles
    if len(players) < (len(mandatory_roles) + 1):
        raise ValueError('Not enough players for mandatory roles')

    # Calculate remaining player count after assigning mandatory roles
    remaining_players = len(players) - len(mandatory_roles)

    # Initialize list to store optional roles chosen
    optional_roles_chosen = []

    for _ in range(remaining_players):
        # Get a weighted random choice based on current optional_roles
        choice = weighted_random_choices(optional_roles, 1)[0]

        # Update counter
        assigned_roles_counter[choice] = assigned_roles_counter.get(choice, 0) + 1

        # Remove optional role if it's not 'Citizen' and already assigned once
        if choice != 'Citizen' and assigned_roles_counter[choice] >= 1:
            del optional_roles[choice]

        optional_roles_chosen.append(choice)

    # Combine mandatory and optional roles and shuffle
    all_roles = mandatory_roles + optional_roles_chosen
    random.shuffle(all_roles)

    # Assign roles to players
    for i, role in enumerate(all_roles):
        print(players[i]['username'], role)
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

def get_next_state(previous_state,players,most_voted_index):
    
    
    match previous_state:
        case "Night":
            if most_voted_index == None:
                return "Day" , None , {'title': "Doctor's Saving Grace", 'message': 'In a miraculous turn of events, the Doctor successfully intervenes, sparing a life and leaving the town in a rare state of peace.'}
            
            players[most_voted_index]['is_alive'] = False
            player_to_kill = players[most_voted_index]

            if player_to_kill['role'] == 'Jester':
                return "Win-Jester" , most_voted_index , {'title': "Jester's Grand Deception", 'message': 'In a tale of masterful manipulation, the Jester fools the town and wins, leaving both Mafia and Citizens questioning their judgment.'}
            
            #check if mafia has won
            mafia_count = 0
            citizen_count = 0
            for player in players:
                if player['is_alive']:
                    if player['role'] == 'Mafia':
                        mafia_count += 1
                    else:
                        citizen_count += 1
            if mafia_count >= citizen_count:
                return "Win-Mafia" , most_voted_index , {'title': "Mafia's Silent Takeover", 'message': 'The Mafia cunningly eliminates their opposition, seizing control of Palermo under the veil of night.'}
            elif mafia_count == 0:
                return "Win-Citizen" , most_voted_index , {'title': 'Citizen Uprising', 'message': 'The Citizens band together, unmasking the Mafia and restoring justice to their beleaguered town.'}
            
            return "Day" , most_voted_index , {'title': "Midnight Casualty: {}".format(player_to_kill['username']), 'message': 'In the dead of night, {} falls victim to the nefarious plots unfolding in Palermo, leaving the town one step closer to chaos.'.format(player_to_kill['username'])}
        case "Day":

            players[most_voted_index]['is_alive'] = False
            player_to_kill = players[most_voted_index]

            if player_to_kill['role'] == 'Jester':
                return "Win-Jester" , most_voted_index , {'title': "Jester's Grand Deception", 'message': 'In a tale of masterful manipulation, the Jester fools the town and wins, leaving both Mafia and Citizens questioning their judgment.'}
            
            #check if mafia has won
            mafia_count = 0
            citizen_count = 0
            for player in players:
                if player['is_alive']:
                    if player['role'] == 'Mafia':
                        mafia_count += 1
                    else:
                        citizen_count += 1
            if mafia_count >= citizen_count:
                return "Win-Mafia" , most_voted_index , {'title': "Mafia's Silent Takeover", 'message': 'The Mafia cunningly eliminates their opposition, seizing control of Palermo under the veil of night.'}
            elif mafia_count == 0:
                return "Win-Citizen" , most_voted_index , {'title': 'Citizen Uprising', 'message': 'The Citizens band together, unmasking the Mafia and restoring justice to their beleaguered town.'}
            
            return "Night" , most_voted_index , {'title': "Voted out : {} ({})".format(player_to_kill['username'],player_to_kill['role']), 'message': 'Was this a good decision? Only time will tell.'}
        case _:pass
    
    
    return "Night" , most_voted_index , {'title': 'Night', 'message': 'Mafia has chosen a player to kill.'}
    