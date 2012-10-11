CONFIGURATION_MODELS = {'models': ['abuse_reports.models.AbuseReportReason', 'ip_ban.models.BanIP', 'pins.models.DefaultBoard', 'cms.models.pagemodel.Page',
                     'pins.models.PinAdvertisment','pins.models.Category', 'site_settings.models.Setting']
                    }

USER_CONTENT_MODELS = {'models':['abuse_reports.models.AbuseReport', 'pins.models.Board', 'django.contrib.comments.*', 'pins.models.Pin']}

USER_MODELS = {'models': ['django.contrib.auth.*', 'profiles.models.Profile']}