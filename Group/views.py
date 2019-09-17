from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, JsonResponse
from .models import Group, GroupMembership, GroupArticles, GroupInvitations, GroupMedia
from BasicArticle.models import Articles
from Community.models import CommunityMembership, CommunityGroups
from django.contrib.auth.models import Group as Roles
from django.contrib.auth.models import User
from rolepermissions.roles import assign_role
from UserRolesPermission.roles import GroupAdmin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from notification.views import notify_update_role, notify_remove_or_add_user, notify_subscribe_unsubscribe
from feeds.views import remove_or_add_user_feed, update_role_feed
from actstream import action
from actstream.models import Action
from actstream.models import target_stream
from BasicArticle.views import getHTML
from django.conf import settings
import json
import requests
from etherpad.views import create_group_ether, create_article_ether_group, create_session_group

def create_group(request):
	if request.method == 'POST':
		name = request.POST['name']
		desc = request.POST['desc']
		try:
			image = request.FILES['group_image']
		except:
			image = None
		user = request.user
		visibility = request.POST['visibility']
		group = Group.objects.create(
			name = name,
			desc  = desc,
			image = image,
			visibility = visibility,
			created_by = user
			)
		role = Roles.objects.get(name='group_admin')
		GroupMembership.objects.create(user=user, group=group, role=role)

		#create ether id for the group 
		create_group_ether(group)
		
		notify_remove_or_add_user(request.user, user, group, 'group_created')
		remove_or_add_user_feed(request.user, group, "group_created")
		return group

def group_view(request, pk):
	invitereceived = 'FALSE'
	try:
		message = 0
		group = Group.objects.get(pk=pk)
		uid = request.user.id
		membership = GroupMembership.objects.get(user=uid, group=group.pk)
		role = Roles.objects.get(name='group_admin')
		if membership.role == role:
			count = GroupMembership.objects.filter(group=group,role=role).count()
			if count < 2:
				message = 1
	except GroupMembership.DoesNotExist:
		membership = 'FALSE'
		try:
			invitereceived = GroupInvitations.objects.filter(user=uid, group=group, status='Invited')
		except GroupInvitations.DoesNotExist:
			invitereceived = 'FALSE'
	try:
		community = CommunityGroups.objects.get(group=pk)
		communitymembership = CommunityMembership.objects.get(user =uid, community = community.community.pk)
	except CommunityMembership.DoesNotExist:
		communitymembership = 'FALSE'
	subscribers = GroupMembership.objects.filter(group = pk).count()
	pubarticles = GroupArticles.objects.raw('select ba.id , ba.title, ba.body, workflow_states.name as state from  workflow_states, BasicArticle_articles as ba , Group_grouparticles as ga  where ba.state_id=workflow_states.id and  ga.article_id=ba.id and ga.group_id=%s and ba.state_id in (select id from workflow_states as w where w.name = "publish");', [group.pk])
	pubarticlescount = len(list(pubarticles))
	users = GroupArticles.objects.raw('select  u.id,username from auth_user u join Group_grouparticles g on u.id = g.user_id where g.group_id=%s group by u.id order by count(*) desc limit 2;', [pk])
	contributors = GroupMembership.objects.filter(group = pk)
	othergroups = CommunityGroups.objects.filter(community = community.community.pk)
	return render(request, 'groupview.html', {'group': group, 'communitymembership':communitymembership,'membership':membership, 'subscribers':subscribers, 'contributors':contributors, 'users':users, 'community':community,'message':message,'pubarticles':pubarticles,'pubarticlescount':pubarticlescount, 'othergroups':othergroups, 'invitereceived':invitereceived})

def group_subscribe(request):
	if request.user.is_authenticated:
		if request.method == 'POST':
			gid = request.POST['gid']
			group = Group.objects.get(pk=gid)
			user = request.user
			role = Roles.objects.get(name='author')
			if GroupMembership.objects.filter(user=user, group=group).exists():
				return redirect('group_view', pk=gid)
			obj = GroupMembership.objects.create(user=user, group=group, role=role)
			notify_subscribe_unsubscribe(request.user, group, 'subscribe')
			return redirect('group_view', pk=gid)
		return render(request, 'groupview.html')
	else:
		return redirect('login')

def group_unsubscribe(request):
	if request.user.is_authenticated:
		if request.method == 'POST':
			gid = request.POST['gid']
			group = Group.objects.get(pk=gid)
			user = request.user
			if GroupMembership.objects.filter(user=user, group=group).exists():
				remove_or_add_user_feed(user, group, 'left')
				notify_remove_or_add_user(user, user, group, 'left')
				obj = GroupMembership.objects.filter(user=user, group=group).delete()
			return redirect('group_view', pk=gid)
		return render(request, 'groupview.html')
	else:
		return redirect('login')

