from ..pla.rng import XOROSHIRO

def filt(result, filter):
    if filter['isSafariSport'] and not result['isSafariSport']:
        return False
    elif filter['isBonusCount'] and not result['isBonusCount']:
        return False
    elif filter['isApricorn'] and not result['ballRoll'] == 99 and not result['isSafariSport']:
        return False
    else:
        return True

def ball_type(ball_roll):
    if ball_roll == 99:
        ball_type = "Apricorn Ball"
    elif ball_roll < 99 and ball_roll >= 75:
        ball_type = "Shop Ball 2"
    elif ball_roll < 75 and ball_roll >= 50:
        ball_type = "Shop Ball 1"
    elif ball_roll < 50 and ball_roll >= 25:
        ball_type = "Great Ball"
    else:
        ball_type = "Pokeball"

    return ball_type

def generate(_rng: XOROSHIRO, npc_count = 21):
    __rng = XOROSHIRO(*_rng.seed.copy())
    #menu close advances
    menu_advances = 0

    
    for _ in range(npc_count):
        menu_advances += __rng.rand_count(91)[1]
    __rng.next()
    menu_advances += 1
    menu_advances += __rng.rand_count(91)[1]

    s0, s1 = __rng.seed


    #Jam the Cram

    item_roll = __rng.rand(4)
    ball_roll = __rng.rand(100)
    is_safari_sport = __rng.rand(1000) == 0
    if is_safari_sport or ball_roll == 99:
        is_bonus_count = __rng.rand(1000) == 0
    else:
        is_bonus_count = __rng.rand(100) == 0

    return {"menuAdvances": menu_advances, "itemRoll": item_roll, "ballRoll": ball_roll, "isSafariSport": is_safari_sport, "isBonusCount": is_bonus_count, "balltype": ball_type(ball_roll),
            "s0": s0,
            "s1": s1}

def predict_cram(seed_s0, seed_s1, npc_count, filter):
    rng = XOROSHIRO(int(seed_s0, 16), int(seed_s1, 16))
    predict = XOROSHIRO(int(seed_s0, 16), int(seed_s1, 16))

    advances = -1

    predict_advances = 0

    print(f"State {rng.state:016x}")
    print(f"isSafariSport Filter: {filter['isSafariSport']}, isBonusCount Filter: {filter['isBonusCount']}, Apricorn Filter: {filter['isApricorn']}")
    print("Finding Target...")

    result = generate(predict, npc_count)

    #print(f"State {rng.state:016x}")
    #print("Finding Target...")

    while not filt(result, filter):
        predict_old = predict_advances
        predict_advances += 1
        predict.next()
        prev = result
        prev["adv"] = predict_old
        result = generate(predict, npc_count)
        _predict = XOROSHIRO(*predict.seed.copy())
        predict_new = predict_advances +1
        next = generate(_predict, npc_count)
        next["adv"] = predict_new
        #print(f"Predict State: {predict.seed[0]:X}, {predict.seed[1]:X}")
        #print(predict_advances, result)
        #print()
    
    last = 0

    print ("Prediction:")
    print(f"Predict State: {predict.seed[0]:X}, {predict.seed[1]:X}")
    print(predict_advances, result)
    print()

    return { "adv": predict_advances,
            "isSafariSport": result['isSafariSport'],
            "bonus": result['isBonusCount'],
            "menu_adv": result['menuAdvances'],
            "ballroll": result['ballRoll'],
            "total": predict_advances+result['menuAdvances'],
            "balltype": result['balltype'],
            "s0": result['s0'],
            "s1": result['s1'],
            "prev": prev,
            "next": next }