from ..pla.rng import XOROSHIRO

def generate(_rng: XOROSHIRO, npc_count=6):

    __rng = XOROSHIRO(*_rng.seed.copy())

    menu_advances = 0

    for _ in range(npc_count):
        menu_advances += __rng.rand_count(91)[1]
    __rng.next()
    menu_advances += 1 + __rng.rand_count(60)[1]

    return {"menu_advances": menu_advances, "lotto": __rng.rand(10) * 10000 + __rng.rand(10) * 1000 + __rng.rand(10) * 100 + __rng.rand(10) * 10 + __rng.rand(10)}


def filter(result, filter):

    return result['lotto'] in filter


def check_lotto(s0, s1, npc_count, ids):

    predict_advances = 0

    predict = XOROSHIRO(int(s0, 16), int(s1, 16))

    filter = ids.split(',')

    print(filter)

    result = generate(predict, npc_count)

    #print(predict_advances, result)
    #print()

    while str(result['lotto']) not in filter:
        prev_old = predict_advances
        prev = result
        predict_advances += 1
        predict.next()
        result = generate(predict, npc_count)
        
        #previous lotto results and next lotto results
        prev['total'] = prev_old + prev['menu_advances']
        _predict = XOROSHIRO(*predict.seed.copy())
        _predict.next()
        next = generate(_predict, npc_count)
        next['total'] = predict_advances + next['menu_advances'] + 1

    print(f"RNG State: S0: {predict.seed[0]:X}, S1: {predict.seed[1]:X}")
    print(predict_advances, result)
    print()

    return { "adv": predict_advances, "lotto": result['lotto'], "menu_adv": result['menu_advances'], "total": predict_advances + result['menu_advances'] }