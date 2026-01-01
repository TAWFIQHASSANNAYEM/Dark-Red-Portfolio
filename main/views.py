from __future__ import annotations

from django.shortcuts import render, redirect
from django.contrib import messages

from .models import Profile, Experience, Education, Project, ContactMessage, SiteSettings

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .forms import ProfileForm, ProjectForm, EducationForm, ExperienceForm, SiteSettingsForm

def home_view(request):
    """
    Home page view.

    Displays:
    - Profile summary (name, headline, about)
    - Recent experience
    - Education
    - Featured projects
    - All projects count / preview
    """
    profile = Profile.objects.first()
    if profile and profile.skills:
        skills_list = [skill.strip() for skill in profile.skills.split(',')]
    else:
        skills_list = []

    context = {
        "profile": profile,                     # Portfolio owner
        "skills_list": skills_list,            # Split skills for template
        "experiences": Experience.objects.all(),               # Work / leadership history
        "educations": Education.objects.all(),                 # Academic background
        "featured_projects": Project.objects.filter(is_featured=True),
        "all_projects": Project.objects.all(),
    }
    return render(request, "home.html", context)


def about_view(request):
    """
    About page view.

    Displays:
    - Profile bio / summary
    - Education history
    """
    profile = Profile.objects.first()
    if profile and profile.skills:
        skills_list = list(set(skill.strip() for skill in profile.skills.split(',')))
    else:
        skills_list = []

    context = {
        "profile": profile,
        "skills_list": skills_list,
        "educations": Education.objects.all(),
    }
    return render(request, "about.html", context)


def experience_view(request):
    """
    Experience page view.

    Displays:
    - Detailed work / leadership experience timeline
    - Education summary (optional sidebar)
    """
    context = {
        "profile": Profile.objects.first(),
        "site_settings": SiteSettings.objects.first(),
        "experiences": Experience.objects.all(),
        "educations": Education.objects.all(),
    }
    return render(request, "experience.html", context)


def projects_view(request):
    """
    Projects page view.

    Displays:
    - All projects
    - Highlights featured projects separately
    """
    context = {
        "profile": Profile.objects.first(),
        "site_settings": SiteSettings.objects.first(),
        "projects": Project.objects.all(),
        "featured_projects": Project.objects.filter(is_featured=True),
    }
    return render(request, "projects.html", context)


def contact_view(request):
    """
    Contact page view.

    Handles:
    - Displaying the contact form
    - Saving submitted messages to the database
    - Showing success / error feedback messages
    """
    profile = Profile.objects.first()
    site_settings = SiteSettings.objects.first()

    if request.method == "POST":
        # Safely extract and clean form data
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        # Basic validation (kept simple for portfolio use)
        if not name or not email or not message:
            messages.error(request, "Please fill in all required fields.")
            return redirect("contact")

        # Persist message to database (viewable in Admin)
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )

        messages.success(
            request,
            "Message sent successfully! I’ll get back to you soon.",
        )
        return redirect("contact")

    return render(request, "contact.html", {"profile": profile, "site_settings": site_settings})


def dashboard_view(request):
    """
    Hidden dashboard: overview + quick links.
    Only logged-in users can access.
    """
    profile = Profile.objects.first()
    site_settings = SiteSettings.objects.first()
    context = {
        "profile": profile,
        "site_settings": site_settings,
        "projects": Project.objects.all(),
        "featured_projects": Project.objects.filter(is_featured=True),
        "experiences": Experience.objects.all(),
        "educations": Education.objects.all(),
        }

    return render(request, "dashboard/dashboard.html", context)


@login_required
def dashboard_profile_edit_view(request):
    """
    Edit your Profile from frontend.
    Creates a Profile row automatically if none exists.
    """
    profile = Profile.objects.first()
    if not profile:
        profile = Profile.objects.create(
            full_name="Your Name",
            headline="Your Headline",
            email="you@example.com",
            about="Write your bio here...",
        )

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("main:dashboard")
    else:
        form = ProfileForm(instance=profile)

    return render(
        request,
        "dashboard/profile_edit.html",
        {"profile": profile, "form": form},
    )


@login_required
def dashboard_project_add_view(request):
    """
    Add a new Project from frontend.
    """
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Project added successfully.")
            return redirect("main:dashboard")
    else:
        form = ProjectForm()

    return render(request, "dashboard/project_form.html", {"form": form, "mode": "add"})


@login_required
def dashboard_project_edit_view(request, pk: int):
    """
    Edit an existing Project from frontend.
    """
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully.")
            return redirect("main:dashboard")
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "dashboard/project_form.html",
        {"form": form, "mode": "edit", "project": project},
    )


@login_required
def dashboard_project_delete_view(request, pk: int):
    """
    Confirm + delete a Project.
    """
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted successfully.")
        return redirect("main:dashboard")

    return render(request, "dashboard/project_delete.html", {"project": project})