def group_article_create_body(request,article, group):
	if request.user.is_authenticated:
		if request.method == 'POST':
			article.body = getHTML(article)
			article.save()
			data={
				'article_id':article.pk,
				'body':article.body
			}
			return JsonResponse(data)
			# return redirect('article_view', article.pk)
			# else:
			# 	article.creation_complete = True
			# 	article.save()
			# 	return render(request, 'new_article_body.html', {'article':article,'community':community, 'status':2, 'url':settings.SERVERURL, 'articleof':'community'})
		else:
			return redirect('home')
	else:
		return redirect('login')

def group_article_create(request):
	pass

def group_h5p_create(request):
	if request.user.is_authenticated:
		if request.method == 'POST':
			gid = request.POST['gid']
			request.session['cid'] = 0
			request.session['gid'] = gid
			try:
				requests.get(settings.H5P_ROOT + 'h5p/h5papi/?format=json')
				return redirect(settings.H5P_ROOT + 'h5p/create/')
			except Exception as e:
				print(e)
				return render(request, 'h5pserverdown.html', {})
		return redirect('home')
	return redirect('login')

def manage_group(request,pk):
	if request.user.is_authenticated:
		group = Group.objects.get(pk=pk)
		community = CommunityGroups.objects.get(group=pk)
		uid = request.user.id
		errormessage = ''
		membership = None
		try:
			membership = GroupMembership.objects.get(user=uid, group=group.pk)
			if membership.role.name == 'group_admin':
				count = GroupMembership.objects.filter( group=group.pk, role=membership.role).count()
				members = GroupMembership.objects.filter(group=group.pk)
				if request.method == 'POST':
					try:
						username = request.POST['username']
						rolename = request.POST['role']
						user = User.objects.get(username = username)
						role = Roles.objects.get(name=rolename)
						status = request.POST['status']

						if status == 'add':
							try:
								is_community_member = CommunityMembership.objects.get(user=user, community=community.community.pk)
								try:
									is_member = GroupMembership.objects.get(user=user, group=group.pk)
									errormessage = 'user exists in group'
								except GroupMembership.DoesNotExist:
									errormessage = inviteUser(request, group, user, role)
							except CommunityMembership.DoesNotExist:
								errormessage = 'user is not a part of the community'
						if status == 'update':
							if count > 1 or count == 1 and username != request.user.username:
								try:
									notify_update_role(request.user, user, group, rolename)
									update_role_feed(user, group, rolename)
									is_member = GroupMembership.objects.get(user=user, group=group.pk)
									is_member.role = role
									is_member.save()
								except GroupMembership.DoesNotExist:
									errormessage = 'no such user in the group'
							else:
								errormessage = 'cannot update this user'
						if status == 'remove':
							if count > 1 or count == 1 and username != request.user.username:
								try:
									notify_remove_or_add_user(request.user, user, group, 'removed')
									remove_or_add_user_feed(user, group, "removed")
									obj = GroupMembership.objects.filter(user=user, group=group).delete()
								except GroupMembership.DoesNotExist:
									errormessage = 'no such user in the group'
							else:
								errormessage = 'cannot remove this user'
						return render(request, 'managegroup.html', {'community':community, 'group':group, 'members':members, 'membership':membership, 'errormessage':errormessage})
						#return redirect('manage_group',pk=pk)
					except User.DoesNotExist:
						errormessage = "no such user in the system"

				return render(request, 'managegroup.html', {'community':community, 'group':group, 'members':members, 'membership':membership, 'errormessage':errormessage})
			else:
				return redirect('group_view',pk=pk)
		except GroupMembership.DoesNotExist:
			return redirect('group_view',pk=pk)
	else:
		return redirect('login')

def inviteUser(request, group, user, role):
	if(isInvited(group, user)):
		errormessage = user.username + ' is already invited to join this group'
	else:
		grpinvite = GroupInvitations.objects.create(invitedby=request.user, user=user, role=role, status='Invited', group=group)
		errormessage = 'invitation sent sucessfully to ' + user.username
	return errormessage

def isInvited(group, user):
	try:
		is_invited = GroupInvitations.objects.get(user=user, group=group.pk, status='Invited')
		return True
	except GroupInvitations.DoesNotExist:
		return False

