d = {313: [346, 349], 346: [350], 0: [313, 312], 312: [348]}
#tree_normal = {0:{313:{346:{350}, 349:{}}, 312:{348:{}}}}
#required = [{0:1}, {313:2}, {346:3}, {349:3}, {312:2}, {348:3}]

from treelib import Tree

tree = Tree()

def search_parent(src, k):
	for key, value in src.items():
		if k in value:
			return key
	return None

def commit_node(tr, p, k, nested):
	rnode, pnode = tr.root, None
	if rnode is None:
		if p is not None:
			rnode = tr.create_node(f'{p}', p, data=1)
	knode = tr.get_node(k)
	if knode is None:
		if p is not None:
			pnode = tr.get_node(p)
			if pnode is None:
				pnode = tr.create_node(f'{p}', p, rnode, data=rnode.data+1)
		knode = tr.create_node(f'{key}', key, pnode, data=pnode.data+1)
	if knode is not None:
		for item in nested:
			if not tr.contains(item):
				node = tr.create_node(f'{item}', item, knode, data=knode.data+1)

for key, value in d.items():
	p = search_parent(d, key)
	commit_node(tree, p, key, value)

print(tree)

result = []
for item in tree.all_nodes():
	result.append({item.identifier:item.data})

print(result)
