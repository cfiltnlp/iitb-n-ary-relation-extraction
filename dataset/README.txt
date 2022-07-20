This file contains the details about the following: 
1. Scripts for converting the original annotations in the datasets (3 datasets, MUC: MUC-6, BB: Bacteria Biotope and DGM: Drug-Gene-Mutation) to the format (RIGD level) required by our approach
2. Evaluation scripts used for each of these datasets

============================================================
Annotation conversion scripts:
============================================================

Our annotation format (RIGD-level) requires following 3 files for each annotated document:

1. DOC_NAME.txt : File containing actual text content

2. DOC_NAME_instances.txt : File containing the information about entities for the document DOC_NAME.txt. Each line in this file has following format-
EntityType <TAB> entity_mention
e.g.
PER	Bert-Olof Svanholm
POST	chairman
PER	Mr. Svanholm
....

3. DOC_NAME_relation_instances.txt : File containing the relation mentions for each relation type of interest for the document DOC_NAME.txt. Each line in this file has following format-
RelationType <TAB> entity_mention1 <TAB> entity_mention2 ...
e.g.
SUCCESSION	Volvo	chairman	Pehr G. Gyllenhammar	Mr. Svanholm
...

Following are the details for creating such annotations for the three datasets.

================================
MUC-6 dataset:

Original MUC-6 dataset can be downloaded from LDC website (https://catalog.ldc.upenn.edu/LDC2003T13)

script name: convert_annotations_MUC.py
parameters:
1. MUC-6 keys file (for "train" partition: \muc6\data\keys\formal-trng.st.key.02oct95; for "test" partition: \muc6\data\keys\formal-tst.ST.key.09oct95)  
2. MUC-6 texts file (for "train" partition: \muc6\data\texts\ie.formal.training.texts; for "test" partition: \muc6\data\texts\ie.formal.test.texts)
3. Output Folder to store annotations in required format (an empty folder should exist already)

=================================
Bacteria Biotope dataset:

Download the original dataset from http://2016.bionlp-st.org/tasks/bb2

script name: convert_annotations_BB.py
parameters:
1. Input folder with the original annotations (for "train" partition : BioNLP-ST-2016_BB-event+ner_train; for "dev" partition: BioNLP-ST-2016_BB-event+ner_dev)
2. Output Folder to store annotations in required format (an empty folder should exist already)

==================================
Drug-Gene-Mutation dataset:

Download the original dataset from http://hanover.azurewebsites.net/

script name: convert_annotations_DGM.py
parameters:
1. Input JSON file (\0\data_graph or \1\data_graph or \2\data_graph or \3\data_graph or \4\data_graph)
2. Output Folder to store annotations in required format (an empty folder should exist already)
3. Known drugs list (known_drugs.txt)
4. Known genes list (known_genes.txt)
5. Known variants list (known_variants.txt)
6. Fold (can be 0 or 1 or 2 or 3 or 4)

The script has to run once for all five partions (0 to 4). For 5-fold cross-validation, one of the partitions is used as test set while other 4 are combined to form the training set.


============================================================
============================================================
Evaluation scripts:
============================================================

Gold annotations are kept in a folder where each file DOC_NAME_relation_instances.txt has the format as explained above.

Predicted relations are kept is folder where each file DOC_NAME_relation_instances.txt is produced in exactly the same format.

Each evaluation script takes following 3 parameters:
1. Path to the gold annotations folder
2. Path to the predicted relations folder
3. Results file (to store the evaluation results)

1. MUC-6 dataset:
evaluate_at_RIGD_level_MUC.py

2. Bacteria Biotope dataset:
evaluate_at_RIGD_level_BB.py

3. Drug-Gene-Mutation dataset:
evaluate_at_RIGD_level_DGM.py
evaluate_at_mention_level_DGM.py
