from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class Profile(models.Model):
    """
    Single owner profile for the portfolio site.
    Tip: keep only ONE Profile row in the DB (the first one is used in views/templates).
    """

    full_name = models.CharField(max_length=150)
    headline = models.CharField(
        max_length=200,
        help_text="Short title, e.g. 'CSE Student & Aspiring SQA/Python Engineer'",
    )
    location = models.CharField(max_length=150, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)

    # Social links
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)

    # Portfolio assets
    cv_file = models.FileField(upload_to="cv/", blank=True, null=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)

    about = models.TextField(help_text="Short bio / summary")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self) -> str:
        return self.full_name


class Experience(models.Model):
    """
    Work/Leadership experience items.
    Supports ongoing roles via is_current=True (end_date should be empty in that case).
    """

    role = models.CharField(max_length=150)
    organization = models.CharField(max_length=150)
    location = models.CharField(max_length=150, blank=True)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)

    description = models.TextField(blank=True, help_text="Key responsibilities, impact, tools used.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]

    def clean(self) -> None:
        # If current, end_date should be empty
        if self.is_current and self.end_date:
            raise ValidationError("If 'is_current' is True, 'end_date' should be empty.")
        # If not current, end_date should be provided (optional rule — comment out if not desired)
        if not self.is_current and self.end_date and self.end_date < self.start_date:
            raise ValidationError("'end_date' cannot be earlier than 'start_date'.")

    def save(self, *args, **kwargs):
        # Normalize: if is_current, force end_date to None
        if self.is_current:
            self.end_date = None
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.role} @ {self.organization}"


class Education(models.Model):
    """
    Education history. end_year can be null for 'Present' if you want.
    """

    institution = models.CharField(max_length=150)
    degree = models.CharField(max_length=150)
    field_of_study = models.CharField(max_length=150, blank=True)

    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(null=True, blank=True)

    result_or_cgpa = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-end_year", "-start_year"]

    def clean(self) -> None:
        if self.end_year is not None and self.end_year < self.start_year:
            raise ValidationError("'end_year' cannot be earlier than 'start_year'.")

    def __str__(self) -> str:
        return f"{self.degree} - {self.institution}"


class Project(models.Model):
    """
    Portfolio projects.
    Slug is auto-generated from title if left blank.
    """

    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)

    short_description = models.CharField(max_length=255)
    long_description = models.TextField(blank=True)

    tech_stack = models.CharField(
        max_length=255,
        help_text="Comma-separated, e.g. 'Python, Django, DRF, PostgreSQL'",
    )

    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)

    is_featured = models.BooleanField(default=False)
    image = models.ImageField(upload_to="projects/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        # Auto-create a unique slug from title if not provided.
        if not self.slug:
            base = slugify(self.title) or "project"
            slug = base
            counter = 1
            while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class ContactMessage(models.Model):
    """
    Contact form submissions.
    Stored in DB so you can view/manage in Django Admin.
    """

    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} - {self.subject}"
