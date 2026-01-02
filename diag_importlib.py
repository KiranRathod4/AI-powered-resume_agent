import importlib
import sys

print("importlib module:", importlib)
print("has importlib.util:", hasattr(importlib, "util"))
print("sys.executable:", sys.executable)
print("sys.version:", sys.version)

try:
    import importlib.util as iu
    print("importlib.util.find_spec available:", hasattr(iu, "find_spec"))
    print("PyPDF2 present:", iu.find_spec("PyPDF2") is not None)
    print("langchain present:", iu.find_spec("langchain") is not None)
    print("langchain_community present:", iu.find_spec("langchain_community") is not None)
except Exception as e:
    print("error importing importlib.util:", repr(e))