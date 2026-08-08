"""
Pure unit tests for LiveDensityManager.
No Django setup needed — we mock redis entirely.
"""
from unittest.mock import patch, MagicMock, call
import sys
import os

# Minimal Django settings stub so redis_density.py can import settings
from unittest.mock import MagicMock
import types

# Create a fake django.conf.settings module
fake_settings = types.SimpleNamespace(
    REDIS_HOST='localhost',
    REDIS_PORT=6379,
    REDIS_DB=0,
    REDIS_PASSWORD='',
)

# Patch before importing the module under test
import django.conf
django_conf_settings_patcher = patch.object(django.conf, 'settings', fake_settings)
django_conf_settings_patcher.start()

from apps.gps.redis_density import LiveDensityManager


class TestLiveDensityManager:

    @patch('apps.gps.redis_density.redis.StrictRedis')
    def test_update_density_success(self, mock_redis_class):
        """update_density stores the user location via GEOADD and returns True."""
        mock_client = MagicMock()
        mock_redis_class.return_value = mock_client
        mock_client.ping.return_value = True

        manager = LiveDensityManager()
        result = manager.update_density(user_id=123, latitude=18.5204, longitude=73.8567)

        assert result is True
        mock_client.geoadd.assert_called_once_with(
            'gps:live_density', (73.8567, 18.5204, '123')
        )

    @patch('apps.gps.redis_density.redis.StrictRedis')
    def test_update_density_when_not_connected(self, mock_redis_class):
        """update_density returns False when Redis is unavailable (fail-safe)."""
        mock_client = MagicMock()
        mock_redis_class.return_value = mock_client
        mock_client.ping.side_effect = Exception("Connection refused")

        manager = LiveDensityManager()
        result = manager.update_density(user_id=99, latitude=18.0, longitude=73.0)

        assert result is False

    @patch('apps.gps.redis_density.redis.StrictRedis')
    def test_get_density_in_radius_returns_user_count(self, mock_redis_class):
        """get_density_in_radius returns the number of users in the given area."""
        mock_client = MagicMock()
        mock_redis_class.return_value = mock_client
        mock_client.ping.return_value = True
        mock_client.georadius.return_value = ['10', '11', '12']

        manager = LiveDensityManager()
        count = manager.get_density_in_radius(latitude=18.5204, longitude=73.8567, radius_meters=100)

        assert count == 3
        mock_client.georadius.assert_called_once_with(
            'gps:live_density', 73.8567, 18.5204, 100, unit='m'
        )

    @patch('apps.gps.redis_density.redis.StrictRedis')
    def test_get_density_in_radius_when_not_connected(self, mock_redis_class):
        """Returns 0 safely when Redis is down."""
        mock_client = MagicMock()
        mock_redis_class.return_value = mock_client
        mock_client.ping.side_effect = Exception("down")

        manager = LiveDensityManager()
        assert manager.get_density_in_radius(18.0, 73.0) == 0

    @patch('apps.gps.redis_density.redis.StrictRedis')
    def test_density_level_50_percent(self, mock_redis_class):
        """250 users in radius → level 50."""
        mock_client = MagicMock()
        mock_redis_class.return_value = mock_client
        mock_client.ping.return_value = True

        manager = LiveDensityManager()
        with patch.object(manager, 'get_density_in_radius', return_value=250):
            assert manager.get_density_level(18.52, 73.85) == 50

    @patch('apps.gps.redis_density.redis.StrictRedis')
    def test_density_level_capped_at_100(self, mock_redis_class):
        """Density level is always capped at 100 even for very large crowds."""
        mock_client = MagicMock()
        mock_redis_class.return_value = mock_client
        mock_client.ping.return_value = True

        manager = LiveDensityManager()
        with patch.object(manager, 'get_density_in_radius', return_value=99999):
            assert manager.get_density_level(18.52, 73.85) == 100

    @patch('apps.gps.redis_density.redis.StrictRedis')
    def test_density_level_zero_when_empty(self, mock_redis_class):
        """Empty area returns density level 0."""
        mock_client = MagicMock()
        mock_redis_class.return_value = mock_client
        mock_client.ping.return_value = True

        manager = LiveDensityManager()
        with patch.object(manager, 'get_density_in_radius', return_value=0):
            assert manager.get_density_level(18.52, 73.85) == 0
