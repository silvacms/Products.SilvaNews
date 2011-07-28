
from silva.core.upgrade.upgrader.upgrade_300 import VERSION_A1
from silva.core.upgrade.upgrade import BaseUpgrader
from Products.SilvaDocument.upgrader.upgrade_300 import DocumentUpgrader


class CatalogUpgrader(BaseUpgrader):

    def validate(self, root):
        return bool(root.service_catalog)

    def upgrade(self, root):
        catalog = root.service_catalog._catalog

        columns = ['get_end_datetime','get_start_datetime',
            'get_location','get_title', 'display_datetime',
            'get_intro', 'sort_index']

        indexes = ['idx_end_datetime', 'idx_display_datetime',
            'idx_parent_path', 'idx_start_datetime', 'idx_target_audiences',
            'idx_timestamp_ranges', 'idx_subjects']

        existing_columns = catalog.schema
        existing_indexes = catalog.indexes

        for column_name in columns:
            if column_name in existing_columns:
                catalog.delColumn(column_name)

        for field_name in indexes:
            if field_name in existing_indexes:
                catalog.delIndex(field_name)

        return root


class RootUpgrader(BaseUpgrader):

    def upgrade(self, root):
        extensions = root.service_extensions
        # If Silva News is installed, we need to refresh it, and
        # install silva.app.news for the migration.
        if extensions.is_installed('SilvaNews'):
            extensions.refresh('SilvaNews')
            if not extensions.is_installed('silva.app.news'):
                extensions.install('silva.app.news')
        return root


class NewsItemUpgrader(DocumentUpgrader):

    def create_document(self, parent, identifier, title):
        factory = parent.manage_addProduct['silva.app.news']
        factory.manage_addNewsItem(identifier, title)


class AgendaItemUpgrader(DocumentUpgrader):

    def create_document(self, parent, identifier, title):
        factory = parent.manage_addProduct['silva.app.news']
        factory.manage_addAgendaItem(identifier, title)


upgrade_catalog = CatalogUpgrader(VERSION_A1, "Silva Root")
upgrade_root = RootUpgrader(VERSION_A1, "Silva Root")
upgrade_newsitem = NewsItemUpgrader(VERSION_A1, "Obsolete Article")
upgrade_agendaitem = AgendaItemUpgrader(VERSION_A1, "Obsolete Agenda Item")