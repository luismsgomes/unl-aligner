#! /usr/bin/env python3
'''                         UNL aligner
                2009 Luís Gomes <luismsgomes@gmail.com>

Bibliography:

    Parallel Texts Alignment.
    Luís Gomes.
    MSc Thesis, Universidade Nova de Lisboa, 2009

    Longest Sorted Sequence Algorithm for Parallel Text Alignment.
    Tiago Ildefonso and José Gabriel Pereira Lopes.
    In Computer Aided Systems Theory – EUROCAST 2005, pages 81-90, 2005

    Cognates Alignment.
    António Ribeiro, Gaël Dias, Gabriel Lopes, and João Mexia.
    In Machine Translation Summit 2001 (MTS-2001).
'''

import collections
import itertools
import sys


ENCODING="UTF-8"


def read_text(filename):
    with open(filename, 'rt', encoding=ENCODING, errors='ignore') as lines:
        lines = list(map(str.split, lines))
        for line in lines: line.append('\\n')
        return list(itertools.chain.from_iterable(lines))


def get_words_by_freq(text):
    freqs_by_word = collections.Counter(text)
    words_by_freq = collections.defaultdict(set)
    for word, freq in freqs_by_word.items():
        words_by_freq[freq].add(word)
    return words_by_freq


def pairs_of_words_with_same_freq(text_x, text_y):
    words_by_freq_x = get_words_by_freq(text_x)
    words_by_freq_y = get_words_by_freq(text_y)
    for freq in words_by_freq_x.keys() & words_by_freq_y.keys():
        words_x, words_y = words_by_freq_x[freq], words_by_freq_y[freq]
        for word_x, word_y in itertools.product(words_x, words_y):
            yield word_x, word_y


def filter_by_spelling_similarity(pairs, simfun, minsim):
    return (pair for pair in pairs if simfun(*pair) >= minsim)


def lis(seq, keyfn=lambda value: value):
    ''' Longest Increasing Subsequence
    >>> seq = [0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15]
    >>> lis(seq)
    [0, 2, 6, 9, 11, 15]
    >>> lis([])
    []
    '''
    if not seq: return seq

    # tail[k] stores the position i of the smallest value seq[i] such that 
    # there is an increasing subsequence of length (k+1) ending at seq[i]
    tail = []
    # prev[k] stores the position i of the rightmost seq[i] such that
    # seq[i] < seq[k]
    prev = []
    for i in range(len(seq)):
        # find the rightmost tail[k] such that seq[tail[k]] < seq[i]
        # TODO: bisect tail instead of linear scan
        for k in range(len(tail)-1, -1, -1):
            if keyfn(seq[tail[k]]) < keyfn(seq[i]):
                if len(tail) == k+1:
                    tail.append(i)
                elif keyfn(seq[tail[k+1]]) > keyfn(seq[i]):
                    tail[k+1] = i
                prev.append(tail[k])                    
                break
        else:
            tail.append(i)
            prev.append(None)

    i = tail[-1]
    subseq = [seq[i]]
    while prev[i] is not None:
        i = prev[i]
        subseq.append(seq[i])
    subseq.reverse()
    return subseq


def ed(s1, s2):
    '''Edit Distance

    >>> ed('', ''), ed('a', 'a'), ed('','a'), ed('a', ''), ed('a!a', 'a.a')
    (0, 0, 1, 1, 1)

    This implementation takes only O(min(|s1|,|s2|)) space.
    '''
    m, n = len(s1), len(s2)
    if m < n:
        m, n = n, m         # ensure n <= m, to use O(min(n,m)) space
        s1, s2 = s2, s1
    d = list(range(n+1))
    for i in range(m):
        p = i
        d[0] = i+1
        for j in range(n):
            t = 0 if s1[i] == s2[j] else 1
            p, d[j+1] = d[j+1], min(p+t, d[j]+1, d[j+1]+1)
    return d[n]


