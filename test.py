import pandas

r = pandas.DataFrame([[1, 2, 3]], columns=['a', 'b', 'c'])
print(r)
r = r.set_index(r['a'])
r = r.loc[1]
print(r.a)
