from django.db import models
from audit_fields.models import BaseAuditModel
import ipcalc
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

class BanIP(BaseAuditModel):
    ip_range = models.CharField(_('IP range'), max_length = 18, 
        help_text = _('IP or IP range (CIDR notation) to ban. Use 198.162.1.0/24 to ban entire 198.162.1.* subnet. Subnet masks less than 16 are not supported.'))

    class Meta:
        verbose_name = _('banned IP')
        verbose_name_plural = _('banned IPs')
    
    def __unicode__(self):
        return self.ip_range
    
    def clean(self, **kwargs):
        try:
            network = ipcalc.Network(self.ip_range)
            list(network)
        except (ValueError, OverflowError) as e:
            raise models.exceptions.ValidationError(e)
        return super(BanIP, self).clean(**kwargs)
    
    @property
    def network(self):
        return ipcalc.Network(self.ip_range)


def purge_cache(sender,*args,**kwargs):
    cache.delete('banned_ips')


models.signals.post_save.connect(purge_cache, sender=BanIP, dispatch_uid='ip_ban.models')
models.signals.post_delete.connect(purge_cache, sender=BanIP, dispatch_uid='ip_ban.models')

    