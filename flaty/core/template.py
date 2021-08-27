CLASS_TEMPLATE = """\
class {}(Model):
	{}
\tclass Meta:
\t\tdatabase = db

modelList['{}'] = {}
"""