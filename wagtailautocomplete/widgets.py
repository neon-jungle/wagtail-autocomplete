import json

from django.apps import apps
from django.forms import Widget
from wagtail.admin.edit_handlers import widget_with_script

from .views import render_page


class Autocomplete(Widget):
    template_name = 'wagtailautocomplete/autocomplete.html'

    def get_context(self, *args, **kwargs):
        context = super(Autocomplete, self).get_context(*args, **kwargs)
        context['widget']['page_type'] = self.page_type
        context['widget']['can_create'] = self.can_create
        context['widget']['is_single'] = self.is_single
        return context

    def format_value(self, value):
        if not value:
            return 'null'

        model = apps.get_model(self.page_type)
        if type(value) == list:
            return json.dumps([
                render_page(page)
                for page in model.objects.filter(id__in=value)
            ])
        else:
            return json.dumps(render_page(model.objects.get(pk=value)))

    def value_from_datadict(self, data, files, name):
        value = json.loads(data.get(name))
        if not value:
            return None

        if type(value) == list:
            return [obj['id'] for obj in value]

        return value['id']

    def render(self, name, value, attrs=None, renderer=None):
        print(name, value, attrs)
        print(dir(self))
        return widget_with_script(
            super().render(name, value, attrs, renderer),
            self.render_js_init(attrs['id']))

    def render_js_init(self, id):
        return "window.initAutoCompleteWidget('{0}');".format(id)
