from sympy.parsing.sympy_parser import standard_transformations, convert_xor, implicit_multiplication, convert_equals_signs
import sympy as smp
import base64
from io import BytesIO
import matplotlib.pyplot as plt


def test():
    return "Hello there"

def second_func():
    return test()


if __name__ == "__main__":
    second_func()