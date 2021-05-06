import time
import json
from kombilo.kombiloNG import *
from kombilo.sgf import Cursor

def point2move(x, y):
    offset = ord('a')
    return chr(x + offset) + chr(y + offset)

def move2index(move, size=19):
    offset = ord('a')
    return ord(move[0]) - offset + (ord(move[1]) - offset) * 19

def pattern_search(sgf, num=float('inf'), disable_alphago_vs_alphago=False):
    K = KEngine()
    K.gamelist.DBlist.append({'sgfpath': './DB/Community', 'name':('./DB/Community', 'kombilo'), 'data': None, 'disabled': 0})
    K.gamelist.DBlist.append({'sgfpath': './DB/Master', 'name':('./DB/Master', 'kombilo'), 'data': None, 'disabled': 0})
    K.gamelist.DBlist.append({'sgfpath': './DB/qipu/201406', 'name':('./DB/qipu/201406', 'kombilo'), 'data': None, 'disabled': 0})
    K.gamelist.DBlist.append({'sgfpath': './DB/qipu/2015', 'name':('./DB/qipu/2015', 'kombilo'), 'data': None, 'disabled': 0})
    K.gamelist.DBlist.append({'sgfpath': './DB/cgibo', 'name':('./DB/cgibo', 'kombilo'), 'data': None, 'disabled': 0})
    K.loadDBs()

    c = Cursor(sgf)
    node = c.getRootNode(0)
    n = 0
    while not c.atEnd and n < num:
        node = c.next()
        if 'B' in node or 'W' in node:
            n += 1
    K.patternSearch(K.get_pattern_from_node(node, selection=[[0, 0], [18, 18]], ptype=FULLBOARD_PATTERN), lk.SearchOptions(1, 0))
    # TODO - get_pattern_from_nodeはFULLBOARD_PATTERNは想定してなさそうなコードだから、上記のようにworkaroundで動かすより直したほうがいい。
    if disable_alphago_vs_alphago:
        K.gameinfoSearch("NOT(PB = 'AlphaGo' AND PW = 'AlphaGo')")
    return K

def search_formatter(K):
    K.gamelist.showDate = 1
    total = K.gamelist.noOfGames()
    oldest = K.gamelist.get_data(0)
    for i in range(total):
        data = K.gamelist.get_data(i)
        if not '0000-00-00' in data: # 日付がわかっている最も古いもの
            oldest = data
            break
    if total > 0:
        return {
            'total': total,
            'games': list(map(lambda i: K.gamelist.get_data(i), range(total - 1, max(0, total - 20) - 1, -1))),
            'oldest': oldest,
            'latest': K.gamelist.get_data(total - 1),
            'nextMoves': list(map(lambda c: {
                'coord': point2move(c.x, c.y),
                'num': c.B or c.W
            }, K.continuations))
        }
    else:
        return {
            'total': total
        }

if __name__ == '__main__':
    disable_alphago_vs_alphago = sys.argv[1] == '--disable_alphago_vs_alphago'
    if sys.argv[-1] == '-':
        f = sys.stdin
    else:
        f = open(sys.argv[-1])
    print(json.dumps(search_formatter(pattern_search(f.read(), disable_alphago_vs_alphago=disable_alphago_vs_alphago))))
