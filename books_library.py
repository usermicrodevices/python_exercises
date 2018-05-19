class book:
	def __init__ ( self, author = 'Van Rossum', caption = 'Python as speak language', date = '2018-05-01 00:00:00'):
		self.author = author
		self.caption = caption
		self.date = date
		self.sorted_field = self.author

	def __repr__(self):
		return 'Author: %s\nCaption: %s\nDate: %s\n' % (self.author, self.caption, self.date)

	def __str__(self):
		return repr(self)

	def set_sorted_field(self, value = 'author'):
		if value == 'author':
			self.sorted_field = self.author
		elif value == 'caption':
			self.sorted_field = self.caption
		elif value == 'date':
			self.sorted_field = self.date

	def __getitem__(self, key):
		return self.sorted_field

class library(list):
	def __init__ ( self, books = []):
		self.books = books

	def __repr__(self):
		result = ''
		for b in self.books:
			result += '======\n%s\n' % str(b)
		return result

	def __str__(self):
		return repr(self)

	# def __add__(self, other):
		# self.books += other
		# return len(self.books)

	def __len__(self):
		return len(self.books)

	def __getitem__(self, key):
		return self.books[key]

	def __setitem__(self, key, value):
		self.books[key] = value

	def __delitem__(self, key):
		del self.books[key]

	def __iter__(self):
		return self.books.__iter__()

	def __contains__(self, item):
		for b in self.books:
			if item == b:
				return True
		return False

	def append(self, item):
		self.books.append(item)

	def count(self):
		return len(self.books)

	def sort(self, func):
		self.books = sorted(self.books, key=func)

	def set_sorted_field(self, value = 'author'):
		for b in self.books:
			b.set_sorted_field(value)

	def search(self, value = '', field = ''):
		if not value:
			print('search value is empty')
		else:
			for b in self.books:
				if field:
					if field == 'author' and value in b.author:
						return b
					elif field == 'caption' and value in b.caption:
						return b
					elif field == 'date' and value in b.date:
						return b
				else:
					if value in b.author or value in b.caption or value in b.date:
						return b
		print('value %s in field %s not found' % (value, field))
		return None

def sorting(s):
	return s[0]


if __name__ == '__main__':
	lib = library([book(author = 'Van Rossum', caption = 'Python as speak language', date = '2018-05-01 00:00:00')])
	b = book(author = 'Bjarne Stroustrup', caption = 'C++ as system language', date = '2018-05-02 00:00:00')
	print(b in lib)
	# lib += [b]
	lib.append(b)
	print(len(lib))
	print(lib)
	print(b in lib)

	lib.sort(sorting)
	print(lib)

	lib.append(book('Randall Hyde', 'Art of Assembly Language, 2nd Edition', '2010-03-01 00:00:00'))
	lib.set_sorted_field('caption')
	lib.sort(sorting)
	print(lib)

	lib.set_sorted_field('date')
	lib.sort(sorting)
	print(lib)

	print(lib.search('Art'))

	print(lib.search('Rossum'))

	print(lib.search('Rossum', 'date'))

	print('='*20)
	print(lib.search('2010', 'date'))
