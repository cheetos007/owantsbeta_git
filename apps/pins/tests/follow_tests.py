from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


from pins.models import Board, Pin, Category

class FollowTestCase(TestCase):

	def setUp(self):
		from pins.follow import follow
		self.follow = follow
		self.follow.flushdb()

	def test_follow_user(self):
		self.follow.add_user_follower(1, 2)
		self.follow.add_user_follower(1, 3)

		self.assertEqual(self.follow.get_user_followers(1), [3, 2])

	def test_following(self):

		self.follow.add_user_follower(1, 2)
		self.follow.add_user_follower(1, 3)

		self.assertEqual(self.follow.get_user_followers(1), [3, 2])
		self.assertEqual(self.follow.get_user_following(3), [1])
		self.assertEqual(self.follow.get_user_following(2), [1])

	def test_delete_followers(self):

		self.follow.add_user_follower(1, 2)
		self.follow.add_user_follower(1, 3)

		self.assertEqual(self.follow.get_user_followers(1), [3, 2])
		self.assertEqual(self.follow.get_user_following(3), [1])
		self.assertEqual(self.follow.get_user_following(2), [1])
		self.follow.delete_user_follower(1,2)
		self.assertEqual(self.follow.get_user_followers(1), [3])
		self.assertEqual(self.follow.get_user_following(2), [])

	def test_nonexistant_followers(self):

		self.follow.add_user_follower(1, 2)
		self.follow.add_user_follower(1, 3)

		self.assertEqual(self.follow.get_user_followers(1), [3, 2])
		self.assertEqual(self.follow.get_user_followers(2), [])
		self.assertEqual(self.follow.get_user_followers(2048), [])

	def test_is_following_user(self):

		self.follow.add_user_follower(1, 2)
		self.follow.add_user_follower(1, 3)
		self.assertEqual(self.follow.is_following_user(1, 2), False)
		self.assertEqual(self.follow.is_following_user(2, 1), True)

		self.follow.delete_user_follower(1,2)
		self.assertEqual(self.follow.is_following_user(2, 1), False)




class TestFollowBoards(TestCase):
	fixtures = ['test', 'initial']
	
	def setUp(self):
		self.user = User.objects.all()[0]
		self.category = Category.objects.all()[0]
		from pins.follow import follow
		self.follow = follow
		self.follow.flushdb()

	def test_blank_boards(self):

		self.assertEqual(self.follow.get_user_unfollowed_boards(1), [])

	def test_explicit_unfollow_board(self):

		self.follow.add_user_unfollowed_board(5, 10)
		self.follow.add_user_unfollowed_board(5, 12)
		self.follow.add_user_unfollowed_board(5, 15)
		self.assertEqual(self.follow.get_user_unfollowed_boards(5), [15, 12, 10])

	def test_implicit_board_unfollow(self):

		b = Board.objects.create(name="Some board", category=self.category, user=self.user)
		self.follow.add_user_follower(self.user.pk, 2)
		self.follow.add_user_unfollowed_board(2, b.pk)
		self.assertEqual(self.follow.get_user_unfollowed_boards(2), [b.pk])

		self.follow.delete_user_follower(self.user.pk, 2)
		self.assertEqual(self.follow.get_user_unfollowed_boards(2), [])

	def test_is_unfollowing(self):
		b = Board.objects.create(name="Some board", category=self.category, user=self.user)
		self.follow.add_user_follower(self.user.pk, 2)
		self.follow.add_user_unfollowed_board(2, b.pk)
		self.assertEqual(self.follow.is_unfollowing_board(2, b.pk), True)



class FollowingPinsTest(TestCase):
	fixtures = ['test', 'initial']
	def setUp(self):
		from pins.follow import follow
		self.follow = follow
		self.follow.flushdb()
		self.user = User.objects.all()[0]
		self.category = Category.objects.create(name='Some category')
		self.board = Board.objects.create(name='Some board', category=self.category, user=self.user)
		self.user2 = User.objects.create(username='testuser')

	def test_followed_people_pins(self):
		p = Pin.objects.create(url="http://example.org/", board=self.board)
		
		self.follow.add_user_follower(self.user.pk, self.user2.pk)

		index_pins = Pin.objects.latest_pins_for_user(self.user2)
		self.assertIn(p, index_pins)

	def test_unfollowed_boards(self):
		p = Pin.objects.create(url="http://example.org/", board=self.board)
		b2 = Board.objects.create(name="some board 2", category = self.category, user=self.user)
		p2 = Pin.objects.create(url="http://example.org/", board=b2)
		self.follow.add_user_follower(self.user.pk, self.user2.pk)

		self.follow.add_user_unfollowed_board(self.user2.pk, b2.pk)


		index_pins = Pin.objects.latest_pins_for_user(self.user2)
		self.assertIn(p, index_pins)
		self.assertNotIn(p2, index_pins)

	def test_category_pins(self):
		p = Pin.objects.create(url="http://example.org/", board=self.board)
		c2 = Category.objects.create(name="Another category")
		b2 = Board.objects.create(name="some board 2", category = c2, user=self.user)
		p2 = Pin.objects.create(url="http://example.org/", board=b2)
		self.follow.add_user_follower(self.user.pk, self.user2.pk)

		index_pins = Pin.objects.latest_pins_for_user(self.user2, category=c2)
		self.assertNotIn(p, index_pins)
		self.assertIn(p2, index_pins)






