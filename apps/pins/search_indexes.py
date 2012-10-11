import datetime
from haystack import indexes
from pins.models import Pin, Board
from django.contrib.auth.models import User


class PinIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    category = indexes.IntegerField(model_attr='board__category__pk')
    created_datetime = indexes.DateTimeField(model_attr='created_datetime')

    def get_model(self):
        return Pin

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.active_pins()

class BoardIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    created_datetime = indexes.DateTimeField(model_attr='created_datetime')

    def get_model(self):
        return Board

    def index_queryset(self):
        return self.get_model().objects.get_active_boards()

class UserIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return User

    def index_queryset(self):
        return self.get_model().objects.filter(is_active=True)