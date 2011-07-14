xweka
=====

**xweka** is a collection of command-line tools to complement the `weka <http://www.cs.waikato.ac.nz/ml/weka/>`_ machine-learning toolkit:

- **weka-convert** (formerly *table2ARFF*) is a utility to convert a tab-delimited training set into a proper ARFF format. It offers various filtering options to remove attributes or instances.

- **weka-parse** parses the raw output from classification and regression models and extract all scores. It can then save those scores as JSON objects or CSV files.

- **weka-run** (formerly *MetaClassify*) run all classification or regression models compatible with a given training set, then aggregate the resulting scores into various CSV-formatted reports.

- **weka-list** lists all classification and regression models compatible (and incompatible) with a given training set.

Contact
-------

Aurelien Mazurie
ajmazurie@oenone.net
http://ajmazurie.oenone.net/
