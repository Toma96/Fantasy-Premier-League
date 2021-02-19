import csv
from collections import Counter


players_by_positions = {'GK': 2, 'DEF': 5, 'MID': 5, 'FW': 3}

FORMATIONS = [(3, 4, 3), (3, 5, 2), (4, 3, 3), (4, 4, 2), (4, 5, 1), (5, 4, 1), (5, 3, 2)]


def add_player_to_team(player, team, budget_left, constraints):
    team.add(player)
    budget_left -= player.value
    constraints[player.club] += 1
    players_by_positions[player.pos] -= 1
    return team, budget_left, constraints


def print_pretty_formation(team, formation):
    attackers = 0
    if formation[2] == 1:
        print("\t\t\tO\t\t\t")
        print("\t\t\t{0}\t\t\t".format(team[-1].name))
        attackers = 1
    elif formation[2] == 2:
        print("\t\t\t\t\tO\t\t\t\tO\t\t")
        print("\t\t\t\t{0}\t\t\t\t{1}\t\t".format(team[-1].name, team[-2].name))
        attackers = 2
    elif formation[2] == 3:
        print("\t\t\t\tO\t\t\tO\t\t\tO\t")
        print("\t\t\t{0}\t\t{1}\t\t\t{2}\t".format(team[-1].name, team[-2].name, team[-3].name))
        attackers = 3

    if formation[1] == 3:
        print("\tO\tO\tO\t")
        print("\t{0}\t{1}\t{2}\t".format(team[-attackers-1].name, team[-attackers-2].name, team[-attackers-3].name))
    elif formation[1] == 4:
        print("\t\tO\t\t\tO\t\t\t\tO\t\t\tO\t")
        print("\t{0}\t{1}\t\t{2}\t\t{3}\t".format(team[-attackers-1].name, team[-attackers-2].name,
                                              team[-attackers-3].name, team[-attackers-4].name))
    elif formation[1] == 5:
        print("\tO\t\t\tO\t\t\tO\t\t\tO\t\t\tO\t")
        print("{0}\t\t{1}\t\t{2}\t{3}\t\t{4}\t".format(team[-attackers - 1].name, team[-attackers - 2].name,
                                                   team[-attackers - 3].name, team[-attackers - 4].name,
                                                   team[-attackers - 5].name))

    if formation[0] == 3:
        print("\t\t\tO\t\t\t\tO\t\t\t\tO\t")
        print("\t{0}\t{1}\t\t\t{2}\t".format(team[1].name, team[2].name, team[3].name))
    elif formation[0] == 4:
        print("\tO\tO\tO\tO\t")
        print("\t{0}\t{1}\t{2}\t{3}\t".format(team[1].name, team[2].name, team[3].name, team[4].name))
    elif formation[0] == 5:
        print("\tO\t\t\tO\t\t\tO\t\t\tO\t\t\tO\t")
        print("\t{0}\t{1}\t{2}\t\t{3}\t\t{4}\t".format(team[1].name, team[2].name,
                                                       team[3].name, team[4].name, team[5].name))

    print("\t\t\t\t\t\t\tO\t\t\t\t\t")
    print("\t\t\t\t\t\t{0}\t\t\t\t\t".format(team[0].name))


class Player:

    def __init__(self, id, pos, name, club, points, value):
        self.id = id
        self.pos = pos
        self.name = name
        self.club = club
        self.points = points
        self.value = value

    def __repr__(self):
        return self.name + " " + self.pos + " " + self.club + " " + str(self.points) + " " + str(self.value)


