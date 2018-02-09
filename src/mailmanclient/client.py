# Copyright (C) 2010-2017 The Free Software Foundation, Inc.
#
# This file is part of mailmanclient.
#
# mailmanclient is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, version 3 of the License.
#
# mailmanclient is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mailmanclient.  If not, see <http://www.gnu.org/licenses/>.

"""Client code."""

from __future__ import absolute_import, unicode_literals

import warnings
from operator import itemgetter

from mailmanclient.constants import (MISSING)
from mailmanclient.restobjects.address import Address
from mailmanclient.restobjects.ban import Bans, BannedAddress
from mailmanclient.restobjects.configuration import Configuration
from mailmanclient.restobjects.domain import Domain
from mailmanclient.restobjects.mailinglist import MailingList
from mailmanclient.restobjects.member import Member
from mailmanclient.restobjects.preferences import Preferences
from mailmanclient.restobjects.queue import Queue
from mailmanclient.restobjects.user import User
from mailmanclient.restbase.connection import Connection, get_data_str
from mailmanclient.restbase.page import Page

__metaclass__ = type
__all__ = [
    'Client'
]


#
# --- The following classes are part of the API
#

class Client:
    """Access the Mailman REST API root."""

    def __init__(self, baseurl, name=None, password=None):
        """Initialize client access to the REST API.

        :param baseurl: The base url to access the Mailman 3 REST API.
        :param name: The Basic Auth user name.  If given, the `password` must
            also be given.
        :param password: The Basic Auth password.  If given the `name` must
            also be given.
        """
        self._connection = Connection(baseurl, name, password)

    def __repr__(self):
        return '<Client ({0.name}:{0.password}) {0.baseurl}>'.format(
            self._connection)

    @property
    def system(self):
        return self._connection.call('system/versions')[1]

    @property
    def preferences(self):
        return Preferences(self._connection, 'system/preferences')

    @property
    def configuration(self):
        response, content = self._connection.call('system/configuration')
        return {section: Configuration(
            self._connection, section) for section in content['sections']}

    @property
    def pipelines(self):
        response, content = self._connection.call('system/pipelines')
        return content

    @property
    def chains(self):
        response, content = self._connection.call('system/chains')
        return content

    @property
    def queues(self):
        response, content = self._connection.call('queues')
        queues = {}
        for entry in content['entries']:
            queues[entry['name']] = Queue(
                self._connection, entry['self_link'], entry)
        return queues

    @property
    def lists(self):
        return self.get_lists()

    def get_lists(self, advertised=None, owner=None):
        url = 'lists'
        data ={}
        if advertised:
            data['advertised'] = 'true'
        if owner:
            data['owner'] = owner
        response, content = self._connection.call(url, data)
        if 'entries' not in content:
            return []
        return [MailingList(self._connection, entry['self_link'], entry)
                for entry in content['entries']]

    def get_list_page(self, count=50, page=1, advertised=None, owner=None):
        url = 'lists'
        data = {}
        if advertised:
            data['advertised'] = 'true'
        if owner:
            data['owner'] = owner
        if data:
            url += '?' + get_data_str(data)
        return Page(self._connection, url, MailingList, count, page)

    @property
    def domains(self):
        response, content = self._connection.call('domains')
        if 'entries' not in content:
            return []
        return [Domain(self._connection, entry['self_link'])
                for entry in sorted(content['entries'],
                                    key=itemgetter('mail_host'))]

    @property
    def members(self):
        response, content = self._connection.call('members')
        if 'entries' not in content:
            return []
        return [Member(self._connection, entry['self_link'], entry)
                for entry in content['entries']]

    def get_member(self, fqdn_listname, subscriber_address):
        return self.get_list(fqdn_listname).get_member(subscriber_address)

    def get_member_page(self, count=50, page=1):
        return Page(self._connection, 'members', Member, count, page)

    @property
    def users(self):
        response, content = self._connection.call('users')
        if 'entries' not in content:
            return []
        return [User(self._connection, entry['self_link'], entry)
                for entry in sorted(content['entries'],
                                    key=itemgetter('self_link'))]

    def get_user_page(self, count=50, page=1):
        return Page(self._connection, 'users', User, count, page)

    def create_domain(self, mail_host, base_url=MISSING,
                      description=None, owner=None):
        if base_url is not MISSING:
            warnings.warn(
                'The `base_url` parameter in the `create_domain()` method is '
                'deprecated. It is not used any more and will be removed in '
                'the future.', DeprecationWarning, stacklevel=2)
        data = dict(mail_host=mail_host)
        if description is not None:
            data['description'] = description
        if owner is not None:
            data['owner'] = owner
        response, content = self._connection.call('domains', data)
        return Domain(self._connection, response['location'])

    def delete_domain(self, mail_host):
        response, content = self._connection.call(
            'domains/{0}'.format(mail_host), None, 'DELETE')

    def get_domain(self, mail_host, web_host=MISSING):
        """Get domain by its mail_host or its web_host."""
        if web_host is not MISSING:
            warnings.warn(
                'The `web_host` parameter in the `get_domain()` method is '
                'deprecated. It is not used any more and will be removed in '
                'the future.', DeprecationWarning, stacklevel=2)
        response, content = self._connection.call(
            'domains/{0}'.format(mail_host))
        return Domain(self._connection, content['self_link'])

    def create_user(self, email, password, display_name=''):
        response, content = self._connection.call(
            'users', dict(email=email,
                          password=password,
                          display_name=display_name))
        return User(self._connection, response['location'])

    def get_user(self, address):
        response, content = self._connection.call(
            'users/{0}'.format(address))
        return User(self._connection, content['self_link'], content)

    def get_address(self, address):
        response, content = self._connection.call(
            'addresses/{0}'.format(address))
        return Address(self._connection, content['self_link'], content)

    def get_list(self, fqdn_listname):
        response, content = self._connection.call(
            'lists/{0}'.format(fqdn_listname))
        return MailingList(self._connection, content['self_link'], content)

    def delete_list(self, fqdn_listname):
        response, content = self._connection.call(
            'lists/{0}'.format(fqdn_listname), None, 'DELETE')

    @property
    def bans(self):
        return Bans(self._connection, 'bans', mlist=None)

    def get_bans_page(self, count=50, page=1):
        return Page(self._connection, 'bans', BannedAddress, count, page)
