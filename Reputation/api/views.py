from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from .serializers import CommunityReputaionSerializer
from Reputation.models import CommunityReputaion, ArticleScoreLog, ResourceScore
from rest_framework.permissions import IsAuthenticated
from Community.models import Community, CommunityMembership, CommunityArticles, CommunityGroups
from Group.models import GroupArticles


class FetchCommunityReputation(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk'
    serializer_class = CommunityReputaionSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        cid = self.kwargs['pk']
        community = Community.objects.get(id=cid)
        if CommunityMembership.objects.filter(community=community, user = self.request.user).exists():
            if CommunityReputaion.objects.filter(community=community, user = self.request.user).exists():
                return CommunityReputaion.objects.get(community=community, user = self.request.user)
            else:
                return CommunityReputaion.objects.create(community=community, user = self.request.user)


class ArticlePublishScore(generics.CreateAPIView):
    lookup_field = 'pk'
    serializer_class = CommunityReputaionSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        articleid = self.kwargs['pk']
        artcile = ArticleScoreLog.objects.get(article=articleid)

        if not artcile.publish and article.article.state.name=='publish':
            res = ResourceScore.objects.get(resource_type='resource')
            if CommunityArticles.objects.filter(article=artcile.article).exists():
                comm_article= CommunityArticles.objects.get(article=artcile.article)
                repu = CommunityReputaion.objects.get(community=comm_article.community, user = article.article.created_by)
                repu.score += res.publish_value
                repu.save()
                return repu
            else:
                group_article = GroupArticles.objects.get(artcile= article.article)
                comm_group = CommunityGroups.objects.get(group=group_article.group)
                repu = CommunityReputaion.objects.get(community=comm_group.community, user = article.article.created_by)
                repu.score += res.publish_value
                repu.save()
                return repu