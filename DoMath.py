from random import randrange, random

class DoMath(object):
    
    def build_candidate(self, summoner_data):
        # Build a team of champions from the champion pools of the summoners we are checking
        # Returns the team if all roles are accounted for, or None if not

        team = []
        for summoner in summoner_data:
            selection = randrange(len(summoner_data[summoner]))
            # champ_to_add is a tuple where [0]=champ-name [1]=id, [2]=role, [3]=points, [4]=summoner-playing
            champ_to_add = summoner_data[summoner][selection]
            team.append(champ_to_add)

        # Make sure we have a valid team, and return None if we don't
        return self.validate_team(team)

    def populate_generation(self, summoner_data, count):
        # Creates <count> valid (not None) candidate teams and adds them t a list

        generation = []
        while len(generation) < count:
            candidate = self.build_candidate(summoner_data)
            if candidate is not None:
                generation.append(candidate)

        return generation

    def fitness(self, candidate):
        # Sums the mastery score total for all of the champions selected in a candidate team

        # champ is a tuple where [0]=champ-name [1]=id, [2]=role, [3]=points, [4]=summoner-playing
        return sum( [champ[3] for champ in candidate ] )

    def grade_generation(self, population):
        # Gives the average score of all the candidate teams in a generation

        generation_score = sum( [self.fitness(candidate) for candidate in population] )
        return generation_score / len(population)

    def evolve(self, population, retain=0.25, random_select=.06):
        # Evolves the generation to get a better team

        # Create a list of tuples (score, team)
        scored = [ (self.fitness(candidate), candidate) for candidate in population]
        # Sort it by score but then throw away the score because I don't care anymore
        scored = [team_tuple[1] for team_tuple in sorted(scored, reverse=True)]
        # Keep the top retain%
        num_keepers = int(len(population) * retain)
        parents = scored[:num_keepers]

        # Avoid local maxmimum by randomly keeping some of the low scorers
        for candidate in scored[num_keepers:]:
            if random_select > random():
                parents.append(candidate)

        # Create next generation candidates using parents
        parents_length = len(parents)
        need_to_create = len(population) - parents_length
        children = []
        while len(children) < need_to_create:
            dad = randrange(parents_length)
            mom = randrange(parents_length)
            if dad != mom:
                dad = parents[dad]
                mom = parents[mom]
                half = int(len(dad) / 2)
                child = dad[:half] + mom[half:]
                if self.validate_team(child) is None:
                    need_to_create -= 1
                    continue
                children.append(child)

        parents.extend(children)
        return parents

    def mutate(self, population, summoner_data, mutate=.01):
        # Introduce mutation to better avoid locals

        for team in population:
            if mutate > random():
                team_test = None
                while team_test is None:
                    # Pick a person to mutate on
                    pos_to_mutate = randrange(len(team))
                    # Mutate them by selecting a new champ for them
                    # Remember the tuple has [0]=champ-name [1]=id, [2]=role, [3]=points, [4]=summoner-playing
                    mutating_summoner = team[pos_to_mutate][4]
                    new_selection = randrange(len(summoner_data[mutating_summoner]))
                    new_champ = summoner_data[mutating_summoner][new_selection]
                    team[pos_to_mutate] = new_champ
                    team_test = self.validate_team(team)

        return population

    def validate_team(self, team):
        # Make sure that a candidate team has exactly one of each summoner, one of each role, and one of each
        # champion. Remember the tuple has [0]=champ-name [1]=id, [2]=role, [3]=points, [4]=summoner-playing

        champions = {info[0] for info in team}
        roles = {info[2] for info in team}
        players = {info[4] for info in team}

        if len(champions) == 5 and len(roles) == 5 and len(players) == 5:
            return team
        else:
            return None
