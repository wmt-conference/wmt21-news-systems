#!/usr/bin/env python3

#
# Calculate the rankings, as shown in the overview paper.
# This is not the actual script used for the paper, but does create the same scores and rankings
#

import pandas
import sys


def main():
  scores = pandas.read_csv("wmt21filtered.20210930.csv", header = None,
    names = ["annotator", "system", "segment", "class", "source", "target", "score", "doc", 8, 9, 10])
  scores = scores[scores['class'] == 'TGT']


  # To compute z-scores, we need mean and std dev for each annotator-language_pair combination
  meanstds = scores.groupby(["annotator", "source", "target"])["score"].agg(["mean", "std"]).reset_index()
  scores = pandas.merge(scores, meanstds, on = ["annotator", "source", "target"])
  scores['z'] = (scores['score'] - scores['mean']) / scores['std']


  # Compute means, by first computing a segment mean, then mean across all segments (for a system-LP combo)
  segment_scores = scores.groupby(["system", "segment",  "source", "target"])[["score", "z"]].mean().reset_index()
  system_scores = segment_scores.groupby(["system", "source", "target"])[['score', 'z']].mean()


  # outputs 
  system_scores.sort_values(by = ["source", "target", "z"], ascending = False, inplace=True)
  system_scores['score'] = system_scores['score'].map('{:,.2f}'.format)
  system_scores['z'] = system_scores['z'].map('{:,.3f}'.format)
  system_scores.to_csv(sys.stdout, sep="\t")

if __name__ == "__main__":
  main()
