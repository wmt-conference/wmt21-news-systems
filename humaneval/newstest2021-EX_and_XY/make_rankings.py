#!/usr/bin/env python3

#
# Calculate the rankings, as shown in the overview paper.
# This is not the actual script used for the paper, but it creates the same scores
# as used in the updated version of the overview paper.
#

import argparse
import pandas
import sys

def output_counts(scores):
  pass

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-s", "--segment", default=False,  action="store_true",
    help = "Output segment-level scores (not system level)")
  parser.add_argument("-c", "--contrastive", default=False,  action="store_true",
    help = "Compute the rankings with the contrastive assessments (as opposed to the regular DA assessments)")
  parser.add_argument("-t", "--totals", default=False, action="store_true",
    help = "Output total numbers of systems and judgements, rather than scores")
  args = parser.parse_args()
  
  csv_file = "wmt21-regular.20210930.csv"
  if args.contrastive:
    csv_file = "wmt21-contrastive.20211109.csv"
  scores = pandas.read_csv(csv_file, header = None,
    names = ["annotator", "system", "segment", "class", "source", "target", "score", "doc", 8, 9, 10])
  scores = scores[scores['class'] == 'TGT']

  if args.totals:
    output_counts(scores)

  # To compute z-scores, we need mean and std dev for each annotator-language_pair combination
  meanstds = scores.groupby(["annotator", "source", "target"])["score"].agg(["mean", "std"]).reset_index()
  scores = pandas.merge(scores, meanstds, on = ["annotator", "source", "target"])
  scores['z'] = (scores['score'] - scores['mean']) / scores['std']


  # Compute means, by first computing a segment mean, then mean across all segments (for a system-LP combo)
  # Note that removing "doc" from the following line reproduces the (incorrect) scores from
  # the first version of the paper
  segment_scores = scores.groupby(["system", "segment", "doc", "source", "target"])[["score", "z"]].mean().reset_index()
  system_scores = segment_scores.groupby(["system", "source", "target"])[['score', 'z']].mean()


  # outputs 
  if args.segment:
    segment_scores.sort_values(by = ["source", "target", "system",  "doc"], ascending = False, inplace=True)
    segment_scores.to_csv(sys.stdout, sep="\t")
  else:
    system_scores.sort_values(by = ["source", "target", "z"], ascending = False, inplace=True)
    system_scores['score'] = system_scores['score'].map('{:,.2f}'.format)
    system_scores['z'] = system_scores['z'].map('{:,.3f}'.format)
    system_scores.to_csv(sys.stdout, sep="\t")

if __name__ == "__main__":
  main()