@login_required
def dashboard_education_add_view(request):
    """
    Dashboard: Add a new Education entry.
    Only accessible to authenticated users.
    """
    profile = Profile.objects.first()

    if request.method == "POST":
        form = EducationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Education added successfully.")
            return redirect("main:dashboard")
        messages.error(request, "Please correct the errors below.")
    else:
        form = EducationForm()

    return render(
        request,
        "dashboard/education_form.html",
        {
            "profile": profile,
            "form": form,
            "mode": "add",
        },
    )


@login_required
def dashboard_education_edit_view(request, pk: int):
    """
    Dashboard: Edit an existing Education entry.
    """
    profile = Profile.objects.first()
    education = get_object_or_404(Education, pk=pk)

    if request.method == "POST":
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, "Education updated successfully.")
            return redirect("main:dashboard")
        messages.error(request, "Please correct the errors below.")
    else:
        form = EducationForm(instance=education)

    return render(
        request,
        "dashboard/education_form.html",
        {
            "profile": profile,
            "form": form,
            "mode": "edit",
            "education": education,
        },
    )


@login_required
def dashboard_education_delete_view(request, pk: int):
    """
    Dashboard: Confirm + delete an Education entry.
    """
    profile = Profile.objects.first()
    education = get_object_or_404(Education, pk=pk)

    if request.method == "POST":
        education.delete()
        messages.success(request, "Education deleted successfully.")
        return redirect("main:dashboard")

    return render(
        request,
        "dashboard/education_delete.html",
        {
            "profile": profile,
            "education": education,
        },
    )


@login_required
def dashboard_experience_add_view(request):
    """
    Dashboard: Add a new Experience entry.
    """
    profile = Profile.objects.first()

    if request.method == "POST":
        form = ExperienceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Experience added successfully.")
            return redirect("main:dashboard")
        messages.error(request, "Please correct the errors below.")
    else:
        form = ExperienceForm()

    return render(
        request,
        "dashboard/experience_form.html",
        {"profile": profile, "form": form, "mode": "add"},
    )


@login_required
def dashboard_experience_edit_view(request, pk: int):
    """
    Dashboard: Edit an existing Experience entry.
    """
    profile = Profile.objects.first()
    experience = get_object_or_404(Experience, pk=pk)

    if request.method == "POST":
        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            messages.success(request, "Experience updated successfully.")
            return redirect("main:dashboard")
        messages.error(request, "Please correct the errors below.")
    else:
        form = ExperienceForm(instance=experience)

    return render(
        request,
        "dashboard/experience_form.html",
        {"profile": profile, "form": form, "mode": "edit", "experience": experience},
    )


@login_required
def dashboard_experience_delete_view(request, pk: int):
    """
    Dashboard: Confirm + delete an Experience entry.
    """
    profile = Profile.objects.first()
    experience = get_object_or_404(Experience, pk=pk)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience deleted successfully.")
        return redirect("main:dashboard")

    return render(
        request,
        "dashboard/experience_delete.html",
        {"profile": profile, "experience": experience},
    )


@login_required
def dashboard_site_settings_edit_view(request):
    """
    Edit Site Settings from frontend.
    Creates a SiteSettings row automatically if none exists.
    """
    site_settings = SiteSettings.objects.first()
    if not site_settings:
        site_settings = SiteSettings.objects.create()

    # Ensure defaults are set if fields are empty
    if not site_settings.site_title:
        site_settings.site_title = SiteSettings._meta.get_field('site_title').default
    if not site_settings.primary_color:
        site_settings.primary_color = SiteSettings._meta.get_field('primary_color').default
    if not site_settings.secondary_color:
        site_settings.secondary_color = SiteSettings._meta.get_field('secondary_color').default
    if not site_settings.accent_color:
        site_settings.accent_color = SiteSettings._meta.get_field('accent_color').default
    if not site_settings.about_page_title:
        site_settings.about_page_title = SiteSettings._meta.get_field('about_page_title').default
    if not site_settings.about_page_subtitle:
        site_settings.about_page_subtitle = SiteSettings._meta.get_field('about_page_subtitle').default
    if not site_settings.experience_page_title:
        site_settings.experience_page_title = SiteSettings._meta.get_field('experience_page_title').default
    if not site_settings.projects_page_title:
        site_settings.projects_page_title = SiteSettings._meta.get_field('projects_page_title').default
    if not site_settings.contact_page_title:
        site_settings.contact_page_title = SiteSettings._meta.get_field('contact_page_title').default
    site_settings.save()

    if request.method == "POST":
        form = SiteSettingsForm(request.POST, instance=site_settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Site settings updated successfully.")
            return redirect("main:dashboard")
    else:
        form = SiteSettingsForm(instance=site_settings)

    return render(
        request,
        "dashboard/site_settings_edit.html",
        {"site_settings": site_settings, "form": form},
    )
