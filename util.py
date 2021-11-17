"""Utils for Feature toggle miner
"""

import os
import json
import re


CONFIGURATION_FILE_PATH = "config"


def read_file(filename):
    """Read the file and return its content.

    :param filename: file to read
    :param type: String
    """

    content = ""
    with open(filename, 'r') as ffile:
        content = ffile.read()
    return content


class ConfigFile:
    """Class of a configuration file. A configuration file has a Json
    format in which are defined the following properties of the project:

    :param config_filename: filename of the configuration file
    :param type: String
    """

    def __init__(self, config_filename):
        self._config = f"{CONFIGURATION_FILE_PATH}/{config_filename}.json"
        self._keywords = None
        self._ft_file = None
        self._directory = ""
        self._url = ""
        self._feature_toggle_token = ""
        self._extract_config()



    def _extract_config(self):
        """Extract data from the configuration file and sets variables
        """
        with open(self._config, 'r') as jsonconfig:
            data_dict = json.load(jsonconfig)
        self._directory = data_dict["directory"]
        self._url = data_dict["url"]
        self._feature_toggle_token = data_dict["feature_structure"]
        self._kw_case(data_dict)

    def _kw_case(self, dict_data):
        """Manage the case where the configuration file does not have the variable
        "keywords" set. We have to take the regex and retrieve the feature
        toggle keywords in "ft_file"

        :param dd: dictionary representing the json file
        :param type: Dict
        """
        if "keywords" in dict_data:
            self._keywords = dict_data["keywords"]
        else:
            self._ft_file = dict_data["ft_file"]
            regexp = dict_data["reg_exp"]
            sep = None
            if "sep_reg_exp" in dict_data:
                sep = dict_data["sep_reg_exp"]
            self._keywords = self._extract_kw_from_ft_file(regexp, sep)


    def _extract_kw_from_ft_file(self, regexp, sep):
        """Extract the keywords from the feature toggle file using the given regex.
        Called from _kw_case only.

        :param regexp: regex of the feature toggles token
        :param type: String
        :param sep: regexp separator
        :param type: String
        :return: list of keywords
        :rtype: List
        """
        with open(self._ft_file, 'r') as fft:
            catch_feat = re.findall(regexp, fft.read())
        if sep:
            keywords = [feature.split(sep)[1] for feature in catch_feat]
        else:
            keywords = list(catch_feat)

        return keywords


    def get_directory(self):
        """Return the directory of the project

        :return: directory
        :rtype: String
        """
        return self._directory


    def get_keywords(self):
        """Return the the list of feature toggles keywords of the project

        :return: List of keywords
        :rtype: List
        """

        return self._keywords


    def get_feature_toggle_token(self):
        """Return the feature toggle token

        :return: feature toggle token
        :rtype: String
        """

        return self._feature_toggle_token


    def get_url(self):
        """Return the url of the project

        :return: url
        :rtype: String
        """

        return self._url



class ASTNodeVisitor:
    """Class of AST visitor (same as Python's AST library). To add a visitor of a
    specific node, one has to add a "visit_" + nodename method.
    """

    def visit(self, cursor):
        """Visit a specific node. If the visitor of the node has been implemented,
        this method calls it. Otherwise, it calls generic_visit().

        :param cursor: cursor over the AST
        :param type: tree_sitter.Cursor
        """

        method = "visit_" + cursor.node.type
        visitor = getattr(self, method, self.generic_visit)
        return visitor(cursor)

    def generic_visit(self, cursor):
        """Visits each node of the AST.

        :param cursor: cursor over the AST
        :param type: tree_sitter.Cursor
        """

        if cursor.goto_first_child():
            self.visit(cursor)
            cursor.goto_parent()
        if cursor.goto_next_sibling():
            self.visit(cursor)


