#!/usr/bin/env python3

#
# Calculate the rankings, as shown in the overview paper.
# This is not the actual script used for the paper, but it creates the same scores
# as used in the updated version of the overview paper.
#
# To reproduce the scores from the updated version, use the -d -z arguments. This 
# will be fixed in a further update to the paper. In other words, the paper should
# be updated so that it alignes with the script results, when the script is run
# without arguments.
#

import argparse
import pandas
import sys

def output_counts(scores):
  totals = scores.groupby(["source", "target"])['system'].count().reset_index()
  systems= scores.groupby(["source", "target"])['system'].nunique().reset_index()
  totals.rename(columns = {'system' : 'annotations'}, inplace=True)
  totals = totals.merge(systems, on = ['source', 'target'])
  totals['mean'] = totals['annotations'] / totals['system']
  #print(totals)
  print(totals)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-c", "--contrastive", default=False,  action="store_true",
    help = "Compute the rankings with the contrastive assessments (as opposed to the regular DA assessments)")

  parser.add_argument("-s", "--segment", default=False,  action="store_true",
    help = "Output segment-level scores (not system level)")
  parser.add_argument("-t", "--totals", default=False, action="store_true",
    help = "Output total numbers of systems and judgements, rather than scores")

  # Document-level scores are different from segment-level scores, so it is recommended
  # that they are not averaged together. Also, the document level scores may have been 
  # mixed with bad reference scores.
  parser.add_argument("-d", "--include-doc-scores", default=False, action="store_true",
    help = "Include document-level judgements")

  # Annotators with zero standard deviation are unreliable, and cannot be normalised reliably
  # so we exclude by default.
  parser.add_argument("-z", "--include-zero-std-annotators", default=False, action="store_true",
    help = "Include annotators with zero standard deviation")

  args = parser.parse_args()
  
  csv_file = "wmt21-regular.20210930.csv"
  if args.contrastive:
    csv_file = "wmt21-contrastive.20211109.csv"
  scores = pandas.read_csv(csv_file, header = None,
    names = ["annotator", "system", "segment", "class", "source", "target", "score", "doc", "doc_score", 9, 10])
  scores = scores[scores['class'] == 'TGT']

  # Remove doc scores
  if not args.include_doc_scores:
    scores  = scores[scores['doc_score'] == False]

  if args.totals:
    output_counts(scores)
    sys.exit(0)

  # To compute z-scores, we need mean and std dev for each annotator-language_pair combination
  meanstds = scores.groupby(["annotator", "source", "target"])["score"].agg(["mean", "std"]).reset_index()
  scores = pandas.merge(scores, meanstds, on = ["annotator", "source", "target"])

  # Remove any annotators with zero mean and standard deviation across the pair
  if not args.include_zero_std_annotators:
    scores = scores[scores['std'] > 0]

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

