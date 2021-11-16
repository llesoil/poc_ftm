# How to test it on a new software system? 

## Selection of the project

For now, it only works with .go projects.

## Requirements

You'll need jupyter notebook and a python environment. 
The easy way to install these is to download Anaconda here : https://docs.conda.io/en/latest/
Install tree-sitter with this command line in a cell `!pip3 install tree_sitter`
Install GraphViz with `conda install -c anaconda graphviz`
(Optional) Install treelib with `conda install -c conda-forge treelib`

## How does it work?

The `Main.ipynb` notebook exploits the json files in the `config` directory, executes the analysis of feature toggles and stores the results in the `results` directory.

Each json file of the `config` directory corresponds to a software system,  e.g. `./config/juju.json` for https://github.com/juju/juju

## How to write your own configuration file

The format is json ( see https://en.wikipedia.org/wiki/JSON)

We list hereafter the list of arguments you **must** add in the configuration file:

- `directory`  the directory of the project e.g. `./juju` for the software system Juju
- `url` the url of the github project. If nothing exists in the previously defined `directory`, the program will launch a `git clone url`, assuming that it will be downloaded in `directory`. For instance, `url` is equal to https://github.com/juju/juju for Juju.
- `feature_structure` the way the program expresses feature toggles. It acts as a filter to avoid keeping false positives. For instance, in the case of Juju, the program uses `features.TheNameOfTheFeatureToggle.enabled()` to define a feature toggle, so we stick to `features.`. Leave it empty if you do not want to filter the statements.

For several projects (e.g. Kops & Juju) we automatically extract the names of the feature toggles with a regular expression, based on a file listing all the feature toggles. If you want to do so, just add : 
-`reg_exp` the format of your regular expression
- `ft_file` the path of the file containing all the feature toggle names (aka keywords to search)
If it is too complicated to automate the process, you can just tell the program what keywords it has to search for, with:
- `keywords` a table of string, the names of the feature toggles

You **have to** specify either `keywords` or (`reg_exp` and `ft_file`).

Please consult the json files of the `config` directory for working examples.

