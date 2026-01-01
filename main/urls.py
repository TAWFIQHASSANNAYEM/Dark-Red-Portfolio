from django.urls import path
from .views import (
    home_view,
    about_view,
    experience_view,
    projects_view,
    contact_view,
    dashboard_view, dashboard_profile_edit_view,
    dashboard_project_add_view, dashboard_project_edit_view, dashboard_project_delete_view,
    dashboard_education_add_view, dashboard_education_edit_view, dashboard_education_delete_view,
    dashboard_experience_add_view, dashboard_experience_edit_view, dashboard_experience_delete_view,
    dashboard_site_settings_edit_view,
)

app_name = "main"

urlpatterns = [
    # Home / landing page
    path("", home_view, name="home"),

    # About / profile details
    path("about/", about_view, name="about"),

    # Experience & leadership history
    path("experience/", experience_view, name="experience"),

    # Projects showcase
    path("projects/", projects_view, name="projects"),

    # Contact form
    path("contact/", contact_view, name="contact"),
    
        # Hidden dashboard (frontend CRUD)
    path("dashboard/", dashboard_view, name="dashboard"),
    path("dashboard/profile/", dashboard_profile_edit_view, name="dashboard_profile_edit"),

    path("dashboard/projects/add/", dashboard_project_add_view, name="dashboard_project_add"),
    path("dashboard/projects/<int:pk>/edit/", dashboard_project_edit_view, name="dashboard_project_edit"),
    path("dashboard/projects/<int:pk>/delete/", dashboard_project_delete_view, name="dashboard_project_delete"),
    
    path("dashboard/education/add/", dashboard_education_add_view, name="dashboard_education_add"),
    path("dashboard/education/<int:pk>/edit/", dashboard_education_edit_view, name="dashboard_education_edit"),
    path("dashboard/education/<int:pk>/delete/", dashboard_education_delete_view, name="dashboard_education_delete"),

    # Experience CRUD (Dashboard)
    path("dashboard/experience/add/", dashboard_experience_add_view, name="dashboard_experience_add"),
    path("dashboard/experience/<int:pk>/edit/", dashboard_experience_edit_view, name="dashboard_experience_edit"),
    path("dashboard/experience/<int:pk>/delete/", dashboard_experience_delete_view, name="dashboard_experience_delete"),

    # Site Settings
    path("dashboard/site-settings/", dashboard_site_settings_edit_view, name="dashboard_site_settings_edit"),

]



