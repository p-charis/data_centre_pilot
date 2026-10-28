# IRaMuTeQ text corpora

Files contain complete articles selected from the FORSEE French and Irish newspaper corpora because their raw text includes a data-centre term. The standard exports contain 642 French and 154 Irish articles. `FR_data_centres_all_excluding_les_echos.txt` contains the same French selection without Les Échos (348 articles).

Selection is an OR search on raw article text after probable-duplicate removal: French terms cover *centre(s) de données*, *data center/centre(s)* and *centre(s) informatique(s)*; Irish terms cover *data center/centre(s)* and *server farm(s)*. Articles retain their original IRaMuTeQ metadata and full text; a `*dcid_...` tag links each text to its source article. Theme vocabulary and the 500-character proximity rule do not determine inclusion.

To recreate the files, run `python3 analyse.py` and `python3 prepare_iramuteq.py` from `data_centre_pilot`.
