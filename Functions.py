def gunnerySkillImproveCost(current_skill):
    if current_skill == 6:
        return 50
    elif current_skill == 5:
        return 100
    elif current_skill == 4:
        return 200
    elif current_skill == 3:
        return 400
    elif current_skill == 2:
        return 800
    elif current_skill == 1:
        return 1000
    else:
        return 0
def pilotingSkillImproveCost(current_skill):
    if current_skill == 6:
        return 25
    elif current_skill == 5:
        return 50
    elif current_skill == 4:
        return 100
    elif current_skill == 3:
        return 200
    elif current_skill == 2:
        return 500
    elif current_skill == 1:
        return 750
    else:
        return 0