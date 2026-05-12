from rest_framework import serializers
from apps.records.models import Attempt, Progress
from apps.users.models import User
from apps.courses.models import Node
import copy

class AttemptSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attempt
        fields = ['user', 'node', 'date', 'attempt']

    def to_representation(self, instance):
        
        response = super().to_representation(instance)

        # Ajout des actions possibles sur ce noeud pour le frontend
        request = self.context.get('request')
        user = request.user if request else None
        
        correction_included = False 
        if user and user.is_authenticated:
            if user.is_staff or user.is_superuser or getattr(instance.node, 'owner', None) == user or \
                user.role == User.Role.TEACHER or Progress.objects.filter(user=user, node=instance.node, status=Progress.Status.COMPLETED).exists():
                correction_included = True

        response['correction_included'] = correction_included


        if not correction_included:
            
            attempt = copy.deepcopy(response.get("attempt", {}))

            if attempt.get("node") and attempt.get("node").get("type") == Node.Type.QUIZ:
                if isinstance(attempt.get("node").get("content"), list):
                    for question in attempt.get("node").get("content"):
                        if isinstance(question, dict):
                            question.pop("answers", None)
            elif attempt.get("node") and attempt.get("node").get("type") == Node.Type.EXERCISE:
                if isinstance(attempt.get("node").get("content"), dict):
                    attempt.get("node").get("content").pop("answer", None)
            
            response["attempt"] = attempt
        
        return response