from .models import NodopScheme, NodopFile
import ast

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
        # TODO: Able to list assignments in code w/ AST traversing.
        node = ast.parse(source)
        nv = AssignVisitor()
        nv.visit(node)
        for nd in nv.nodes:
            print(nd.value)
            
    # TODO: Make a comparison process to check if there is a similarity in assigning values.
    
    def eval(self, ref: NodopFile, candidate: NodopFile):
        self.list_assignments(ref.get_raw_source())
        return 1.0