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
    profile_image_link = models.CharField(max_length=500, blank=True, help_text="Optional link or path to profile image if not uploading")
    favicon = models.ImageField(upload_to="favicon/", blank=True, null=True, help_text="Site favicon (16x16 or 32x32 PNG)")
    favicon_link = models.CharField(max_length=500, blank=True, help_text="Optional link or path to favicon if not uploading")

    skills = models.CharField(max_length=500, blank=True, help_text="Comma-separated skills/badges, e.g. 'Django, DRF Ready, SQA Mindset'")

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


class SiteSettings(models.Model):
    """
    Site-wide settings for customization.
    Single row expected.
    """

    THEME_CHOICES = [
        ('dark_red', 'Dark Red (Professional)'),
        ('dark_blue', 'Dark Blue (Corporate)'),
        ('dark_green', 'Dark Green (Nature)'),
        ('dark_purple', 'Dark Purple (Creative)'),
        ('ocean_deep', 'Ocean Deep (Calm)'),
        ('sunset_orange', 'Sunset Orange (Warm)'),
        ('forest_dark', 'Forest Dark (Organic)'),
        ('royal_purple', 'Royal Purple (Elegant)'),
        ('cyberpunk', 'Cyberpunk (Futuristic)'),
        ('midnight_blue', 'Midnight Blue (Deep)'),
        ('default', 'Default (Reset to Original)'),
    ]

    site_title = models.CharField(max_length=100, default="Tawfiq Hassan Nayem", help_text="Site title for browser tab")
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='dark_red', help_text="Choose a color theme for the entire site")
    primary_color = models.CharField(max_length=7, default="#b31919", help_text="Primary color (hex, e.g. #b31919)")
    secondary_color = models.CharField(max_length=7, default="#333333", help_text="Secondary color (hex, e.g. #333333)")
    accent_color = models.CharField(max_length=7, default="#ffffff", help_text="Accent color (hex, e.g. #ffffff)")

    # Additional page content
    about_page_title = models.CharField(max_length=100, default="About Me", help_text="Title for About page")
    about_page_subtitle = models.CharField(max_length=200, default="Get to know me better", help_text="Subtitle for About page")
    about_page_content = models.TextField(blank=True, help_text="Content for About page")
    experience_page_title = models.CharField(max_length=100, default="Experience", help_text="Title for Experience page")
    experience_page_content = models.TextField(blank=True, help_text="Content for Experience page")
    projects_page_title = models.CharField(max_length=100, default="Projects", help_text="Title for Projects page")
    projects_page_content = models.TextField(blank=True, help_text="Content for Projects page")
    contact_page_title = models.CharField(max_length=100, default="Contact", help_text="Title for Contact page")
    contact_page_content = models.TextField(blank=True, help_text="Content for Contact page")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def get_theme_colors(self):
        """Return comprehensive theme colors based on selected theme"""
        themes = {
            'dark_red': {
                # Primary colors
                'primary': '#b31919',
                'secondary': '#8b0000',
                'accent': '#ffffff',

                # Background layers
                'bg0': '#0b0b0d',      # Main background
                'bg1': '#111115',      # Secondary background
                'bg2': '#1a1a1f',      # Tertiary background
                'navbar_bg': 'rgba(10,10,14,.85)',  # Navbar background
                'card': '#14141a',     # Card backgrounds
                'card_hover': '#1a1a20', # Card hover state
                'footer_bg': 'rgba(20,20,26,.95)', # Footer background

                # Text colors
                'text': '#e9e9ee',     # Primary text
                'text_secondary': '#d1d1d6', # Secondary text
                'muted': '#b5b5c2',   # Muted text
                'muted_light': '#9a9aad', # Lighter muted text
                'navbar_text': '#e9e9ee', # Navbar text
                'navbar_muted': '#b5b5c2', # Navbar muted text

                # Border and separator colors
                'border': '#262633',  # Primary borders
                'border_light': '#3a3a4a', # Light borders
                'divider': 'rgba(38,38,51,.9)', # Dividers

                # Interactive elements
                'btn_primary': 'linear-gradient(180deg, #b31919, #8b0000)',
                'btn_primary_hover': 'linear-gradient(180deg, #c82323, #990000)',
                'btn_ghost': 'rgba(255,255,255,.03)',
                'btn_ghost_hover': 'rgba(255,255,255,.08)',
                'btn_ghost_border': 'rgba(255,255,255,.12)',

                # Special elements
                'glow': 'rgba(179,19,19,.35)', # Glow effects
                'glow_line': 'linear-gradient(90deg, transparent, rgba(179,19,19,.75), transparent)',
                'badge_bg': 'rgba(179,19,19,.12)',
                'badge_border': 'rgba(179,19,19,.25)',
                'badge_text': '#ffd0d0',
                'pill_bg': 'rgba(255,255,255,.03)',
                'pill_border': 'rgba(255,255,255,.12)',
                'pill_text': '#b5b5c2',

                # Links
                'link': '#ffb3b3',
                'link_hover': '#ffd0d0',

                # Form elements
                'form_bg': 'rgba(255,255,255,.04)',
                'form_border': 'rgba(255,255,255,.10)',
                'form_focus_bg': 'rgba(255,255,255,.05)',
                'form_focus_border': 'rgba(179,19,19,.55)',
                'form_focus_shadow': 'rgba(179,19,19,.18)',

                # Timeline
                'timeline_line': 'rgba(179,19,19,.35)',
                'timeline_dot': '#b31919',
                'timeline_glow': 'rgba(179,19,19,.35)',
            },
            'dark_blue': {
                'primary': '#1e40af',
                'secondary': '#1e3a8a',
                'accent': '#ffffff',
                'bg0': '#0f172a',
                'bg1': '#1e293b',
                'bg2': '#334155',
                'navbar_bg': 'rgba(15,23,42,.85)',
                'card': '#1e293b',
                'card_hover': '#334155',
                'footer_bg': 'rgba(30,41,59,.95)',
                'text': '#f1f5f9',
                'text_secondary': '#e2e8f0',
                'muted': '#94a3b8',
                'muted_light': '#cbd5e1',
                'navbar_text': '#f1f5f9',
                'navbar_muted': '#94a3b8',
                'border': '#475569',
                'border_light': '#64748b',
                'divider': 'rgba(71,85,105,.9)',
                'btn_primary': 'linear-gradient(180deg, #1e40af, #1e3a8a)',
                'btn_primary_hover': 'linear-gradient(180deg, #2563eb, #1d4ed8)',
                'btn_ghost': 'rgba(255,255,255,.03)',
                'btn_ghost_hover': 'rgba(255,255,255,.08)',
                'btn_ghost_border': 'rgba(255,255,255,.12)',
                'glow': 'rgba(30,64,175,.35)',
                'glow_line': 'linear-gradient(90deg, transparent, rgba(30,64,175,.75), transparent)',
                'badge_bg': 'rgba(30,64,175,.12)',
                'badge_border': 'rgba(30,64,175,.25)',
                'badge_text': '#bfdbfe',
                'pill_bg': 'rgba(255,255,255,.03)',
                'pill_border': 'rgba(255,255,255,.12)',
                'pill_text': '#94a3b8',
                'link': '#93c5fd',
                'link_hover': '#bfdbfe',
                'form_bg': 'rgba(255,255,255,.04)',
                'form_border': 'rgba(255,255,255,.10)',
                'form_focus_bg': 'rgba(255,255,255,.05)',
                'form_focus_border': 'rgba(30,64,175,.55)',
                'form_focus_shadow': 'rgba(30,64,175,.18)',
                'timeline_line': 'rgba(30,64,175,.35)',
                'timeline_dot': '#1e40af',
                'timeline_glow': 'rgba(30,64,175,.35)',
            },
            'dark_green': {
                'primary': '#059669',
                'secondary': '#047857',
                'accent': '#ffffff',
                'bg0': '#064e3b',
                'bg1': '#065f46',
                'bg2': '#0f766e',
                'navbar_bg': 'rgba(6,78,59,.85)',
                'card': '#065f46',
                'card_hover': '#0f766e',
                'footer_bg': 'rgba(6,95,70,.95)',
                'text': '#ecfdf5',
                'text_secondary': '#d1fae5',
                'muted': '#6ee7b7',
                'muted_light': '#a7f3d0',
                'navbar_text': '#ecfdf5',
                'navbar_muted': '#6ee7b7',
                'border': '#10b981',
                'border_light': '#34d399',
                'divider': 'rgba(16,185,129,.9)',
                'btn_primary': 'linear-gradient(180deg, #059669, #047857)',
                'btn_primary_hover': 'linear-gradient(180deg, #10b981, #059669)',
                'btn_ghost': 'rgba(255,255,255,.03)',
                'btn_ghost_hover': 'rgba(255,255,255,.08)',
                'btn_ghost_border': 'rgba(255,255,255,.12)',
                'glow': 'rgba(5,150,105,.35)',
                'glow_line': 'linear-gradient(90deg, transparent, rgba(5,150,105,.75), transparent)',
                'badge_bg': 'rgba(5,150,105,.12)',
                'badge_border': 'rgba(5,150,105,.25)',
                'badge_text': '#d1fae5',
                'pill_bg': 'rgba(255,255,255,.03)',
                'pill_border': 'rgba(255,255,255,.12)',
                'pill_text': '#6ee7b7',
                'link': '#6ee7b7',
                'link_hover': '#a7f3d0',
                'form_bg': 'rgba(255,255,255,.04)',
                'form_border': 'rgba(255,255,255,.10)',
                'form_focus_bg': 'rgba(255,255,255,.05)',
                'form_focus_border': 'rgba(5,150,105,.55)',
                'form_focus_shadow': 'rgba(5,150,105,.18)',
                'timeline_line': 'rgba(5,150,105,.35)',
                'timeline_dot': '#059669',
                'timeline_glow': 'rgba(5,150,105,.35)',
            },
            'dark_purple': {
                'primary': '#7c3aed',
                'secondary': '#6d28d9',
                'accent': '#ffffff',
                'bg0': '#2d1b69',
                'bg1': '#3730a3',
                'bg2': '#4c1d95',
                'navbar_bg': 'rgba(45,27,105,.85)',
                'card': '#3730a3',
                'card_hover': '#4c1d95',
                'footer_bg': 'rgba(55,48,163,.95)',
                'text': '#f3e8ff',
                'text_secondary': '#e9d5ff',
                'muted': '#c4b5fd',
                'muted_light': '#ddd6fe',
                'navbar_text': '#f3e8ff',
                'navbar_muted': '#c4b5fd',
                'border': '#8b5cf6',
                'border_light': '#a78bfa',
                'divider': 'rgba(139,92,246,.9)',
                'btn_primary': 'linear-gradient(180deg, #7c3aed, #6d28d9)',
                'btn_primary_hover': 'linear-gradient(180deg, #8b5cf6, #7c3aed)',
                'btn_ghost': 'rgba(255,255,255,.03)',
                'btn_ghost_hover': 'rgba(255,255,255,.08)',
                'btn_ghost_border': 'rgba(255,255,255,.12)',
                'glow': 'rgba(124,58,237,.35)',
                'glow_line': 'linear-gradient(90deg, transparent, rgba(124,58,237,.75), transparent)',
                'badge_bg': 'rgba(124,58,237,.12)',
                'badge_border': 'rgba(124,58,237,.25)',
                'badge_text': '#e9d5ff',
                'pill_bg': 'rgba(255,255,255,.03)',
                'pill_border': 'rgba(255,255,255,.12)',
                'pill_text': '#c4b5fd',
                'link': '#c4b5fd',
                'link_hover': '#ddd6fe',
                'form_bg': 'rgba(255,255,255,.04)',
                'form_border': 'rgba(255,255,255,.10)',
                'form_focus_bg': 'rgba(255,255,255,.05)',
                'form_focus_border': 'rgba(124,58,237,.55)',
                'form_focus_shadow': 'rgba(124,58,237,.18)',
                'timeline_line': 'rgba(124,58,237,.35)',
                'timeline_dot': '#7c3aed',
                'timeline_glow': 'rgba(124,58,237,.35)',
            },
            'ocean_deep': {
                'primary': '#0ea5e9',
                'secondary': '#0284c7',
                'accent': '#ffffff',
                'bg0': '#0c4a6e',
                'bg1': '#075985',
                'bg2': '#0369a1',
                'navbar_bg': 'rgba(12,74,110,.85)',
                'card': '#075985',
                'card_hover': '#0369a1',
                'footer_bg': 'rgba(7,89,133,.95)',
                'text': '#f0f9ff',
                'text_secondary': '#e0f2fe',
                'muted': '#7dd3fc',
                'muted_light': '#bae6fd',
                'navbar_text': '#f0f9ff',
                'navbar_muted': '#7dd3fc',
                'border': '#0ea5e9',
                'border_light': '#38bdf8',
                'divider': 'rgba(14,165,233,.9)',
                'btn_primary': 'linear-gradient(180deg, #0ea5e9, #0284c7)',
                'btn_primary_hover': 'linear-gradient(180deg, #38bdf8, #0ea5e9)',
                'btn_ghost': 'rgba(255,255,255,.03)',
                'btn_ghost_hover': 'rgba(255,255,255,.08)',
                'btn_ghost_border': 'rgba(255,255,255,.12)',
                'glow': 'rgba(14,165,233,.35)',
                'glow_line': 'linear-gradient(90deg, transparent, rgba(14,165,233,.75), transparent)',
                'badge_bg': 'rgba(14,165,233,.12)',
                'badge_border': 'rgba(14,165,233,.25)',
                'badge_text': '#bae6fd',
                'pill_bg': 'rgba(255,255,255,.03)',
                'pill_border': 'rgba(255,255,255,.12)',
                'pill_text': '#7dd3fc',
                'link': '#7dd3fc',
                'link_hover': '#bae6fd',
                'form_bg': 'rgba(255,255,255,.04)',
                'form_border': 'rgba(255,255,255,.10)',
                'form_focus_bg': 'rgba(255,255,255,.05)',
                'form_focus_border': 'rgba(14,165,233,.55)',
                'form_focus_shadow': 'rgba(14,165,233,.18)',
                'timeline_line': 'rgba(14,165,233,.35)',
                'timeline_dot': '#0ea5e9',
                'timeline_glow': 'rgba(14,165,233,.35)',
            },
            'sunset_orange': {
                'primary': '#ea580c',
                'secondary': '#c2410c',
                'accent': '#ffffff',
                'bg0': '#7c2d12',
                'bg1': '#9a3412',
                'bg2': '#c2410c',
                'navbar_bg': 'rgba(124,45,18,.85)',
                'card': '#9a3412',
                'card_hover': '#c2410c',
                'footer_bg': 'rgba(154,52,18,.95)',
                'text': '#fff7ed',
                'text_secondary': '#fed7aa',
                'muted': '#fdba74',
                'muted_light': '#fed7aa',
                'navbar_text': '#fff7ed',
                'navbar_muted': '#fdba74',
                'border': '#ea580c',
                'border_light': '#f97316',
                'divider': 'rgba(234,88,12,.9)',
                'btn_primary': 'linear-gradient(180deg, #ea580c, #c2410c)',
                'btn_primary_hover': 'linear-gradient(180deg, #f97316, #ea580c)',
                'btn_ghost': 'rgba(255,255,255,.03)',
                'btn_ghost_hover': 'rgba(255,255,255,.08)',
                'btn_ghost_border': 'rgba(255,255,255,.12)',
                'glow': 'rgba(234,88,12,.35)',
                'glow_line': 'linear-gradient(90deg, transparent, rgba(234,88,12,.75), transparent)',
                'badge_bg': 'rgba(234,88,12,.12)',
                'badge_border': 'rgba(234,88,12,.25)',
                'badge_text': '#fed7aa',
                'pill_bg': 'rgba(255,255,255,.03)',
                'pill_border': 'rgba(255,255,255,.12)',
                'pill_text': '#fdba74',
                'link': '#fdba74',
                'link_hover': '#fed7aa',
                'form_bg': 'rgba(255,255,255,.04)',
                'form_border': 'rgba(255,255,255,.10)',
                'form_focus_bg': 'rgba(255,255,255,.05)',
                'form_focus_border': 'rgba(234,88,12,.55)',
                'form_focus_shadow': 'rgba(234,88,12,.18)',
                'timeline_line': 'rgba(234,88,12,.35)',
                'timeline_dot': '#ea580c',
                'timeline_glow': 'rgba(234,88,12,.35)',
            },
            'forest_dark': {
                'primary': '#166534',
                'secondary': '#14532d',
                'accent': '#ffffff',
                'bg0': '#1a2e05',
                'bg1': '#365314',
                'bg2': '#4d7c0f',
                'navbar_bg': 'rgba(26,46,5,.85)',
                'card': '#365314',
                'card_hover': '#4d7c0f',
                'footer_bg': 'rgba(54,83,20,.95)',
                'text': '#f7fee7',
                'text_secondary': '#ecfccb',
                'muted': '#bef264',
                'muted_light': '#d9f99d',
                'navbar_text': '#f7fee7',
                'navbar_muted': '#bef264',
                'border': '#65a30d',
                'border_light': '#84cc16',
                'divider': 'rgba(101,163,13,.9)',
                'btn_primary': 'linear-gradient(180deg, #166534, #14532d)',
                'btn_primary_hover': 'linear-gradient(180deg, #22c55e, #16a34a)',
                'btn_ghost': 'rgba(255,255,255,.03)',
                'btn_ghost_hover': 'rgba(255,255,255,.08)',
                'btn_ghost_border': 'rgba(255,255,255,.12)',
                'glow': 'rgba(22,163,74,.35)',
                'glow_line': 'linear-gradient(90deg, transparent, rgba(22,163,74,.75), transparent)',
                'badge_bg': 'rgba(22,163,74,.12)',
                'badge_border': 'rgba(22,163,74,.25)',
                'badge_text': '#d9f99d',
                'pill_bg': 'rgba(255,255,255,.03)',
                'pill_border': 'rgba(255,255,255,.12)',
                'pill_text': '#bef264',
                'link': '#bef264',
                'link_hover': '#d9f99d',
                'form_bg': 'rgba(255,255,255,.04)',
                'form_border': 'rgba(255,255,255,.10)',
                'form_focus_bg': 'rgba(255,255,255,.05)',
                'form_focus_border': 'rgba(22,163,74,.55)',
                'form_focus_shadow': 'rgba(22,163,74,.18)',
                'timeline_line': 'rgba(22,163,74,.35)',
                'timeline_dot': '#166534',
                'timeline_glow': 'rgba(22,163,74,.35)',
            },
            'royal_purple': {
                'primary': '#581c87',
                'secondary': '#4c1d95',
                'accent': '#ffffff',
                'bg0': '#2d1b69',
                'bg1': '#4c1d95',
                'bg2': '#6d28d9',
                'navbar_bg': 'rgba(45,27,105,.85)',
                'card': '#4c1d95',
                'card_hover': '#6d28d9',
                'footer_bg': 'rgba(76,29,149,.95)',
                'text': '#faf5ff',
                'text_secondary': '#f3e8ff',
                'muted': '#d8b4fe',
                'muted_light': '#e9d5ff',
                'navbar_text': '#faf5ff',
                'navbar_muted': '#d8b4fe',
                'border': '#7c3aed',
                'border_light': '#8b5cf6',
                'divider': 'rgba(124,58,237,.9)',
                'btn_primary': 'linear-gradient(180deg, #581c87, #4c1d95)',
                'btn_primary_hover': 'linear-gradient(180deg, #7c3aed, #6d28d9)',
                'btn_ghost': 'rgba(255,255,255,.03)',
                'btn_ghost_hover': 'rgba(255,255,255,.08)',
                'btn_ghost_border': 'rgba(255,255,255,.12)',
                'glow': 'rgba(88,28,135,.35)',
                'glow_line': 'linear-gradient(90deg, transparent, rgba(88,28,135,.75), transparent)',
                'badge_bg': 'rgba(88,28,135,.12)',
                'badge_border': 'rgba(88,28,135,.25)',
                'badge_text': '#e9d5ff',
                'pill_bg': 'rgba(255,255,255,.03)',
                'pill_border': 'rgba(255,255,255,.12)',
                'pill_text': '#d8b4fe',
                'link': '#d8b4fe',
                'link_hover': '#e9d5ff',
                'form_bg': 'rgba(255,255,255,.04)',
                'form_border': 'rgba(255,255,255,.10)',
                'form_focus_bg': 'rgba(255,255,255,.05)',
                'form_focus_border': 'rgba(88,28,135,.55)',
                'form_focus_shadow': 'rgba(88,28,135,.18)',
                'timeline_line': 'rgba(88,28,135,.35)',
                'timeline_dot': '#581c87',
                'timeline_glow': 'rgba(88,28,135,.35)',
            },
            'cyberpunk': {
                'primary': '#00ff88',
                'secondary': '#00cc66',
                'accent': '#ffffff',
                'bg0': '#0a0a0a',
                'bg1': '#1a1a1a',
                'bg2': '#2a2a2a',
                'navbar_bg': 'rgba(10,10,10,.85)',
                'card': '#1a1a1a',
                'card_hover': '#2a2a2a',
                'footer_bg': 'rgba(26,26,26,.95)',
                'text': '#ffffff',
                'text_secondary': '#f0f0f0',
                'muted': '#00ff88',
                'muted_light': '#33ff99',
                'navbar_text': '#ffffff',
                'navbar_muted': '#00ff88',
                'border': '#00ff88',
                'border_light': '#33ff99',
                'divider': 'rgba(0,255,136,.9)',
                'btn_primary': 'linear-gradient(180deg, #00ff88, #00cc66)',
                'btn_primary_hover': 'linear-gradient(180deg, #33ff99, #00ff88)',
                'btn_ghost': 'rgba(255,255,255,.03)',
                'btn_ghost_hover': 'rgba(255,255,255,.08)',
                'btn_ghost_border': 'rgba(255,255,255,.12)',
                'glow': 'rgba(0,255,136,.35)',
                'glow_line': 'linear-gradient(90deg, transparent, rgba(0,255,136,.75), transparent)',
                'badge_bg': 'rgba(0,255,136,.12)',
                'badge_border': 'rgba(0,255,136,.25)',
                'badge_text': '#33ff99',
                'pill_bg': 'rgba(255,255,255,.03)',
                'pill_border': 'rgba(255,255,255,.12)',
                'pill_text': '#00ff88',
                'link': '#00ff88',
                'link_hover': '#33ff99',
                'form_bg': 'rgba(255,255,255,.04)',
                'form_border': 'rgba(255,255,255,.10)',
                'form_focus_bg': 'rgba(255,255,255,.05)',
                'form_focus_border': 'rgba(0,255,136,.55)',
                'form_focus_shadow': 'rgba(0,255,136,.18)',
                'timeline_line': 'rgba(0,255,136,.35)',
                'timeline_dot': '#00ff88',
                'timeline_glow': 'rgba(0,255,136,.35)',
            },
            'midnight_blue': {
                'primary': '#1e1b4b',
                'secondary': '#312e81',
                'accent': '#ffffff',
                'bg0': '#0f0a1a',
                'bg1': '#1e1b4b',
                'bg2': '#312e81',
                'navbar_bg': 'rgba(15,10,26,.85)',
                'card': '#1e1b4b',
                'card_hover': '#312e81',
                'footer_bg': 'rgba(30,27,75,.95)',
                'text': '#f8fafc',
                'text_secondary': '#e2e8f0',
                'muted': '#a5b4fc',
                'muted_light': '#c7d2fe',
                'navbar_text': '#f8fafc',
                'navbar_muted': '#a5b4fc',
                'border': '#6366f1',
                'border_light': '#818cf8',
                'divider': 'rgba(99,102,241,.9)',
                'btn_primary': 'linear-gradient(180deg, #1e1b4b, #312e81)',
                'btn_primary_hover': 'linear-gradient(180deg, #3730a3, #4338ca)',
                'btn_ghost': 'rgba(255,255,255,.03)',
                'btn_ghost_hover': 'rgba(255,255,255,.08)',
                'btn_ghost_border': 'rgba(255,255,255,.12)',
                'glow': 'rgba(30,27,75,.35)',
                'glow_line': 'linear-gradient(90deg, transparent, rgba(30,27,75,.75), transparent)',
                'badge_bg': 'rgba(30,27,75,.12)',
                'badge_border': 'rgba(30,27,75,.25)',
                'badge_text': '#c7d2fe',
                'pill_bg': 'rgba(255,255,255,.03)',
                'pill_border': 'rgba(255,255,255,.12)',
                'pill_text': '#a5b4fc',
                'link': '#a5b4fc',
                'link_hover': '#c7d2fe',
                'form_bg': 'rgba(255,255,255,.04)',
                'form_border': 'rgba(255,255,255,.10)',
                'form_focus_bg': 'rgba(255,255,255,.05)',
                'form_focus_border': 'rgba(30,27,75,.55)',
                'form_focus_shadow': 'rgba(30,27,75,.18)',
                'timeline_line': 'rgba(30,27,75,.35)',
                'timeline_dot': '#1e1b4b',
                'timeline_glow': 'rgba(30,27,75,.35)',
            },
            'default': {
                # Original hardcoded values from the CSS
                'primary': '#b31919',
                'secondary': '#8b0000',
                'accent': '#ffffff',
                'bg0': '#0b0b0d',
                'bg1': '#111115',
                'bg2': '#1a1a1f',
                'navbar_bg': 'rgba(10,10,14,.55)',
                'card': 'linear-gradient(180deg, rgba(20,20,26,.96), rgba(16,16,22,.92))',
                'card_hover': 'linear-gradient(180deg, rgba(20,20,26,.96), rgba(16,16,22,.92))',
                'footer_bg': 'rgba(20,20,26,.95)',
                'text': '#e9e9ee',
                'text_secondary': '#d1d1d6',
                'muted': '#b5b5c2',
                'muted_light': '#9a9aad',
                'navbar_text': '#e9e9ee',
                'navbar_muted': '#b5b5c2',
                'border': 'rgba(38,38,51,.6)',
                'border_light': '#3a3a4a',
                'divider': 'rgba(38,38,51,.9)',
                'btn_primary': 'linear-gradient(180deg, #b31919, #8b0000)',
                'btn_primary_hover': 'linear-gradient(180deg, #c82323, #990000)',
                'btn_ghost': 'rgba(255,255,255,.03)',
                'btn_ghost_hover': 'rgba(255,255,255,.06)',
                'btn_ghost_border': 'rgba(255,255,255,.12)',
                'glow': 'rgba(179,19,19,.22)',
                'glow_line': 'linear-gradient(90deg, transparent, rgba(179,19,19,.75), transparent)',
                'badge_bg': 'rgba(179,19,19,.12)',
                'badge_border': 'rgba(179,19,19,.25)',
                'badge_text': '#ffd0d0',
                'pill_bg': 'rgba(255,255,255,.03)',
                'pill_border': 'rgba(255,255,255,.12)',
                'pill_text': '#b5b5c2',
                'link': '#ffb3b3',
                'link_hover': '#ffd0d0',
                'form_bg': 'rgba(255,255,255,.04)',
                'form_border': 'rgba(255,255,255,.10)',
                'form_focus_bg': 'rgba(255,255,255,.05)',
                'form_focus_border': 'rgba(179,19,19,.55)',
                'form_focus_shadow': 'rgba(179,19,19,.18)',
                'timeline_line': 'rgba(179,19,19,.35)',
                'timeline_dot': '#b31919',
                'timeline_glow': 'rgba(179,19,19,.35)',
            },
        }
        return themes.get(self.theme, themes['dark_red'])

    def __str__(self) -> str:
        return "Site Settings"


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
