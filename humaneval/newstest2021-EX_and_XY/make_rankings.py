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

from scipy.stats import mannwhitneyu

LANG_CODES = {
  "eng" : "English",
  "fra" : "French",
  "deu" : "German",
  "isl" : "Icelandic",
  "zho" : "Chinese",
  "jpn" : "Japanese",
  "ces" : "Czech",
  "rus" : "Russian",
  "hau" : "Hausa",

}

def output_counts(scores):
  totals = scores.groupby(["source", "target"])['system'].count().reset_index()
  systems= scores.groupby(["source", "target"])['system'].nunique().reset_index()
  totals.rename(columns = {'system' : 'annotations'}, inplace=True)
  totals = totals.merge(systems, on = ['source', 'target'])
  totals['mean'] = totals['annotations'] / totals['system']
  #print(totals)
  print(totals)

def add_wins_losses_matched(segment_scores, system_scores):
  """Use the Mann-Whiteny (Wilcoxon sum-ranks) to calculate wins and losses for systems. This
   version uses the matched segments, as in Appraise"""
  # To calculate this, we need a table with tuples of 
  # (source, target, system-A, system-B, doc, segment, mean-score-A, mean-score-B)
  segment_pair_scores = pandas.merge(segment_scores, segment_scores, on = ["source", "target", "segment", "doc"])
  # we do not compare systems to themselves, but do make both pairwise comparisons. Inefficient, but simpler.
  segment_pair_scores = segment_pair_scores[segment_pair_scores['system_x'] !=  segment_pair_scores['system_y']]
  comparisons = segment_pair_scores.groupby(["source", "target", "system_x", "system_y"])\
    [["z_x", "z_y"]].\
    apply(lambda t: mannwhitneyu(t.z_x, t.z_y, alternative="greater").pvalue).reset_index()
    
  # In the Appraise calculations, we only allow system A to win over system B, if system A has a higher
  # z-score than system B, and is significantly better in the mann-whitney test. Because we are only calculating
  # Mann Whitney on a subset of segments, it is possible to have a lower z, but still win on Mann Whitney
  system_pair_scores = pandas.merge(system_scores.reset_index(), system_scores.reset_index(), on = ["source", "target"])
  system_pair_scores['z_win'] = system_pair_scores['z_x'] > system_pair_scores['z_y']
  comparisons = pandas.merge(comparisons, system_pair_scores, on = ["source", "target", "system_x", "system_y"])
  comparisons['win'] = (comparisons[0] < 0.05) & (comparisons['z_win'])
  
  # Count wins and losses, then add to the system_scores table
  win_counts = comparisons.groupby(["source", "target", "system_x"])['win'].sum().reset_index()
  loss_counts = comparisons.groupby(["source", "target", "system_y"])['win'].sum().reset_index()
  system_scores = pandas.merge(system_scores, win_counts,
    left_on = ["source", "target", "system"],
    right_on = ["source", "target", "system_x"],
  )
  system_scores = pandas.merge(system_scores, loss_counts,
    left_on = ["source", "target", "system_x"],
    right_on = ["source", "target", "system_y"],
  )
  system_scores.rename(columns = {'system_y': "system", "win_x":  "wins", "win_y": "losses"}, inplace=True)
  del system_scores['system_x']
  return system_scores

def add_wins_losses_unmatched(segment_scores, system_scores):
  """As in add_wins_losses_matched() but use all judgements for each system pair (not just matched)"""