def ned(s1, s2): return ed(s1, s2) / max(1, len(s1), len(s2))


_edsim_cache = {}
def edsim(s1, s2):
    if s1 == s2: return 1.0
    sim = _edsim_cache.get((s1, s2), None)
    if sim is None:
        sim = 1.0 - ned(s1, s2)
        _edsim_cache[(s1, s2)] = sim
    return sim


def align(text_x, text_y, simfun, mincpl, minsim, maxrec, reclevel=0):
    if reclevel > maxrec:
        yield ' '.join(text_x), ' '.join(text_y), '!'
        return
    cands = list(pairs_of_words_with_same_freq(text_x, text_y))
    if minsim == 1.0:
        cands = [(wx, wy) for wx, wy in cands if wx == wy]
    elif mincpl > 0:
        cands = [(wx, wy) for wx, wy in cands if wx[:mincpl] == wy[:mincpl]]
    if 0.0 < minsim < 1.0:
        cands = list(filter_by_spelling_similarity(cands, simfun, minsim))
    pos_by_word_x = collections.defaultdict(list)
    pos_by_word_y = collections.defaultdict(list)
    for pos, word in enumerate(text_x): pos_by_word_x[word].append(pos)
    for pos, word in enumerate(text_y): pos_by_word_y[word].append(pos)
    points = [zip(pos_by_word_x[word_x], pos_by_word_y[word_y])
              for word_x, word_y in cands]
    points = list(itertools.chain.from_iterable(points))
    if not points:
        yield ' '.join(text_x), ' '.join(text_y), '?'
        return
    points.sort()
    anchors = lis(points, keyfn=lambda point: (point[1], point[0]))
    x1, y1 = 0, 0
    for x2, y2 in anchors:
        if x2 > x1 or y2 > y1:
            for seg in align(text_x[x1:x2], text_y[y1:y2],
                             simfun, mincpl, minsim, maxrec, reclevel + 1):
                yield seg
        yield text_x[x2], text_y[y2], reclevel
        x1, y1 = x2 + 1, y2 + 1
    remainder_x, remainder_y = text_x[x1:], text_y[y1:]
    if remainder_x or remainder_y:
        for seg in align(remainder_x, remainder_y,
                         simfun, mincpl, minsim, maxrec, reclevel + 1):
            yield seg


def error(template, *args, **kwargs):
    print(template.format(*args, **kwargs), file=sys.stderr)


def usage(progname):
    error('\nUsage: {} TEXT_X TEXT_Y OUTPUT MINCPL MINSIM MAXREC\n', progname)
    error('\tTEXT_X and TEXT_Y are the filenames of the input texts')
    error('\tOUTPUT is the filename of the output file')
    error('\tMINCPL (minimum common prefix length) is a positive integer value')
    error('\tMINSIM (minimum similarity) is a decimal value between 0.0 and 1.0')
    error('\tMAXREC (maximum recursion depth) is a positive integer value')
    error('\tInput texts should be UTF-8 encoded.  Output file will also be UTF-8.')
    error('\nExample:\n{} en.txt pt.txt enpt.txt 3 .6 10\n', progname)


if __name__ == '__main__':
    import doctest
    doctest.testmod()    
    if len(sys.argv) != 7:
        usage(sys.argv[0])
        sys.exit(1)
    mincpl = int(sys.argv[4])
    minsim = float(sys.argv[5])
    if not 0.0 <= minsim <= 1.0:
        error('minsim must be a value between 0.0 and 1.0.')
        sys.exit(1)
    simfun = edsim if minsim < 1.0 else lambda s1, s2: 1.0 if s1 == s2 else 0.0
    maxrec = int(sys.argv[6])
    text_x, text_y = read_text(sys.argv[1]), read_text(sys.argv[2])
    with open(sys.argv[3], "wt", encoding=ENCODING) as output:
        for segment in align(text_x, text_y, simfun, mincpl, minsim, maxrec):
            print(*segment, sep='\t', file=output)

