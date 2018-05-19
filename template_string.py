'testing object override as string class'

from traceback import format_exc

class TemplateString:
	def __init__(self, value):
		self.value = value

	def __str__(self):
		'convert any value to string'
		return repr(self.value)

	def __format__(self, format_spec):
		if not format_spec:
			format_spec = 'example format is ({value})'
		return format_spec.format(value=self.value)

	def __lt__(self, other):
		return self.value < other

	def __le__(self, other):
		return self.value <= other

	def __eq__(self, other):
		return self.value == other

	def __ne__(self, other):
		return self.value != other

	def __gt__(self, other):
		return self.value > other

	def __ge__(self, other):
		return self.value >= other

	def __bool__(self):
		return self.value != None and self.value != 0

def _print(expression):
	try:
		print(eval(expression))
	except:
		print(format_exc())


if __name__ == '__main__':
	test_string = TemplateString(1234567890)
	_print('test_string')
	_print('format(test_string)')
	_print("format(test_string, 'This is ({value})')")
	_print('test_string > 9876543210')
	_print('test_string < 9876543210')
	_print("test_string < '9876543210'")
	_print("test_string < ['9876543210', 987654320]")

	print('='*20)

	test_string = TemplateString(1234567.890)
	print(test_string)
	print(format(test_string))
	print(format(test_string, 'This is ({value})'))
