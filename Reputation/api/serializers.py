from rest_framework import serializers
from Reputation.models import CommunityReputaion, FlagReason
from Reputation.models import ArticleScoreLog, ArticleUserScoreLogs, MediaScoreLog, MediaUserScoreLogs
from badges.models import BadgeToUser, Badge

class CommunityReputaionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityReputaion
        fields = [
            'community',
            'user',
            'upvote_count',
            'downvote_count',
            'published_count'
        ]
        
class ArticleScoreLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleScoreLog
        fields = [
            'resource',
            'upvote',
            'downvote',
            'reported',
            'publish'
        ]
class ArticleUserScoreLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleUserScoreLogs
        fields = [
            'resource',
            'user',
            'upvoted',
            'downvoted',
            'reported'
        ]

class MediaScoreLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaScoreLog
        fields = [
            'resource',
            'upvote',
            'downvote',
            'reported',
            'publish'
        ]
class MediaUserScoreLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaUserScoreLogs
        fields = [
            'resource',
            'user',
            'upvoted',
            'downvoted',
            'reported'
        ]

class FlagReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlagReason
        fields = ['id', 'reason']
        
class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['id', 'user', 'level', 'icon', 'title', 'description']

class BadgeToUserSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = BadgeToUser
        fields = ['user', 'badge', 'community']