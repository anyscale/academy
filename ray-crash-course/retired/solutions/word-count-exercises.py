#!/usr/bin/env python

# The combined solution for the exercises for the Parallel Iterators lesson.

import glob, gzip, re, sys, os
import numpy as np
import ray

class WordCount:
    "Wraps a dictionary of words and counts."
    def __init__(self):
        self.counts = {}

    def __call__(self, word, increment):
        count = increment
        if word in self.counts:
            count = self.counts[word]+increment
        self.counts[word] = count
        return (word, count)

    def sort_counts(self, descending=True):
        "Returns a generator of word-count pairs sorted by count."
        return (wc for wc in sorted(self.counts.items(), key = lambda wc: wc[1], reverse=descending))

def unzip(f):
    if f.endswith(".gz"):
        return gzip.open(f)
    else:
        return open(f, 'r')

# Exercise 3: Remove stop words. Edit this set to taste!
stop_words1 = {
    'that', 'the', 'this', 'an',
    'and', 'or', 'but', 'of'
}
## All the single digits and ASCII letters:
l=[str(i) for i in range(10)]
l.extend([chr(i) for i in range(ord('a'), ord('z')+1)])

stop_words = stop_words1.union(set(l))

def is_stop_word(word):
    """
    Treat all single-character words, blanks, and integers as stop words.
    (Try adding floating point numbers.)
    Otherwise, check for membership in a set of words.
    We use a set because it provides O(1) lookup!
    """
    w = word.strip()
    if len(w) <= 1 or w.isdigit():
        return True
    return w in stop_words

def count_words(file_globs, top_n = 100, batch_window = 1024):
    # The working directory of this application may be _different_
    # than the Ray cluster's working directory. (In a real cluster,
    # the files available will be different, too, but we'll ignore
    # the problem here.) So, we need to pass absolute paths or our
    # ray.util.iter.from_items won't find the files!
    globs = [g for f in file_globs for g in glob.glob(f)]
    file_list = list(map(lambda f: os.path.abspath(f), globs))

    print(f'Processing {len(file_list)} files: {file_list}')
    # Exercise 1: use combine instead of for_each(...).flatten(...).
    # We replace two occurrences:
    word_count = (
        ray.util.iter.from_items(file_list, num_shards=4)
           .combine(lambda f: unzip(f).readlines())
           # Exercise 2: convert to lower case!
           .combine(lambda line: re.split('\W+', line.lower())) # split into words.
           # Exercise 3: remove stop words.
           .filter(lambda word: not is_stop_word(word))
           .for_each(lambda word: (word, 1))
           .batch(batch_window)
    )
    # Combine the dictionaries of counts across shards with a sliding window
    # of "batch_window" lines.
    wordCount = WordCount()
    for shard_counts in word_count.gather_async():
        for word, count in shard_counts:
            wordCount(word, count)
    sorted_list_iterator = wordCount.sort_counts()
    return [sorted_list_iterator.__next__() for i in range(top_n)]

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Word Count using Ray Parallel Iterators")
    parser.add_argument('files', metavar='file', type=str, nargs='+',
                        help='file globs to process')
    parser.add_argument('-n', '--top-n', metavar='N', type=int, default=100, nargs='?',
        help='How many of the most frequently-occurring words to print')
    parser.add_argument('-b', '--batch', metavar='N', type=int, default=1024, nargs='?',
        help='Size of the streaming batch window')
    parser.add_argument('-l', '--local', help="Run Ray locally. Default is to join a cluster",
        action='store_true')

    args = parser.parse_args()
    print(f"""
        {parser.description}
        files:        {args.files}
        Top N:        {args.top_n}
        Batch size:   {args.batch}
        Run locally?  {args.local}
        """)
    if args.local:
        ray.init()
    else:
        ray.init(address='auto')
    print(count_words(args.files, top_n=args.top_n, batch_window=args.batch))


if __name__ == '__main__':
    main()
