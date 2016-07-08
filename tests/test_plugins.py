"""Tests for plugin system."""
import unittest2 as unittest


class TestPlugins(unittest.TestCase):
    """Unit test for plugin code."""

    def test_plugin_locator_with_manager(self):
        """Test cases for plugin locator.

        Uses custom PluginLocator inside PluginManager.
        """
        from drop.plugins import DropPluginLocator
        from yapsy.PluginManager import PluginManager

        pm = PluginManager(plugin_locator=DropPluginLocator())

        # TODO: Create some dummy plugins to be found

        pm.collectPlugins()
        pm.getAllPlugins()
