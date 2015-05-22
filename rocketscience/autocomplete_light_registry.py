import autocomplete_light
from models import Debater

class TeammatesAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields= ['^name',]

autocomplete_light.register(Debater, TeammatesAutocomplete)