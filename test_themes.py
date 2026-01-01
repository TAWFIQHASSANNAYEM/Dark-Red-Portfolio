#!/usr/bin/env python
"""
Test script for theme system functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dark_Red_Portfolio.settings')
django.setup()

from main.models import SiteSettings

def test_theme_colors():
    """Test that all themes return valid color schemes"""
    print("🧪 Testing Theme System Implementation")
    print("=" * 50)

    # Test all theme choices
    themes = [choice[0] for choice in SiteSettings.THEME_CHOICES]
    expected_keys = ['primary', 'secondary', 'accent', 'bg0', 'bg1', 'card', 'text', 'muted', 'border']

    print(f"📋 Testing {len(themes)} themes: {', '.join(themes)}")
    print()

    all_passed = True

    for theme in themes:
        print(f"🎨 Testing theme: {theme}")

        # Create a SiteSettings instance with this theme
        settings = SiteSettings(theme=theme)

        # Get theme colors
        colors = settings.get_theme_colors()

        # Check if all expected keys are present
        missing_keys = [key for key in expected_keys if key not in colors]
        if missing_keys:
            print(f"  ❌ Missing keys: {missing_keys}")
            all_passed = False
        else:
            print("  ✅ All required color keys present")

        # Check if colors are valid CSS color values (basic validation)
        invalid_colors = []
        for key, value in colors.items():
            if not isinstance(value, str) or not value.strip():
                invalid_colors.append(f"{key}: {value}")
            # Allow hex codes, rgba(), and linear-gradient() values
            elif not (value.startswith('#') or value.startswith('rgba(') or value.startswith('linear-gradient(')):
                invalid_colors.append(f"{key}: {value}")

        if invalid_colors:
            print(f"  ❌ Invalid color formats: {invalid_colors}")
            all_passed = False
        else:
            print("  ✅ All colors are valid CSS color values")

        # Show sample colors
        print(f"  🎨 Primary: {colors['primary']}, Secondary: {colors['secondary']}, BG: {colors['bg0']}")
        print()

    # Test default theme fallback
    print("🔄 Testing default theme fallback")
    settings = SiteSettings(theme='nonexistent_theme')
    colors = settings.get_theme_colors()
    if colors == settings.get_theme_colors.__defaults__[0]['dark_red']:
        print("  ✅ Default theme fallback works correctly")
    else:
        print("  ❌ Default theme fallback failed")
        all_passed = False
    print()

    # Test database operations
    print("💾 Testing database operations")
    try:
        # Create or get existing settings
        settings, created = SiteSettings.objects.get_or_create(
            defaults={'site_title': 'Test Site'}
        )

        # Test theme saving and retrieval
        original_theme = settings.theme
        settings.theme = 'dark_blue'
        settings.save()

        # Refresh from database
        settings.refresh_from_db()
        if settings.theme == 'dark_blue':
            print("  ✅ Theme persistence works correctly")
        else:
            print("  ❌ Theme persistence failed")
            all_passed = False

        # Restore original theme
        settings.theme = original_theme
        settings.save()

    except Exception as e:
        print(f"  ❌ Database operation failed: {e}")
        all_passed = False

    print()
    print("=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Theme system is working correctly.")
    else:
        print("❌ SOME TESTS FAILED! Please review the implementation.")

    return all_passed

def test_template_integration():
    """Test that templates can access theme colors"""
    print("\n🔧 Testing Template Integration")
    print("=" * 30)

    try:
        from django.template import Template, Context

        # Test template rendering with theme colors
        template_content = """
        {% load static %}
        <style>
            :root{
                --bg0: {{ site_settings.get_theme_colors.bg0 }};
                --primary: {{ site_settings.get_theme_colors.primary }};
            }
        </style>
        """

        template = Template(template_content)
        settings = SiteSettings(theme='cyberpunk')
        context = Context({'site_settings': settings})
        rendered = template.render(context)

        # Check if theme colors are rendered
        if '--bg0: #0a0a0a' in rendered and '--primary: #00ff88' in rendered:
            print("✅ Template integration works correctly")
            return True
        else:
            print("❌ Template integration failed")
            print("Rendered output:", rendered)
            return False

    except Exception as e:
        print(f"❌ Template integration test failed: {e}")
        return False

if __name__ == '__main__':
    success1 = test_theme_colors()
    success2 = test_template_integration()

    if success1 and success2:
        print("\n🎯 Theme system implementation is COMPLETE and WORKING!")
        sys.exit(0)
    else:
        print("\n⚠️  Theme system has ISSUES that need to be fixed!")
        sys.exit(1)