class IFVisitor(ASTNodeVisitor):
    """Visitor of IF_STATEMENT. Extract the feature toggles from if statements.

    :param feature_toggle_token: feature toggle token to look for in if\
     statements
    :param type: String
    :param source: source code
    :param type: Bytes
    :param kw_list: list of feature toggles keywords
    :param type: List
    """

    def __init__(self, feature_toggle_token, source, kw_list):
        self._feature_toggle_token = feature_toggle_token
        self._source = source
        self._kw_list = kw_list
        self.res = {"expression": [], "imply": [], "var": []}
        self._stack = []
        super()

    def generic_visit(self, cursor):
        """In addition to ASTNodeVisitor's, this implementation uses a stack to follow
        nested loops."""

        if cursor.goto_first_child():
            self.visit(cursor)
            cursor.goto_parent()
            if cursor.node.type == "if_statement"\
                and self._stack:
                self._stack.pop()
        if cursor.goto_next_sibling():
            self.visit(cursor)

    def visit_if_statement(self, cursor):
        """If_statement visitor: update the variable res of the type of feature toggle
        interactions: inside an expression, nested ifs, etc."""

        nnode = cursor.node.children[1]
        txt = self._source[nnode.start_byte:nnode.end_byte].decode('utf8')
        self._stack.append(txt)
        if self._feature_toggle_token in txt:
            for kw in self._kw_list:
                if f"{self._feature_toggle_token}.{kw}" in txt:
                    if nnode.type == "binary_expression":
                        self.res["expression"].append(txt)
                    else:
                        ssize = len(self._stack)
                        if ssize == 1:
                            self.res["var"].append(self._stack[0])
                        elif len(self._stack) > 1:
                            self.res["imply"].append(self._stack.copy())
        self.generic_visit(cursor)


class File:
    """Class of a file in the project.

    :param filepath: path to the file
    :param type: String
    :param project: the project
    :param type: Project
    :param parser: tree sitter parser of the language
    :param type: tree_sitter.Parser
    """

    def __init__(self, filepath, project, parser):
        self._file = filepath
        self._project = project
        self._content = read_file(self._file)
        self._source = bytes(self._content, "utf8")
        self._data = None
        self._content = ""
        self._parser = parser

    def extract(self):
        """Extract information about feature toggles from the file

        :return: dictionnary containing nested if statement with feature toggles\
         (imply), if statement with only feature toggles and if statement with\
         expressions and feature toggles.
        :rtype: Dict
        """

        tree = self._parser.parse(self._source)
        cursor = tree.walk()
        ast_visitor = IFVisitor(self._project.get_feature_toggle_token(),\
                                self._source, self._project.get_keywords())
        ast_visitor.generic_visit(cursor)
        self._data =  ast_visitor.res


    def get_data(self):
        """Return data

        :return: data
        :rtype: Dict
        """

        if self._data is None:
            self.extract()
        return self._data


class Project:
    """Class of a Project. A project has a configuration file and is composed of files.

    :param project_name: Name of the project
    :param type: String
    :param parser: parser of the language
    :param type: tree_sitter.Parser
    """

    def __init__(self, project_name, parser):
        self.project_name = project_name
        self._parser = parser
        self._config_file = ConfigFile(self.project_name.lower())
        self._ft_file = None
        self._file_kw_dict = dict()
        self._count_file = dict()
        self._kw_occurences = dict()
        self._files = None
        self._parser = parser
        for kw in self._config_file.get_keywords():
            self._count_file[kw] = 0
            self._kw_occurences[kw] = 0


    def _ft_format(self, ft):
        """Returns the feature toggle format.

        :return: ft format
        :rtype: String
        """

        return f"{self._config_file.get_feature_toggle_token()}.{ft}"


    def get_files_with_keywords(self):
        """Gives the list of all files with feature toggles according to feature toggle
        token and keywords. Update internal counting variables.

        :return: all files with ft
        :rtype: List
        """

        if self._files is None:
            self._files = dict()
            f_w_kw = self._get_files_with_keywords()
            for f in f_w_kw:
                self._files[f] = None

        return self._files.keys()


    def _get_files_with_keywords(self):

        folders = [x[0] for x in os.walk(self._config_file.get_directory())]
        target_lang_files = []
        for dir_name in folders:
            target_lang_files.extend([f"{dir_name}/{k}" for k in os.listdir(dir_name)\
                                      if k.endswith(".go")])
        files_w_ft = []
        for src in target_lang_files:
            file_content = read_file(src)
            kws_in = [k for k in self._config_file.get_keywords()\
                      if self._ft_format(k) in file_content]
            if kws_in:
                self._file_kw_dict[src] = kws_in
                files_w_ft.append(src)
                for k in kws_in:
                    self._count_file[k] += 1
                    self._kw_occurences[k] += file_content.count(self._ft_format(k))

        return files_w_ft


    def analyse_files(self):
        """Analyse all interesting files and updates the dictionary of files."""

        if self._files is None:
            self.get_files_with_keywords()
        self._analyse_files()


    def _analyse_files(self):
        for target_file in self._files:
            self._files[target_file] = File(target_file, self, self._parser)
            self._files[target_file].extract()

    def get_feature_toggle_token(self):
        """Return the feature toggle token

        :return: feature toggle token
        :rtype: String
        """
        return self._config_file.get_feature_toggle_token()


    def get_keywords(self):
        """Return the the list of feature toggles keywords of the project

        :return: List of keywords
        :rtype: List
        """

        return self._config_file.get_keywords()
