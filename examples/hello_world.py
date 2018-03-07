from template import Template
from template.util import Literal

template = Template()
source = Literal("Hello [% name or 'World' %]!")

print(template.process(source))
print(template.process(source, {'name': 'Badger'}))
