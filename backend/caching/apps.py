"""
Caching application configuration.
"""

from django.apps import AppConfig


class CachingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'caching'
    verbose_name = 'Caching System'
    
    def ready(self):
        """
        Testing cache connectivity during app startup
        """
        try:
            from .core import default_cache_manager
            
            try:
                default_cache_manager.set('app_ready_test', True, 10)
                if default_cache_manager.get('app_ready_test'):
                    print("✓ Redis cache connectivity confirmed")
                default_cache_manager.delete('app_ready_test')
            except Exception as e:
                print(f"⚠ Redis cache connectivity issue: {e}")
        except ImportError:
            print("⚠ Caching system not available")
            pass
