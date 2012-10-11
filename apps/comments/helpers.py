from django.contrib.contenttypes.models import ContentType
from comments import get_model

def get_comments_for_obj(obj):
	content_type = ContentType.objects.get_for_model(obj)
	return (get_model().objects
		.filter(content_type=content_type, object_pk=obj.id)
		.select_related('user__profile'))