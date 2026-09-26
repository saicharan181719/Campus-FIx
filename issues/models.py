from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Location(models.Model):

    block = models.CharField(max_length=100)
    building = models.CharField(max_length=100, blank=True)
    room = models.CharField(max_length=100, blank=True)
    area = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ['block', 'building', 'room']

    def __str__(self):
        parts = [
            self.block,
            self.building,
            self.room,
            self.area,
        ]

        return " - ".join(
            part for part in parts if part
        )


class Issue(models.Model):

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('reviewed', 'Reviewed'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('reopened', 'Reopened'),
    ]

    ticket_id = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='issues'
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='issues'
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='reported'
    )

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reported_issues'
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_issues'
    )

    image = models.ImageField(
        upload_to='issue_images/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        is_new = self.pk is None
        old_status = None

        if not is_new:
            old_issue = Issue.objects.get(pk=self.pk)
            old_status = old_issue.status

        super().save(*args, **kwargs)

        # Create ticket ID for a new issue
        if is_new and not self.ticket_id:

            self.ticket_id = (
                f"CF-{timezone.now().year}-{self.pk:05d}"
            )

            super().save(
                update_fields=['ticket_id']
            )

            # Create initial status history
            IssueUpdate.objects.create(
                issue=self,
                updated_by=self.reporter,
                status=self.status,
                comment='Issue reported.'
            )

        # Create history when status changes
        elif old_status and old_status != self.status:

            IssueUpdate.objects.create(
                issue=self,
                status=self.status,
                comment=(
                    f'Status changed from '
                    f'{old_status} to {self.status}.'
                )
            )

    def __str__(self):
        return f"{self.ticket_id} - {self.title}"


class IssueUpdate(models.Model):

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name='updates'
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='issue_updates'
    )

    status = models.CharField(
        max_length=20,
        choices=Issue.STATUS_CHOICES
    )

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.issue.ticket_id} - {self.status}"