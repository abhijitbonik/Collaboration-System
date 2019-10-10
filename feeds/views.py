
from django.shortcuts import render
from Community.models import CommunityArticles, Community, CommunityMembership, CommunityGroups, CommunityCourses ,CommunityMedia
from actstream import action
from actstream.models import Action
from django.contrib.contenttypes.models import ContentType
from BasicArticle.models import Articles
from Group.models import GroupArticles, GroupMembership
from Course.models import Course
from Media.models import Media
# Create your views here.


def create_resource_feed(actor,verb_id,action_object):
	verb=''
	if isinstance(actor, Articles):
		if CommunityArticles.objects.filter(article=actor).exists():
			target = CommunityArticles.objects.get(article=actor).community
			if verb_id=="article_published" :
				verb="Article has been published"
				actor_href='article_view'

		else:
			target = GroupArticles.objects.get(article=actor).group
			if verb_id=="article_published" :
				verb="Article has been published in the group"
				actor_href='article_view'
				action.send(actor,verb=verb,action_object=action_object,target=target,actor_href=actor_href,actor_href_id=actor.id,action_object_href='display_user_profile',action_object_href_id=action_object.username)
				comm=CommunityGroups.objects.get(group=target)
				target=comm.community

	if isinstance(actor, Media):
		target = CommunityMedia.objects.get(media=actor).community
		if verb_id=="image_published" :
		    verb="Image has been published"
		    actor_href='media_view'
		if verb_id=="audio_published" :
		    verb="Audio has been published"
		    actor_href='media_view'
		if verb_id=="video_published" :
		    verb="Video has been published"
		    actor_href='media_view'



	if isinstance(actor, Course):
		if CommunityCourses.objects.filter(course=actor).exists():
			target = CommunityCourses.objects.get(course=actor).community

	if verb_id == 'course_edit':
		verb="Course is available for editing"
		actor_href = 'course_view'

	if verb_id=='course_no_edit':
		verb = "Course is no more available for editing"
		actor_href = 'course_view'

	if verb_id=="course_published" :
		verb="Course has been published"
		actor_href='course_view'

	if verb_id == 'article_edit':
		verb="Article is available for editing"
		actor_href = 'article_edit'

	if verb_id=='article_no_edit':
		verb = "This article is no more available for editing"
		actor_href = 'article_view'

	if verb_id == 'image_edit':
		verb="Image is available for editing"
		actor_href = 'media_view'

	if verb_id=='image_no_edit':
		verb = "This image is no more available for editing"
		actor_href = 'media_view'

	if verb_id =='audio_edit' :
		verb="Audio is available for editing"
		actor_href = 'media_edit'

	if verb_id=='audio_no_edit':
		verb = "This audio is no more available for editing"
		actor_href = 'media_view'

	if verb_id =='video_edit':
		verb="Video is available for editing"
		actor_href = 'media_edit'

	if verb_id=='video_no_edit':
		verb = "This video is no more available for editing"
		actor_href = 'media_view'

	action.send(actor,verb=verb,action_object=action_object,target=target,actor_href=actor_href,actor_href_id=actor.id,action_object_href='display_user_profile',action_object_href_id=action_object.username)


def update_role_feed(user,target,current_role):
	previous_role = ''

	if isinstance(target, Community) and CommunityMembership.objects.filter(user=user, community=target).exists():
		membership = CommunityMembership.objects.get(user=user, community=target.pk)
		previous_role = membership.role.name

	elif GroupMembership.objects.filter(user=user, group=target).exists():
		membership = GroupMembership.objects.get(user=user, group=target.pk)
		previous_role = membership.role.name


	if current_role=='publisher':
		if previous_role=='author':
			action.send(user, verb='Role changed from Author to Publisher',target=target, actor_href='display_user_profile', actor_href_id=user.username)
		elif previous_role=='community_admin' or previous_role=='group_admin':
			action.send(user, verb='Role changed from Admin to Publisher',target=target, actor_href='display_user_profile', actor_href_id=user.username)

	elif current_role=='author':
		if previous_role=='publisher':
			action.send(user, verb='Role changed from Publisher to Author',target=target, actor_href='display_user_profile', actor_href_id=user.username)
		elif previous_role=='community_admin' or previous_role=='group_admin':
			action.send(user, verb='Role changed from Admin to Author',target=target, actor_href='display_user_profile', actor_href_id=user.username)

	elif current_role=='community_admin' or current_role=='group_admin':
		if previous_role=='publisher':
			action.send(user, verb='Role changed from Publisher to Admin',target=target, actor_href='display_user_profile', actor_href_id=user.username)
		elif previous_role=='author':
			action.send(user, verb='Role changed from Author to Admin',target=target, actor_href='display_user_profile', actor_href_id=user.username)

def remove_or_add_user_feed(user,target,action_type):
	if action_type=='community_created':
		action.send(user, verb='Admin has been added to the community',target=target, actor_href='display_user_profile', actor_href_id=user.username)

	elif action_type=='group_created':
		action.send(user, verb='Admin has been added to the group',target=target, actor_href='display_user_profile', actor_href_id=user.username)

	else:
		previous_role = ''
		if isinstance(target, Community) and CommunityMembership.objects.filter(user=user, community=target).exists():
			membership = CommunityMembership.objects.get(user=user, community=target.pk)
			previous_role = membership.role.name

		elif GroupMembership.objects.filter(user=user, group=target).exists():
			membership = GroupMembership.objects.get(user=user, group=target.pk)
			previous_role = membership.role.name

		if previous_role=='publisher':
			if action_type=='removed':
				action.send(user, verb='Publisher has been removed',target=target, actor_href='display_user_profile', actor_href_id=user.username)
			elif action_type=='left':
				action.send(user, verb='Publisher has left',target=target, actor_href='display_user_profile', actor_href_id=user.username)
			elif action_type=='added':
				verb = 'Publisher has been added'
				action.send(user, verb=verb, target=target, actor_href='display_user_profile', actor_href_id=user.username)


		elif previous_role=='community_admin' or previous_role=='group_admin':
			if action_type=='removed':
				action.send(user, verb='Admin has been removed',target=target, actor_href='display_user_profile', actor_href_id=user.username)
			elif action_type=='left':
				action.send(user, verb='Admin has left',target=target, actor_href='display_user_profile', actor_href_id=user.username)
			elif action_type=='added':
				verb = 'Admin has been added'
				action.send(user, verb=verb, target=target, actor_href='display_user_profile', actor_href_id=user.username)
