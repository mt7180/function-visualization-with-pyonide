from sympy.parsing.sympy_parser import standard_transformations, convert_xor, implicit_multiplication, convert_equals_signs
import sympy as smp
import base64
from io import BytesIO
import matplotlib.pyplot as plt

def parse_function(raw_input)-> None:
    inp, limits = extract_limit(raw_input)
    solution = {"errors":[], "input": inp, "limits": limits}
    try:
        if not inp:
            raise ValueError('no input given')
        #input = [inp.strip() for inp in expr.split(';')]
        transformations = (standard_transformations 
                            + (implicit_multiplication,) 
                            + (convert_xor,) 
                            + (convert_equals_signs,))

        if ("=" or "Eq") in inp:
            sol = smp.simplify(smp.parse_expr(
                inp, 
                transformations=transformations, 
                local_dict = {'e': smp.E})
            ).lhs
        else:
            sol = smp.parse_expr(
                inp, 
                transformations=transformations, 
                local_dict = {'e': smp.E}
            )
        #print("sol:", sol, list(sol.free_symbols))
        solution["smp_function"] = sol
        solution["free_symbols"] = list(sol.free_symbols)
        
    except AttributeError or ValueError or TypeError:
        solution["errors"].append("parsing your function returned an error")
    except Exception as ex:
        solution["errors"].append(str(ex))
    generate_diagram(solution)
    solution["latex_description"] = get_latex_functions(solution)
        
    return solution

def extract_limit(expr: str)->str:
        """get limit at the end of input_str: "x^2; e^x [-1, 4]
           if something went wrong, original input_str is returned
        """
        if len(expr) > 0 and expr[-1] == ']':
            if '[' in expr:
                split_indx = expr.rfind("[")
                limits = expr[split_indx+1:-1]
                return (expr[:split_indx].strip(), 
                    [float(limit) for limit in limits.split(',')])
            else: return "bad syntax", None
        return expr, None

def get_latex_functions(solution):
    vars = ','.join(map(lambda x: str(x), solution["free_symbols"]))
    return ("$$f(" + vars +')' + " = "
            + smp.latex(solution["smp_function"]) + "$$")



def move_sympyplot_to_axes(p, ax): # ax has to be a tuple
    backend = p.backend(p)
    backend.ax = ax
    backend.process_series()
    for axis in backend.ax:
        axis.spines['right'].set_color('none')
        axis.spines['bottom'].set_position('zero')
        axis.spines['top'].set_color('none')
    plt.close(backend.fig)

def generate_2D_symbolic(solution, ax):
    if not solution["limits"]:
        solution["limits"] = [-5,5]
   
    f = solution["smp_function"]
    # print(type(f))
    p1 = smp.plot(
        f,
        (solution["free_symbols"][0], solution["limits"][0], solution["limits"][1]),
        show = False
    )
    move_sympyplot_to_axes(p1, (ax,))

def generate_3D_symbolic(solution, ax):
    #x, y, z = smp.symbols('x y z')
    #functions = {f.symbolic_function: f.free_variables for f in function_set.functions}
    #free_vars = [*functions.values()][0] # only for the first function, todo: check if same vars for other functions
    if not solution["limits"]:
        solution["limits"] = [-5,5]

    f = solution["smp_function"]
    p1 = smp.plotting.plot3d(
        f, 
        (solution["free_symbols"][0], solution["limits"][0], solution["limits"][1]), 
        (solution["free_symbols"][1], solution["limits"][0], solution["limits"][1]),
        surface_color='green', show = False
    )
    move_sympyplot_to_axes(p1, (ax,))
        
def generate_diagram(solution):
    
    try:
        plt.switch_backend('Agg')   # without GUI initialization, not needed
        fig = plt.figure(figsize=plt.figaspect(0.5))
        
        plt.rcParams['figure.figsize'] = 5 , 5
        plt.rcParams['legend.loc'] = 'upper right'
        max_vars = len(solution["free_symbols"])
        
        if max_vars < 2:
            ax = fig.add_subplot(1, 1, 1,)
            generate_2D_symbolic(solution, ax)
        elif max_vars < 3:
            ax = fig.add_subplot(1, 1, 1, projection='3d')
            generate_3D_symbolic(solution, ax)
        
        plt.legend(loc='upper right')
        plt.xlabel(solution["free_symbols"])  # todo: welche free_vars (mit set.difference)
        plt.tight_layout()
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=70)

        # Embed the result into html output
        data = base64.b64encode(buffer.getbuffer()).decode("utf-8")
        solution["figure"] = f"data:image/png;base64,{data}"
        buffer.close()
    except Exception as ex:
        solution["errors"].append(str(ex))
        solution["figure"] = None
    

if __name__ == "__main__":
    input_string = "x^2-3"
    print(parse_function(input_string))