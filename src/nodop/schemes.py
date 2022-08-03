from models import NodopScheme, NodopFile
import ast
from difflib import SequenceMatcher

class AssignVisitor(ast.NodeVisitor):
    
    def __init__(self):
        super().__init__()
        self.nodes = list()
    
    def visit(self, node):
        if isinstance(node, ast.Assign):
            self.nodes.append(node)
        self.generic_visit(node)

class VariableNamingScheme(NodopScheme):
    
    @property
    def name(self):
        return "Variable Naming Substitution"
    
    @property
    def max_score(self):
        return 1.0
    
    def list_assignments(self, source):
        node = ast.parse(source)
        nv = AssignVisitor()
        nv.visit(node)
        return [(i, nd.targets, nd.value) for i, nd in enumerate(nv.nodes)]
        
    def get_name_similarity(self, ref, candidate):
        ref = list(filter(lambda node: isinstance(node[1][0], ast.Name), ref))
        candidate = list(filter(lambda node: isinstance(node[1][0], ast.Name), candidate))
        base_score = 0.0
        lengths = (len(ref), len(candidate))
        if lengths[0] == lengths[1]:
            base_score = (1 / (lengths[0] + 1)) # Suspected
        for i in range(min(lengths)):
            if len(ref[i][1]) == len(candidate[i][1]):
                if ((SequenceMatcher(None, ref[i][1][0].id, candidate[i][1][0].id).ratio() > 0.926)):
                    base_score += (1 / (min(lengths) + 1))
        return base_score
        
    # TODO: Make a comparison process to check if there is a similarity in assigning values.
    
    def eval(self, ref: NodopFile, candidate: NodopFile):
        lst_ref = self.list_assignments(ref.get_raw_source())
        lst_cand = self.list_assignments(candidate.get_raw_source())
        return self.get_name_similarity(lst_ref, lst_cand)