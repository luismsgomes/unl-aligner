# unl-aligner


## Description

This program implements the algorithm described in (Ildefonso and Lopes, 2005) for aligning parallel texts using the Longest Increasing Subsequence. That method has evolved from (Ribeiro, Dias, Lopes, and Mexia, 2001). You can find a brief description of these methods in section 2.2.2 of (Gomes, 2009).

Please note that this is not an implementation of my own method for parallel texts alignment but instead an implementation of a state-of-the-art method from the paper (Ildefonso and Lopes, 2005).  It diverges from the algorithm described in that paper in a minor detail: whenever there are multiple Increasing Subsequences with the same length, this implementation chooses the leftmost while the paper prescribes selecting the righmost.

## Usage

Command syntax:

    ./unl-aligner.py TEXT_X TEXT_Y MINCPL MINSIM MAXREC

The parameters `TEXT_X` and `TEXT_Y` are the texts to be aligned. Tokenization of the texts is of your responsability. The program assumes that tokens are separated by spaces.

`MINCPL` is a positive integer value. It is the minimum common prefix length that a pair of words must have to be considered as possible cognate.

`MINSIM` is a decimal value between 0 and 1. It is the minimum spelling similarity that a pair of words must have to be considered as possible cognate.

`MAXREC` is the maximum depth of recursion allowed.

Example usage:

    $ cat English.txt

Our ordinary measures of distance fail us here in the realm of the galaxies .
We need a much larger unit : the light year .
It measures how far light travels in a year, nearly 10 trillion kilometers .

    $ cat Portuguese.txt

As nossas habituais medidas de distância falham-nos aqui no reino das galáxias .
Precisamos de uma unidade bastante maior : o ano-luz .
Ele mede a distância que a luz percorre durante um ano , cerca de 10 biliões de quilómetros .

    $ ./unl-aligner.py English.txt Portuguese.txt 3 .6 10 | column -s $'\t' -t

    Our ordinary measures of              As nossas habituais medidas de            ?
    distance                              distância                                 1
    fail us here in the realm of the      falham-nos aqui no reino das              ?
    galaxies                              galáxias                                  0
    .                                     .                                         0
    \n                                    \n                                        0
    We need a much larger unit            Precisamos de uma unidade bastante maior  ?
    :                                     :                                         0
    the light year                        o ano-luz                                 ?
    .                                     .                                         0
    \n                                    \n                                        0
    It measures how far light travels in  Ele mede a distância que                  ?
    a                                     a                                         0
    year, nearly                          luz percorre durante um ano , cerca de    ?
    10                                    10                                        0
    trillion kilometers                   biliões de quilómetros                    ?
    .                                     .                                         0
    \n                                    \n                                        0

The third column may contain either an integer value, a question mark (?), or an exclamation mark (!):

    An integer value indicates that the segment contains a pair of words that were considered possible cognates. The value indicates the recursion depth at which the alignment was made.
    A question mark (?) indicates that the segment could not be further refined, ie. could not be split into finer segments.
    An exclamation mark (!) indicates that the maximum recursion depth was reached and thus a finer alignment of that segment was not attempted. 

## License

This code is released under a Creative Commons Attribution 3.0 Unported License.

## Bibliography

If you use this program in your research, please cite:

Parallel Texts Alignment.
Luís Gomes.
MSc Thesis, Universidade Nova de Lisboa, 2009
([pdf](http://run.unl.pt/bitstream/10362/2051/1/Gomes_2009.pdf), [bibtex](https://research.variancia.com/pubs/mscthesis.bib))

