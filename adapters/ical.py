from five import grok
from zope.component import queryAdapter, getUtility
from zope.interface import implements
from zope.app.intid.interfaces import IIntIds
from icalendar import Calendar, Event, vText, vDatetime, vDate
from icalendar.interfaces import ICalendar, IEvent
from Products.SilvaNews.interfaces import (IAgendaItemVersion, IAgendaFilter,
    IAgendaViewer)
from Products.SilvaNews.datetimeutils import UTC, local_timezone
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class AgendaFactoryEvent(grok.Adapter):
    grok.context(IAgendaItemVersion)
    grok.implements(IEvent)
    grok.provides(IEvent)

    def __call__(self, viewer):
        return AgendaEvent(self.context, viewer)

class AgendaEvent(Event):

    def __init__(self, context, viewer=None):
        super(AgendaEvent, self).__init__()
        date_rep = context.get_calendar_date_representation()
        intid = getUtility(IIntIds)
        timezone = viewer and viewer.get_timezone() or context.timezone()
        start_dt = context.start_datetime().astimezone(timezone)
        end_dt = context.end_datetime().astimezone(timezone)
        start_date = date(start_dt.year, start_dt.month, start_dt.day)
        end_date = date(end_dt.year, end_dt.month, end_dt.day)
        if start_date == end_date:
            if start_date:
                self['DTSTART'] = vDatetime(start_dt)
            if end_date:
                self['DTEND'] = vDatetime(end_dt)
        else:
            self['DTSTART'] = vDate(start_date)
            self['DTEND'] = vDate(end_date + relativedelta(days=+1))

#        self['RRULE']

        self['UID'] = "%d@silvanews" % intid.register(context.object())
        if context.location:
            self['LOCATION'] = vText(context.location())
        self['SUMMARY'] = vText(context.get_title())
        if viewer is None:
            self['URL'] = context.object().absolute_url()
        else:
            self['URL'] = viewer.url_for(context)

class AgendaCalendar(Calendar, grok.Adapter):
    grok.context(IAgendaViewer)
    grok.implements(ICalendar)
    grok.provides(ICalendar)

    def __init__(self, context):
        super(AgendaCalendar, self).__init__()
        self.context = context
        self['PRODID'] = \
            vText('-//Infrae SilvaNews Calendaring//NONSGML Calendar//EN')
        self['VERSION'] = '2.0'
        self['X-WR-CALNAME'] = self.context.get_title()
        self['X-WR-TIMEZONE'] = self.context.get_timezone_name()
        now = datetime.now(UTC)
        for brain in self.context.get_items_by_date_range(
                now + relativedelta(years=-1), now + relativedelta(years=+1)):
            agenda_item_version = brain.getObject()
            event_factory = AgendaFactoryEvent(agenda_item_version)
            event = event_factory(self.context)
            if event is not None:
                self.add_component(event)


