import os
import typing
import difflib
import abc

a = b = 1

def mod_no_blank_lines(src: typing.List[str], strip_left: bool=False):
    """
    This function should return a list of str without any blank lines.
    The returned str(s) also need to be stripped off whitespaces in the right.
    
    Case 1: only whitespaces
    >>> mod_no_blank_lines(['a', '   ', 'b'])
    ['a', 'b']
    
    Case 2: contains backslash-n
    >>> mod_no_blank_lines(['a', '\\n', 'b'])
    ['a', 'b']
    
    Case 3: stripping right spaces
    >>> mod_no_blank_lines(['a     ', '    \\n\\n     ', '     b    '])
    ['a', '     b']
    
    Case 4: stripping both sides
    >>> mod_no_blank_lines(['a     ', '    \\n\\n     ', '     b    '], True)
    ['a', 'b']
    """
    if strip_left:
        return [line.strip() for line in src if line.strip()]
    return [line.rstrip() for line in src if line.strip()]

def diff_string_lst(ref: typing.List[str], candidate: typing.List[str]):
    badoneline = (
        " ".join(mod_no_blank_lines(ref, True)),
        " ".join(mod_no_blank_lines(candidate, True))
        )
    return difflib.SequenceMatcher(None, badoneline[0], badoneline[1]).ratio()

class NodopFile:
    
    def __init__(self, path: str | os.PathLike, lines: None | typing.Tuple[int]=None):
        self.__path = path
        self.__lines = lines

    def get_raw_source(self):
        with open(self.__path) as f:
            return f.read()

    def get_real_source(self):
        with open(self.__path) as f:
            return [line for line in f.readlines()]
        
    def get_source(self):
        with open(self.__path) as f:
            if not self.__lines:
                return mod_no_blank_lines([line for line in f.readlines()])
            return mod_no_blank_lines([
                line for i, line in enumerate(f.readlines(), 1)
                if i in range(self.__lines[0], self.__lines[1] + 1)
                ])

class NodopScheme(abc.ABC):
    
    @property
    @abc.abstractproperty
    def name(self) -> str:
        pass
    
    @property
    @abc.abstractproperty
    def max_score(self) -> float:
        pass
    
    @abc.abstractmethod
    def eval(self, ref: NodopFile, candidate: NodopFile) -> float:
        pass

class NodopChecker:
    
    def __init__(self, ref: NodopFile, candidate: NodopFile, schemes: None | typing.List[NodopScheme]=None):
        if not ( isinstance(ref, NodopFile) or isinstance(candidate, NodopFile) ):
            raise TypeError("NodopChecker cannot be initialized, consider using `build_checker()`")
        self.__ref = ref
        self.__candidate = candidate
        self.__schemes = schemes
    
    @classmethod
    def build_checker(cls, ref: str | os.PathLike, candidate: str | os.PathLike, schemes: None | typing.List[object]=None):
        return NodopChecker(NodopFile(ref), NodopFile(candidate), schemes)
    
    def get_string_similarity(self):
        return diff_string_lst(
            self.__ref.get_real_source(), self.__candidate.get_real_source()
        )

    def create_result(self):
        result = NodopResult()
        result.push_to_flow("String Similarity Check", self.get_string_similarity(), 1.0)

        if self.__schemes:
            for scheme in self.__schemes:
                made_scheme = scheme()
                scheme_score = made_scheme.eval(self.__ref, self.__candidate)
                result.push_to_flow(made_scheme.name, scheme_score, made_scheme.max_score)
        
        return result

class NodopResult:

    def __init__(self):
        self.__flow = dict()
        self.current_score = 0.0
        self.max_score = 0.0
    
    @property
    def current_score(self):
        return self.__current_score
    
    @current_score.setter
    def current_score(self, score):
        self.__current_score = score

    @property
    def max_score(self):
        return self.__max_score
    
    @max_score.setter
    def max_score(self, score):
        self.__max_score = score

    def push_to_flow(self, name, score, max_score):
        self.__flow[name] = (score, max_score)
        self.max_score += max_score
        self.current_score += score

    def print_result(self):
        for k,v in self.__flow.items():
            print(f"{k}... -> {v[0]:.2f} / {v[1]:.2f} ({(v[0]/v[1])*100:.2f}%)")
        print()
        print(f"Final Result: {self.current_score:.2f} / {self.max_score:.2f} ({(self.current_score/self.max_score)*100:.2f}%)")
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
    from schemes import VariableNamingScheme
    chk = NodopChecker.build_checker("demo/hello_name_01.py", "demo/hello_name_02.py", [VariableNamingScheme])
    result = chk.create_result()
    result.print_result()