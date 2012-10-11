def callable_setting(key):
	def inner_fn():
		from site_settings.helpers import get_setting
		return get_setting(key)
	return inner_fn

THUMBNAIL_WATERMARK = callable_setting('watermark')
THUMBNAIL_WATERMARK_ALWAYS = callable_setting('watermark_enabled')
THUMBNAIL_WATERMARK_POSITION = callable_setting('watermark_position')
THUMBNAIL_WATERMARK_OPACITY = callable_setting('watermark_opacity')
THUMBNAIL_WATERMARK_SIZE = callable_setting('watermark_size')

#assumes we have a local redis install at default port
THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.redis_kvstore.KVStore'
THUMBNAIL_ENGINE = 'sorl_watermarker.engines.pil.Engine'