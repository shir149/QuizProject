from django import forms
from django.forms.widgets import FileInput

class MultipleFileInput(FileInput):
    def __init__(self, attrs=None):
        super().__init__(attrs)
        if attrs is not None:
            self.attrs.update(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        attrs.update({'multiple': 'multiple'})
        return super().render(name, value, attrs, renderer)