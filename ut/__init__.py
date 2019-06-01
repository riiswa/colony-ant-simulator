def cp(a,b):
    d = []
    [d.append(f) for e in map(lambda x: [(x,c) for c in a],b) for f in e]
    return d
