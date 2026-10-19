from rest_framework import serializers
from .models import Category, Ticket


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "code")


class TicketSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(
        source="get_priority_display", read_only=True
    )

    class Meta:
        model = Ticket
        fields = (
            "id",
            "title",
            "description",
            "category",
            "category_name",
            "status",
            "status_display",
            "priority",
            "priority_display",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate_title(self, value):
        cleaned = value.strip()
        if len(cleaned) < 5:
            raise serializers.ValidationError(
                "Тема обращения должна содержать не менее 5 символов."
            )
        return cleaned

    def validate(self, attrs):
        if self.instance is None:
            if attrs.get("status", Ticket.Status.NEW) != Ticket.Status.NEW:
                raise serializers.ValidationError(
                    {"status": "Новое обращение всегда создается в статусе «Новая»."}
                )
            return attrs

        old_status = self.instance.status
        new_status = attrs.get("status", old_status)

        allowed_transitions = {
            Ticket.Status.NEW: {Ticket.Status.PROGRESS},
            Ticket.Status.PROGRESS: {Ticket.Status.DONE},
            Ticket.Status.DONE: set(),
        }

        if new_status != old_status:
            if new_status not in allowed_transitions[old_status]:
                raise serializers.ValidationError(
                    {
                        "status": f"Недопустимый перевод статуса из «{self.instance.get_status_display()}» в требуемый."
                    }
                )
        return attrs
