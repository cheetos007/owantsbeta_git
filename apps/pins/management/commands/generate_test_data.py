import random
import os
import json
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User 
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site 

from pins.models import Pin, Board, User, DefaultBoard, Like, Category

from pins.forms import get_pin_url_form

COMMENT_WORDS = [ s.lower().strip(",.\n") for s in """Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
Vivamus sed tellus dui. Duis tristique rhoncus adipiscing. Nullam id sem at 
ipsum faucibus facilisis. Etiam id metus odio. Curabitur id vehicula magna. 
Suspendisse tincidunt tincidunt orci sed laoreet. Nulla faucibus, mi at venenatis 
imperdiet, dolor ante adipiscing elit, eu dictum turpis nunc sed risus. Donec vehicula, 
nisi non elementum aliquet, lacus mi mattis tellus, sed ultrices felis urna ac leo. Suspendisse 
vitae purus quam. Proin nunc elit, tempor vel tincidunt id, feugiat ac eros. Nam massa tellus, 
rhoncus non ultrices vel, laoreet vel diam. Cras ante nibh, pulvinar eget porttitor quis, feugiat 
semper enim. Vestibulum suscipit cursus massa nec rhoncus. Donec fermentum, dolor vitae accumsan accumsan, 
augue nisi vulputate magna, eget accumsan elit nunc vel velit. Nulla sagittis, tortor et ullamcorper consectetur, 
sapien velit sollicitudin eros, sit amet placerat nulla velit a ligula. Aliquam elit magna, adipiscing vel 
posuere eget, suscipit laoreet nisl.""".split(' ')]

def make_comment():
    words = random.sample(COMMENT_WORDS, random.randint(5, 55))
    return ' '.join(words).capitalize() + '.'

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--num-pins',
            action='store',
            dest='num_pins',
            default=100,
            help='Number of pins to create',
            type='int'),
        make_option('--num-videos',
            action='store',
            dest='num_videos',
            default=50,
            help='Number of videos to create',
            type='int'),
        make_option('--max-comments',
            action='store',
            dest='max_comments',
            default=20,
            help='Maximum number of comments per pin to generate',
            type='int'),
        make_option('--num-users',
            action='store',
            dest='num_users',
            default=50,
            help='Maximum number of comments per pin to generate',
            type='int'),
        make_option('--num-likes',
            action='store',
            dest='num_likes',
            default=50,
            help='Maximum number of comments per pin to generate',
            type='int'),
        )

    def handle(self, *args, **options):
        #create users
        default_boards = DefaultBoard.objects.all()
        image_dir = os.path.join(os.path.dirname(settings.MEDIA_ROOT), 'default_images')
        image_files = [os.path.join(image_dir, f) for f in os.listdir(image_dir)]
        self.stdout.write("Generating %d users, %d pins with 0-%d comments per pin.\n" % (options['num_users'], options['num_pins'], options['max_comments'] ))

        for i in xrange(options['num_users']):
            u = User.objects.create(username="user%d" % i, first_name="User No %d" % i, email="user%d@example.org" % i)
            for b in default_boards:
                Board.objects.create(user=u, name=b.name, category=b.category)

        users = list(User.objects.all())
        boards = list(Board.objects.all())
        ct = ContentType.objects.get_for_model(Pin)
        site = Site.objects.get_current()

        #generate default users to follow for each category
        for c in Category.objects.get_list_for_welcome_screen():
            users = random.sample(users, 4)
            for u in users:
                c.recommended_users_to_follow.add(u)

        for i in xrange(options['num_pins']):
            is_repin = bool((random.randint(0,100) > 80) and Pin.objects.count()>0)
            p = Pin.objects.create(description = make_comment(), board=random.choice(boards))
            if not is_repin:
                f_name = random.choice(image_files)
                p.image.save(os.path.basename(f_name),  ContentFile(open(f_name, 'rb').read()))
            else:
                p.is_repin = True
                p.source_pin = random.choice(list(Pin.objects.filter(is_repin=False)))
                p.save()
            for ic in xrange(random.randint(0, options['max_comments'])):
                Comment.objects.create(comment=make_comment(), user=random.choice(users), 
                    content_type_id = ct.pk, object_pk=p.pk, site=site)

            for il in xrange(random.randint(0, options['num_likes'])):
                Like.objects.like_pin(p, random.choice(users))

        source_json = os.path.join(settings.PROJECT_ROOT, 'apps', 'pins','management',
            'commands','video_sources.json')
        videos = json.loads(open(source_json,'rb').read())

        for i in xrange(options['num_videos']):
            b = random.choice(boards)
            form_class = get_pin_url_form(b.user)
            v = random.choice(videos)
            data = {'description': make_comment(), 'board': b.pk, 'url':'http://youtube.com/', 
                'parser':v['parser'], 'video_id': v['video_id']}
            form = form_class(data)
            form.is_valid()
            form.save()

        self.stdout.write("Data generated successfully!")








