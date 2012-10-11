# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Setting.allow_facebook_share'
        db.delete_column('site_settings_setting', 'allow_facebook_share')

        # Adding field 'Setting.allow_facebook_like'
        db.add_column('site_settings_setting', 'allow_facebook_like', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'Setting.allow_facebook_share'
        db.add_column('site_settings_setting', 'allow_facebook_share', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Deleting field 'Setting.allow_facebook_like'
        db.delete_column('site_settings_setting', 'allow_facebook_like')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'site_settings.setting': {
            'Meta': {'object_name': 'Setting'},
            'administrator_email': ('django.db.models.fields.EmailField', [], {'default': "'admin@example.org'", 'max_length': '255'}),
            'allow_facebook_like': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_tweet': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'bookmarklet_title': ('django.db.models.fields.CharField', [], {'default': "'owants'", 'max_length': '50'}),
            'bookmarklet_title_en': ('django.db.models.fields.CharField', [], {'default': "'owants'", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'bookmarklet_title_lv': ('django.db.models.fields.CharField', [], {'default': "'owants'", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'site_settings_setting_created_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'facebook_api_secret': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'facebook_app_id': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'google_oauth2_client_id': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'google_oauth2_client_secret': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified_datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'site_settings_setting_modified_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'site_logo': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'default': "'owants'", 'max_length': '255'}),
            'site_name_en': ('django.db.models.fields.CharField', [], {'default': "'owants'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'site_name_lv': ('django.db.models.fields.CharField', [], {'default': "'owants'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'twitter_consumer_key': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'twitter_consumer_secret': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'twitter_handle': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['site_settings']