#     source target      score         z  wins      system  losses
# 0    eng    hau  71.380258 -0.197747     1         AMU      10
# 1    eng    isl  49.958291 -0.611475     1  Allegro.eu      10
# 2    eng    deu  82.369249 -0.391847     0   BUPT_rush      17
# 3    eng    jpn  79.499882  0.085110     8   BUPT_rush       7
# 4    eng    zho  79.977509  0.071395    11   BUPT_rush       6
   
   # Not sure how to do this in pandas, so we build up the wins/losses outside pandas
  segment_scores['key'] = segment_scores['doc'].str.cat(segment_scores['segment'].astype('str'), sep = "_")
  min_prop = 1
  min_prop_name = None
  for pair, df in segment_scores.groupby(["source", "target"]):
    systems = df['system'].unique()
    wins = {s : 0 for s in systems}
    loses = {s : 0 for s in systems}
   
    for i, system_x in enumerate(systems):
      for system_y in systems[i+1:]:
        print (pair, system_x, system_y)
        keys_x = set(df[df.system == system_x]['key'].unique())
        keys_y = set(df[df.system == system_y]['key'].unique())
        intersect = len(keys_x.intersection(keys_y))
        len_x = len(keys_x)
        len_y = len(keys_y)
        prop = min(intersect/len_x, intersect/len_y)
        if prop < min_prop:
          min_prop = prop
          min_prop_name = (pair[0], pair[1], system_x, system_y) 
        print(f"Intersect: {intersect}; len(x): {len_x}; len(y): {len_y}; prop: {prop}")
        
        z_x = df[df.system == system_x]['z']
        z_y = df[df.system == system_y]['z']
  print (min_prop)
  print(min_prop_name)
  sys.exit(0)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-c", "--contrastive", default=False,  action="store_true",
    help = "Compute the rankings with the contrastive assessments (as opposed to the regular DA assessments)")

  parser.add_argument("-o", "--output-format", 
    choices = ["segment", "totals", "system", "tables"], default="system")

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

  if args.output_format == "totals":
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


  system_scores = add_wins_losses_unmatched(segment_scores, system_scores)
  print(system_scores.head())
  sys.exit(0)


  # outputs 
  if args.output_format == "segment":
    segment_scores.sort_values(by = ["source", "target", "system",  "doc"], ascending = False, inplace=True)
    segment_scores.to_csv(sys.stdout, sep="\t")
  elif args.output_format == "system":
    system_scores.sort_values(by = ["source", "target", "z"], ascending = False, inplace=True)
    system_scores['score'] = system_scores['score'].map('{:,.2f}'.format)
    system_scores['z'] = system_scores['z'].map('{:,.3f}'.format)
    system_scores.to_csv(sys.stdout, sep="\t")
  elif args.output_format == "tables":
    # Output the latex tables
    for pair, by_pair in system_scores.groupby(["source", "target"]):
      print(f"[{pair[0]}-->{pair[1]}]")
      by_pair_sorted = by_pair.sort_values(by = "z", ascending = False)
      source = LANG_CODES[pair[0]]
      target = LANG_CODES[pair[1]]

      system_count = len(by_pair_sorted)
      min_wins_current_cluster = system_count
      latex = f"{{\\bf \\tto{{{source}}}{{{target}}} \\\\[0.5mm]\n"
      latex += "\\begin{tabular}{cccrl}\n"
      latex += "& Rank & Ave. & Ave. z & System\\\\ \\hline\n"
      print('Wins                                        System ID  Z Score  R Score')
      for i,row in enumerate(by_pair_sorted.itertuples()):
        print(f"{row.wins:02d} {row.system:>50} {row.z:+2.5f} {row.score:+2.5f}".replace("+"," "))
        min_wins_current_cluster = min(row.wins, min_wins_current_cluster)
        remaining = system_count - (i +1)
        add_cluster_boundary = False
        # We declare a cluster boundary if this system has a win count
        # equal to the number of remaining systems.
        if min_wins_current_cluster == remaining:
          print('-' * 80)
          add_cluster_boundary = True

        top_rank = row.losses + 1
        worst_rank = system_count - row.wins
        
        latex += "\\Uncon{} & "
        latex += f"{top_rank}-{worst_rank} & " if top_rank != worst_rank else f"{top_rank} & "
        latex += f"{row.score:.1f} & "
        latex += f"{row.z:-.3f} & ".replace("+", " ")
        latex += f"{row.system}\\\\ \n".replace('_', '\_')
        if add_cluster_boundary: latex += "\\hline\n" 
        
      latex += "\\hline\n\\end{tabular}"
      print("")
      print(latex)
      print("")
  else:
    raise RuntimeError(f"Output format {args.output_format} not recognised")

if __name__ == "__main__":
  main()

