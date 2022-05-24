# import inspect
#
#
# class A(object):
#
#     def p(self):
#         previous_frame = inspect.currentframe().f_back
#         print(previous_frame.b)
#
#
# class B(object):
#     def __init__(self):
#         self.b = 1
#         self.a = A()
#
#     def run(self):
#         self.a.p()
#
# print(B().run())

import inspect

def hello():
    previous_frame = inspect.currentframe().f_back
    (filename, line_number,
     function_name, lines, index) = inspect.getframeinfo(previous_frame)
    return (filename, line_number, function_name, lines, index)

print(hello())

# ('/home/unutbu/pybin/test.py', 10, '<module>', ['hello()\n'], 0)