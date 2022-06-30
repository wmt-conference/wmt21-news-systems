# Description of data collected via Appraise

## source-based DA

All annotations are collected in file `wmt21-regular.20210930.csv`. The column names are following:

 * User ID
 * System Name
 * Segment ID - also sentence number in `Document ID`
 * Quality control item - keep only TGT tokens for most analysis
 * Source Language
 * Target Language
 * Score
 * Document ID
 * Does score represent whole document (or individual segments)
 * Annotation Start
 * Annotation End

 You may want to combine `User ID` with file `Types_of_crowds_for_annotations.csv` to get better knowledge about annotators.

 ## Contrastive DA

 All annotations are in the file `wmt21-contrastive.20211109.csv` with following column names:

 * User ID
 * System filename
 * Line Number - equal to line number in `System filename`
 * Quality control item - keep only TGT tokens for most analysis
 * Source Language
 * Target Language
 * Score
 * Annotation Start
 * Annotation End

 ### Contrastive DA with evaluated sentences

 For metrics evaluation, you may want to check file `wmt21-contrastive-with-sentences.csv`. It has the following structure (keep in mind we removed quality control items):

 * User ID
 * System filename
 * Line Number - equal to line number in `System filename`
 * Source Language
 * Target Language
 * Score
 * Annotation Start
 * Annotation End
 * Barch ID - sentences with the same batch has been evaluated in contrastive manner, where user saw both translations next to each other (score is copied for equal translations)
 * Position of annotation - was the sentence shown as first or second on the screen
 * Source
 * Translation
 * Human reference A

