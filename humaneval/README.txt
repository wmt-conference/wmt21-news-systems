WMT21 Human evaluation data
------------------------------

The data contained in this package is provided for research purposes only and comes with no guarantee.

If using the following data, please cite the WMT'21 findings paper.


A main purpose of providing this data is to allow participants in the news shared task to verify results
for themselves and to provide data for developing better ways of ranking systems in future evaluations. 
Details of the set up of different annotations are provided in the above paper.

The main data files to look at are:

analysis/ad-latest.csv -- Contains all unfiltered human annotations

analysis/ad-<source language><target language>-good-stnd-redup.csv 
-- eg analysis/ad-csen-good-stnd-redup.csv for czech to english

The above file contains human assessments provided by Mturk workers who passed strict quality control checks, 
where scores are standardised by that human judge's mean and standard deviation score 
(computed over all the judgments they provided). This is the basis of overall scores for systems. 

Overall scores for systems are calculate by computing a micro average over segments (eg analysis/ad-seg-scores-cs-en.csv) 
before an overall average per system (eg analysis/ad-sys-ranking-cs-en-z.csv).
Significance test results are in eg: analysis/ad-DA-diff-wilcoxon-rs-csen.csv

Questions please email graham.yvette@gmail.com or wmt-organisers@inf.ed.ac.uk, please read section 3 of the above paper before contacting, clarification questions or improvement suggestions welcome. The methodology used at WMT is desribed in further detail in the following paper:

@article{NLE:9961497,
  author = {Graham, Yvette and Baldwin, Timothy and Moffat, Alistair and Zobel, Justin},
  title = {Can machine translation systems be evaluated by the crowd alone},
  journal = {Natural Language Engineering},
  volume = {FirstView},
  month = {1},
  year = {2016},
  issn = {1469-8110},
  pages = {1--28},
  numpages = {28},
  doi = {10.1017/S1351324915000339},
  URL = {http://journals.cambridge.org/article_S1351324915000339},
}

The following directory contains human evaluation crowd-sourced on MTurk (to-english language pairs), details in WMT :
mturk-newstest2021-toen

The following directory contains human evaluation data collected by Facebook:
facebook-wikipedia-2021


The following directory contains the out-of-English and fr-de evaluation:
newstest2021-EX_and_XY