def update_group_info(request,pk):
	if request.user.is_authenticated:
		group = Group.objects.get(pk=pk)
		errormessage = ''
		membership = None
		uid = request.user.id
		try:
			membership = GroupMembership.objects.get(user=uid, group=group.pk)
			if membership.role.name == 'group_admin':
				if request.method == 'POST':
					name = request.POST['name']
					desc = request.POST['desc']
					visibility = request.POST['visibility']
					group.name = name
					group.desc = desc
					group.visibility = visibility
					try:
						image = request.FILES['group_image']
						group.image = image
					except:
						errormessage = 'image not uploaded'
					group.save()
					return redirect('group_view',pk=pk)
				else:
					return render(request, 'updategroupinfo.html', {'group':group,'membership':membership})
			else:
				return redirect('group_view',pk=pk)
		except GroupMembership.DoesNotExist:
			return redirect('group_view',pk=pk)
	else:
		return redirect('login')

def group_content(request, pk):
	grparticles = ''
	try:
		group = Group.objects.get(pk=pk)
		uid = request.user.id
		membership = GroupMembership.objects.get(user=uid, group=group.pk)
		if membership:
			garticles = GroupArticles.objects.raw('select "article" as type , ba.id, ba.title, ba.body, ba.image, ba.views, ba.created_at, username, workflow_states.name as state from  workflow_states, auth_user au, BasicArticle_articles as ba , Group_grouparticles as ga  where au.id=ba.created_by_id and ba.state_id=workflow_states.id and  ga.article_id =ba.id and ga.group_id=%s and ba.state_id in (select id from workflow_states as w where w.name = "visible" or w.name="private");', [group.pk])
			gmedia = GroupMedia.objects.raw('select "media" as type, media.id, media.title, media.mediafile as image, media.mediatype, media.created_at, username, workflow_states.name as state from workflow_states, Media_media as media, Group_groupmedia as gmedia, auth_user au where au.id=media.created_by_id and media.state_id=workflow_states.id and media.id=gmedia.media_id and gmedia.group_id=%s and media.state_id in (select id from workflow_states as w where w.name = "visible" or w.name="private");', [group.pk])

			gh5p = []
			try:
				response = requests.get(settings.H5P_ROOT + 'h5p/h5papi/?format=json')
				json_data = json.loads(response.text)
				print(json_data)

				for obj in json_data:
					if obj['group_id'] == group.pk:
						gh5p.append(obj)
			except Exception as e:
				print(e)
				print("H5P server down...Sorry!! We will be back soon")

			lstfinal = list(garticles) + list(gmedia) + list(gh5p)
			page = request.GET.get('page', 1)
			paginator = Paginator(list(lstfinal), 5)
			try:
				grparticles = paginator.page(page)
			except PageNotAnInteger:
				grparticles = paginator.page(1)
			except EmptyPage:
				grparticles = paginator.page(paginator.num_pages)

	except GroupMembership.DoesNotExist:
		return redirect('group_view', group.pk)
	return render(request, 'groupcontent.html', {'group': group, 'membership':membership, 'grparticles':grparticles})

def handle_group_invitations(request):
	if request.method == 'POST':
		pk = int(request.POST['pk'])
		grpinivtation=GroupInvitations.objects.get(pk=pk)
		status = request.POST['status']
		user = User.objects.get(username = request.user.username)

		if status=='Accept' and grpinivtation.status!='Accepted':
			grpmmbership = GroupMembership.objects.create(user=grpinivtation.user, group=grpinivtation.group, role=grpinivtation.role)
			grpinivtation.status = 'Accepted'
			grpinivtation.save()
			notify_remove_or_add_user(request.user, user, grpinivtation.group, 'added')
			if grpinivtation.role.name=='publisher' or grpinivtation.role.name=='group_admin':
				remove_or_add_user_feed(user, grpinivtation.group, 'added')

		if status=='Reject' and grpinivtation.status!='Rejected':
			grpinivtation.status = 'Rejected'
			grpinivtation.save()

		return redirect('user_dashboard')

def feed_content(request, pk):
	grpfeeds = ''
	try:
		group = Group.objects.get(pk=pk)
		uid = request.user.id
		membership = GroupMembership.objects.get(user=uid, group=group.pk)
		if membership:
			gfeeds = group.target_actions.all()
			page = request.GET.get('page', 1)
			paginator = Paginator(list(gfeeds), 10)
			try:
				grpfeeds = paginator.page(page)
			except PageNotAnInteger:
				grpfeeds = paginator.page(1)
			except EmptyPage:
				grpfeeds = paginator.page(paginator.num_pages)

	except GroupMembership.DoesNotExist:
		return redirect('group_view', group.pk)
	return render(request, 'groupfeed.html', {'group': group, 'membership':membership, 'grpfeeds':grpfeeds})
