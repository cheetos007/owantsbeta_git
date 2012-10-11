# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Changing field 'Board.is_active'
        db.alter_column('pins_board', 'is_active', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Category.is_active'
        db.alter_column('pins_category', 'is_active', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Pin.domain'
        db.alter_column('pins_pin', 'domain_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pins.PinDomain'], null=True, blank=True))

        # Changing field 'Pin.is_active'
        db.alter_column('pins_pin', 'is_active', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Pin.is_flagged'
        db.alter_column('pins_pin', 'is_flagged', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Pin.url'
        db.alter_column('pins_pin', 'url', self.gf('django.db.models.fields.URLField')(max_length=255, blank=True))

        # Changing field 'Pin.is_repin'
        db.alter_column('pins_pin', 'is_repin', self.gf('django.db.models.fields.BooleanField')(blank=True))
    
    
    def backwards(self, orm):
        
        # Changing field 'Board.is_active'
        db.alter_column('pins_board', 'is_active', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Category.is_active'
        db.alter_column('pins_category', 'is_active', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Pin.domain'
        db.alter_column('pins_pin', 'domain_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pins.PinDomain'], blank=True))

        # Changing field 'Pin.is_active'
        db.alter_column('pins_pin', 'is_active', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Pin.is_flagged'
        db.alter_column('pins_pin', 'is_flagged', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Pin.url'
        db.alter_column('pins_pin', 'url', self.gf('django.db.models.fields.URLField')(max_length=255))

        # Changing field 'Pin.is_repin'
        db.alter_column('pins_pin', 'is_repin', self.gf('django.db.models.fields.BooleanField')())
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'pins.board': {
            'Meta': {'object_name': 'Board'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pins.Category']", 'null': 'True', 'blank': 'True'}),
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pins_board_created_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'modified_datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pins_board_modified_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'board_set'", 'to': "orm['auth.User']"})
        },
        'pins.category': {
            'Meta': {'object_name': 'Category'},
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pins_category_created_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'modified_datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pins_category_modified_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'pins.pin': {
            'Meta': {'object_name': 'Pin'},
            'board': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pins.Board']"}),
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pins_pin_created_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pins.PinDomain']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_flagged': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_repin': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'modified_datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pins_pin_modified_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'repinned_pin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'first_level_repinned_set'", 'null': 'True', 'to': "orm['pins.Pin']"}),
            'source_pin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'all_repinned_set'", 'null': 'True', 'to': "orm['pins.Pin']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'})
        },
        'pins.pindomain': {
            'Meta': {'object_name': 'PinDomain'},
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pins_pindomain_created_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'domain_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pins_pindomain_modified_set'", 'null': 'True', 'to': "orm['auth.User']"})
        }
    }
    
    complete_apps = ['pins']