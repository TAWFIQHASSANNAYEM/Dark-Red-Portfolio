# Main/forms.py
from __future__ import annotations

from django import forms
from .models import Profile, Project, Education, Experience, SiteSettings


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "full_name",
            "headline",
            "location",
            "email",
            "phone",
            "linkedin_url",
            "github_url",
            "facebook_url",
            "instagram_url",
            "about",
            "cv_file",
            "profile_image",
            "profile_image_link",
            "favicon",
            "favicon_link",
            "skills",
        ]
        widgets = {
            "about": forms.Textarea(attrs={"rows": 6}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "slug",
            "short_description",
            "long_description",
            "tech_stack",
            "github_url",
            "live_url",
            "is_featured",
            "image",
        ]
        widgets = {
            "short_description": forms.Textarea(attrs={"rows": 2}),
            "long_description": forms.Textarea(attrs={"rows": 6}),
            "tech_stack": forms.TextInput(attrs={"placeholder": "Python, Django, DRF, PostgreSQL"}),
        }


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = [
            "institution",
            "degree",
            "field_of_study",
            "start_year",
            "end_year",
            "result_or_cgpa",
            "description",
        ]


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = [
            "role",
            "organization",
            "location",
            "start_date",
            "end_date",
            "is_current",
            "description",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 5}),
        }


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            "site_title",
            "theme",
            "primary_color",
            "secondary_color",
            "accent_color",
            "about_page_title",
            "about_page_subtitle",
            "about_page_content",
            "experience_page_title",
            "experience_page_content",
            "projects_page_title",
            "projects_page_content",
            "contact_page_title",
            "contact_page_content",
        ]
        widgets = {
            "about_page_content": forms.Textarea(attrs={"rows": 6}),
            "experience_page_content": forms.Textarea(attrs={"rows": 6}),
            "projects_page_content": forms.Textarea(attrs={"rows": 6}),
            "contact_page_content": forms.Textarea(attrs={"rows": 6}),
        }