if __name__ == '__main__':

    no_instance = int(input("Please select the number of instance (1, 2 or 3): "))
    csv_file = 'instance' + str(no_instance) + '.csv'
    slicing_step = 17 if no_instance == 1 else 6       # explanation on line 123 !

    my_team = set()
    starting_budget = 100
    clubs_constraints = Counter()

    goalkeepers_db = []
    defenders_db = []
    midfielders_db = []
    forwards_db = []
    all_players = []

    #  1. READING FROM FILE AND COLLECTING DATA  #

    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=['ID', 'pos', 'name', 'club', 'points', 'value'])
        for row in reader:
            player = Player(row['ID'], row['pos'], row['name'], row['club'], float(row['points']), float(row['value']))
            all_players.append(player)
            if row['pos'] == "GK":
                goalkeepers_db.append(player)
            elif row['pos'] == "DEF":
                defenders_db.append(player)
            elif row['pos'] == "MID":
                midfielders_db.append(player)
            else:
                forwards_db.append(player)


    #  2. Finding the weakest players to put into team as substitutes  #

    weakest_gk = sorted(goalkeepers_db, key=lambda p: p.value)[0]
    my_team, starting_budget, clubs_constraints = add_player_to_team(weakest_gk, my_team, starting_budget, clubs_constraints)

    max_benched_by_position = {'DEF': 3, 'MID': 2, 'FW': 2}
    bench_counter = 0
    for weak_player in sorted(all_players, key=lambda p: p.value):
        pos = weak_player.pos
        if pos != 'GK':
            if (players_by_positions[pos] - 1) > max_benched_by_position[pos]:
                my_team, starting_budget, clubs_constraints = add_player_to_team(weak_player, my_team, starting_budget,
                                                                             clubs_constraints)
                bench_counter += 1
            if bench_counter == 3:
                break


    #  3. Greedy algorithm to find the first eleven (greedy by points)

    for pos_no, database in zip(players_by_positions.values(), [goalkeepers_db, defenders_db, midfielders_db, forwards_db]):
        player_counter = 0
        # We are slicing through the possible players in order to reduce the search space for greedy algorithm.
        # I've tried a couple of different slicing steps, it turns out the best (final points in the end) are
        # 17 for instance1 and 6 for instance2
        for player_to_add in sorted(database, key=lambda p: p.points, reverse=True)[::slicing_step]:
            if player_to_add not in my_team and starting_budget > player_to_add.value and player_counter < pos_no:
                if clubs_constraints[player_to_add.club] >= 3:
                    continue
                my_team.add(player_to_add)
                player_counter += 1
                clubs_constraints[player_to_add.club] += 1
                starting_budget -= player_to_add.value

    # 4. CHECK THE CURRENT SOLUTION GIVEN BY THE GREEDY ALGORITHM  #

    print("My team:")
    print(my_team)
    print()
    print("Number of players in team: {0}".format(len(my_team)))
    print("Budget left: {0}".format(starting_budget))
    sum_points = 0
    for player in my_team:
        sum_points += player.points
    print("Total points (whole team): {0}".format(sum_points))

    my_goalkeepers = []
    my_defenders = []
    my_midfielders = []
    my_forwards = []

    starting_eleven = []

    for player in my_team:
        if player.pos == "GK":
            my_goalkeepers.append(player)
        elif player.pos == "DEF":
            my_defenders.append(player)
        elif player.pos == "MID":
            my_midfielders.append(player)
        else:
            my_forwards.append(player)
    my_goalkeepers.sort(key=lambda x: x.points, reverse=True)
    my_defenders.sort(key=lambda x: x.points, reverse=True)
    my_midfielders.sort(key=lambda x: x.points, reverse=True)
    my_forwards.sort(key=lambda x: x.points, reverse=True)
    print("\nTeam by positions:")
    print(my_goalkeepers)
    print(my_defenders)
    print(my_midfielders)
    print(my_forwards)


    #  5. FIND THE BEST POSSIBLE FORMATION  #

    last_max_points = 0
    best_formation = (4, 4, 2)
    for formation in FORMATIONS:
        starting_eleven.append(my_goalkeepers[0])
        total_points = my_goalkeepers[0].points

        for i in range(formation[0]):
            starting_eleven.append(my_defenders[i])
            total_points += my_defenders[i].points
        for j in range(formation[1]):
            starting_eleven.append(my_midfielders[j])
            total_points += my_midfielders[j].points
        for k in range(formation[2]):
            starting_eleven.append(my_forwards[k])
            total_points += my_forwards[k].points

        if total_points > last_max_points:
            last_max_points = total_points
            best_eleven = starting_eleven.copy()
            best_formation = formation

        starting_eleven.clear()

    print(best_eleven)
    print("Starting eleven points: {0}".format(last_max_points))
    print_pretty_formation(best_eleven, best_formation)

    all_players_dict = {'GK': goalkeepers_db, 'DEF': defenders_db, 'MID': midfielders_db, 'FW': forwards_db}
    total_points = last_max_points


    #     7. LOCAL SEARCH     #

    while True:
        player_replacements = []

        for i in range(11):
            player_to_remove = best_eleven[i]
            position = player_to_remove.pos

            for player in sorted(all_players_dict[position], key=lambda p: p.points, reverse=True):
                if starting_budget >= (player.value - player_to_remove.value) and clubs_constraints[player.club] < 3 and player not in my_team:
                    if (total_points + player.points - player_to_remove.points) > last_max_points:
                        player_replacements.append((player_to_remove, player, player.points - player_to_remove.points, i))

        if len(player_replacements) > 0:
            player_replacements.sort(key=lambda p: p[2], reverse=True)

            player_to_remove = player_replacements[0][0]
            player_to_add = player_replacements[0][1]
            best_eleven[player_replacements[0][3]] = player_to_add

            my_team.remove(player_to_remove)
            my_team.add(player_to_add)
            clubs_constraints[player_to_remove.club] -= 1
            clubs_constraints[player_to_add.club] += 1
            starting_budget -= (player_to_add.value - player_to_remove.value)
            total_points += player_to_add.points - player_to_remove.points
            last_max_points = total_points
            print(total_points)
            print(starting_budget)
            print("Player {0} replaced by player {1}".format(player_to_remove, player_to_add))
        else:
            break


    #  8. PRINT FINAL CHOSEN FORMATION, PLAYERS' IDS AND TOTAL POINTS

    print_pretty_formation(best_eleven, best_formation)

    for player in best_eleven:
        print(player.id, end=',')
    for player in my_team:
        if player not in best_eleven:
            print(player.id, end=',')

    print("Total points: ", last_max_points)









