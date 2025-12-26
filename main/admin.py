from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html

from .models import ContactMessage, Education, Experience, Profile, Project


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Keep ONE Profile row in DB (your personal portfolio owner profile).
    """

    list_display = ("full_name", "headline", "email", "updated_at")
    list_editable = ("headline",)
    search_fields = ("full_name", "email", "headline")
    readonly_fields = ("updated_at", "profile_image_preview")

    fieldsets = (
        (
            "Profile Info",
            {
                "fields": (
                    "full_name",
                    "headline",
                    "location",
                    "email",
                    "phone",
                    "linkedin_url",
                    "github_url",
                    "facebook_url",
                    "instagram_url",
                    "cv_file",
                )
            },
        ),
        ("About", {"fields": ("about",)}),
        (
            "Image",
            {
                "fields": ("profile_image", "profile_image_preview"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("updated_at",),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="Profile Image")
    def profile_image_preview(self, obj: Profile):
        if obj.profile_image:
            return format_html(
                '<img src="{}" style="width:100px;height:100px;object-fit:cover;border-radius:50%;border:1px solid #ddd;" />',
                obj.profile_image.url,
            )
        return "No image"


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("role", "organization", "start_date_display", "end_date_display", "is_current")
    list_filter = ("organization", "is_current", "start_date")
    search_fields = ("role", "organization", "location", "description")
    list_editable = ("is_current",)
    date_hierarchy = "start_date"

    fieldsets = (
        ("Position", {"fields": ("role", "organization", "location")}),
        ("Dates", {"fields": ("start_date", "end_date", "is_current")}),
        ("Description", {"fields": ("description",)}),
    )

    @admin.display(description="Start", ordering="start_date")
    def start_date_display(self, obj: Experience):
        return obj.start_date.strftime("%b %Y")

    @admin.display(description="End", ordering="end_date")
    def end_date_display(self, obj: Experience):
        if obj.is_current:
            return "Present"
        if obj.end_date:
            return obj.end_date.strftime("%b %Y")
        return "-"


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("degree", "institution", "years_display", "result_or_cgpa")
    list_filter = ("institution", "start_year")
    search_fields = ("degree", "institution", "field_of_study", "description")
    ordering = ("-end_year", "-start_year")

    fieldsets = (
        ("Education", {"fields": ("institution", "degree", "field_of_study")}),
        ("Years & Result", {"fields": ("start_year", "end_year", "result_or_cgpa")}),
        ("Description", {"fields": ("description",)}),
    )

    @admin.display(description="Years")
    def years_display(self, obj: Education):
        end = obj.end_year if obj.end_year is not None else "Present"
        return f"{obj.start_year}–{end}"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "is_featured", "tech_stack_short", "created_at")
    list_filter = ("is_featured", "created_at")
    list_editable = ("is_featured",)
    search_fields = ("title", "short_description", "tech_stack")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "image_preview")

    fieldsets = (
        ("Project Info", {"fields": ("title", "slug", "is_featured")}),
        ("Description", {"fields": ("short_description", "long_description")}),
        ("Tech & Links", {"fields": ("tech_stack", "github_url", "live_url")}),
        (
            "Image",
            {
                "fields": ("image", "image_preview"),
                "classes": ("collapse",),
            },
        ),
        ("Timestamps", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    @admin.display(description="Tech Stack")
    def tech_stack_short(self, obj: Project):
        return (obj.tech_stack[:60] + "...") if len(obj.tech_stack) > 60 else obj.tech_stack

    @admin.display(description="Project Image")
    def image_preview(self, obj: Project):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:160px;height:105px;object-fit:cover;border:1px solid #ddd;border-radius:6px;" />',
                obj.image.url,
            )
        return "No image"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at",)
    actions = ("mark_as_read", "mark_as_unread")

    @admin.action(description="Mark selected as read")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="Mark selected as unread")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
