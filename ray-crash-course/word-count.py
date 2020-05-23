#!/usr/bin/env python
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

def count_words(file_globs, top_n = 100, batch_window = 1024):
    # The working directory of this application may be _different_
    # than the Ray cluster's working directory. (In a real cluster,
    # the files available will be different, too, but we'll ignore
    # the problem here.) So, we need to pass absolute paths or our
    # ray.util.iter.from_items won't find the files!
    globs = [g for f in file_globs for g in glob.glob(f)]
    file_list = list(map(lambda f: os.path.abspath(f), globs))

    print(f'Processing {len(file_list)} files: {file_list}')
    # See also the combine operation, which is for_each(...).flatten(...).
    word_count = (
        ray.util.iter.from_items(file_list, num_shards=4)
           .for_each(lambda f: unzip(f).readlines())
           .flatten()  # converts one record per file will all lines to one record per line.
           .for_each(lambda line: re.split('\W+', line)) # split into words
           .flatten()  # flatten lists of words into one word per record
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
    parser.add_argument('--top-n', metavar='N', type=int, default=100, nargs='?',
        help='How many of the most frequently-occurring words to print')
    parser.add_argument('--batch', metavar='N', type=int, default=1024, nargs='?',
        help='Size of the streaming batch window')
    parser.add_argument('--local', help="Run Ray locally. Default is to join a cluster",
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
